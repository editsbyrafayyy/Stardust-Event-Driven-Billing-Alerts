from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
# ORM stands for object relational mapping 

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit= False, autoflush= True, bind= engine) 
'''
Eventhough autocommit is set to False by default and autoflush to True by default. Autoflush here means that whenever a query is to be run
SQLAlchemy syncs/gets the changes made, so the data that is interacted with is upto date. (the idea is similar to how google doc would
save all the changes made before the user copies a link to share it with someone)
While, autocommit means that I get to finalize the transaction instead of it being finalized after every action (similar to pushing on git)  
 '''

class Base(DeclarativeBase): # helps mapping python objects to SQL tables (this is inherited by all the classes) and it helps with tracking schema
	pass