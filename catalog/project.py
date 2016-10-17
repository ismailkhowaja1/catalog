from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, StoreItem, User
from flask import session as login_session
import random
import string
import datetime
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///catalogmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# JSON APIs to view Catalog Information
@app.route('/catalog/JSON')
def catalogMenuJSON():
    items = session.query(StoreItem).all()
    its = jsonify(Item= [i.serialize for i in items])
    return its

@app.route('/catalog/catalog_item/<int:item_id>/JSON')
def itemJSON(item_id):
    item = session.query(StoreItem).filter_by(item_id=item_id).one()
    return jsonify(item=[item.serialize])


@app.route('/catalog/<int:category_id>/JSON')
def catItemsJSON(category_id):
    cat_items = session.query(StoreItem).filter_by(cat_id=category_id).all()
    return jsonify(catItems=[i.serialize for i in cat_items])

"""User helper methods to create and get user data"""
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
        'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.user_id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.user_id
    except:
        return None



#this is helper method for login which will crete state id
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    return render_template('login.html', STATE=state)


# this is used to connect a facebook account to login and add items
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]


    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


#this will disconnect from your app
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


# this route is main page when you first type localhost:5000
@app.route('/')
@app.route('/catalog')
def showCategories():
    categories = session.query(Category).order_by(asc(Category.name)).all()
    items = session.query(StoreItem).limit(10)
    if 'username' not in login_session:
        return render_template('catalog.html', categories = categories, items=items)
    else:
        return render_template('loggedincatalog.html', categories = categories, items = items)


# this route will take you independent category items
@app.route('/catalog/<string:category_id>/items')
def showCategoryItems(category_id):
    category = session.query(Category).filter_by(category_id=category_id).one()
    items = session.query(StoreItem).filter_by(cat_id = category.category_id).all()
    itemCount = session.query(StoreItem).filter_by(cat_id=category.category_id).count()
    return render_template('category_items.html', items=items, count=itemCount, category=category)


#this route will lead to individual item and its description
@app.route('/catalog/<int:category_id>/<int:item_id>')
def showDescription(category_id, item_id):
    category = session.query(Category).filter_by(category_id=category_id).one()
    item = session.query(StoreItem).filter_by(item_id=item_id).one()
    if 'username' not in login_session:
        return render_template('public_item_des.html', category=category, item=item)
    else:
        return render_template('item_des.html', category=category, item=item)


#this route will lead to edit item page
@app.route('/catalog/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(item_id):
    editedItem = session.query(StoreItem).filter_by(item_id=item_id).one()
    categoryId = session.query(StoreItem.cat_id).filter_by(item_id=item_id).one()[0]
    category = session.query(Category).filter_by(category_id=categoryId).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedItem.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this item. %s %s');}</script><body onload='myFunction()''>" % (login_session['user_id'], editedItem.user_id)
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']

        session.add(editedItem)
        session.commit()
        return redirect(url_for('showDescription', category_id=category.category_id, item_id=editedItem.item_id))
    else:
        return render_template('item_edit.html', item=editedItem, category=category)


#this route will
@app.route('/catalog/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItem(item_id):
    deleteItem = session.query(StoreItem).filter_by(item_id=item_id).one()
    categoryId = session.query(StoreItem.cat_id).filter_by(item_id=item_id).one()[0]
    category = session.query(Category).filter_by(category_id=categoryId).one()
    if 'username' not in login_session:
        return redirect('/login')
    if deleteItem.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this Item.');}</script><body onload='myFunction()''>"

    if request.method == 'POST':
        session.delete(deleteItem)
        session.commit()
        return redirect(url_for('showCategoryItems', category_id=category.category_id))
    else:
        return render_template('item_delete.html', item=deleteItem)


@app.route('/catalog/add', methods=['GET', 'POST'])
def addItem():
    categories = session.query(Category).all()
    if 'username' not in login_session:
        return redirect('/login')
    else:
        if request.method == 'POST':
            if request.form['name'] and request.form['description'] and request.form['category']:
                category = session.query(Category).filter_by(name= request.form['category']).one()
                newItem = StoreItem(user_id=login_session['user_id'] , name=request.form['name'], description=request.form['description'], cat_id=category.category_id)
                session.add(newItem)
                session.commit()
                return redirect(url_for('showCategories'))
        else:
            return render_template('add_item.html', categories=categories)

# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategories'))



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)