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


motherboard = Component(user_id=1, name="Motherboard", image="static/images/motherboard.svg")
session.add(motherboard)
session.commit()

memory = Component(user_id=1, name="Memory", image="static/images/ram_memory.svg")
session.add(memory)
session.commit()

power_supply = Component(user_id=1, name="Power Supply", image="static/images/power_supply.svg")
session.add(power_supply)
session.commit()

processor = Component(user_id=1, name="Processor", image="static/images/processor.svg")
session.add(processor)
session.commit()

hard_drive = Component(user_id=1, name="Hard Drive", image="static/images/hard_drive.svg")
session.add(hard_drive)
session.commit()

graphic_card = Component(user_id=1, name="Graphic Card", image="static/images/graphic_card.svg")
session.add(graphic_card)
session.commit()

print "added items!"
