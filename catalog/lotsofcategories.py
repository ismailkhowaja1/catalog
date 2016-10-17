from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, User, StoreItem

engine = create_engine('sqlite:///catalogmenu.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
category1 = Category(category_id=1, name="Soccer")
session.add(category1)
session.commit()

category2 = Category(category_id=2, name="BasketBall")
session.add(category2)
session.commit()

category3 = Category(category_id=3, name="BaseBall")
session.add(category3)
session.commit()

category4 = Category(category_id=4, name="Frisbee")
session.add(category4)
session.commit()

category5 = Category(category_id=5, name="SnowBoarding")
session.add(category5)
session.commit()

category6 = Category(category_id=6, name="Rock Climbing")
session.add(category6)
session.commit()


print "catetories added"