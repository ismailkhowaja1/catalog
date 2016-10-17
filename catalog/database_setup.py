from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):
	__tablename__ = "category"

	category_id = Column(Integer, primary_key=True)
	name = Column(String(100))


	@property
	def serialize(self):
	    """Return object data in easily serializeable format"""
	    return {
            'name': self.name,
            'id': self.category_id,
            }



class StoreItem(Base):
	__tablename__ = "storeitem"

	item_id = Column(Integer, primary_key=True)
	name = Column(String)
	description = Column(String)
	user_id = Column(Integer, ForeignKey('user.user_id'))
	user = relationship(User)
	cat_id = Column(Integer, ForeignKey('category.category_id'))
	category = relationship(Category)

	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
            'name': self.name,
            'description': self.description,
            'id': self.item_id,
            'cat_id': self.cat_id,
            'cat_name': self.category.name
        }



engine = create_engine('sqlite:///catalogmenu.db')


Base.metadata.create_all(engine)