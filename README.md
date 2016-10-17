# catalog
you have to download vm virtual machine, git bash, python

install all above

https://udacity.atlassian.net/wiki/display/BENDH/Vagrant+VM+Installation you should also have facebook account to log in

you have to clone this project and in git bash you have to redirect to directory vagrant then type vagrant up in gitbash

after succesfully doing that type those commands

cd /vagrant

cd /catalog

first you will need to create database so after cd /catalog type python lotsofcategories.py

then run the actual project so you will see the categories python project.py

then you should be able to see website with address: localhost:5000

for JSON for all items you have to type in browser: localhost:5000/catalog/JSON for JSON for only category items: localhost:5000/catalog/1/JSON (1 is category id) for JSON for arbitary item: localhost:5000/catalog/catalog_item/1/JSON (1 is item id)
