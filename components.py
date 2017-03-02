from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import  Base, Component, Item, User

engine = create_engine('sqlite:///pccomponents.db')
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

User1 = User(name="Antonio", email="antonio@gmail.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()


motherboard = Component(user_id=1, name="motherboard", image="https://image.flaticon.com/icons/svg/141/141009.svg")
session.add(motherboard)
session.commit()

ram = Component(user_id=1, name="ram", image="https://image.flaticon.com/icons/svg/141/141009.svg")
session.add(ram)
session.commit()


kingston = Item(user_id=1, name="kingston", description="New kingston Ram 64GB the future", price="46.58", component=ram)
session.add(kingston)
session.commit()

msi = Item(user_id=1, name="msi", description="MSI 970 AM3+", price="95.00", component=motherboard)
session.add(msi)
session.commit()

kingston2 = Item(user_id=1, name="kingston2", description="New kingston Ram 128GB the future", price="85.28", component=ram)
session.add(kingston2)
session.commit()

print "added items!"
