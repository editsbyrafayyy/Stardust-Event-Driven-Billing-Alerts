from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import settings
# ORM stands for object relational mapping, it serves as a bridge between OOP and RDBMS, without it raw sql strings would be needed inside python code, manually
# execution, and parsing logic to make it all work. ORM automates all this by being able to perform mapping and SQL generation while working only with python methods/objects

engine = create_engine(settings.database_url) # engine refers to the pool of physical connections with the db, we connect it with our DB with the DB_URL that we pass
# engine is a connection pool which keeps persistent TCP connections and they are handed out as needed
SessionLocal = sessionmaker(autocommit= False, autoflush= True, bind= engine) 
# Session Local creates sessions on demand (used in get_db)
'''
Eventhough autocommit is set to False by default and autoflush to True by default. Autoflush here means that whenever a query is to be run
SQLAlchemy syncs/gets the changes made, so the data that is interacted with is upto date. (the idea is similar to how google doc would
save all the changes made before the user copies a link to share it with someone)
While, autocommit means that I get to finalize the transaction instead of it being finalized after every action (similar to pushing on git)  
 '''

class Base(DeclarativeBase): # helps mapping python objects to SQL tables (this is inherited by all the classes) and it helps with tracking schema
	pass

def get_db(): # defines a generator type of object 
	db = SessionLocal() # this creates a fresh session with the db (used to run queries)
	try: # keeps an eye out of errors and even if everything fails, it still will go to finally
		yield db # hands over the session over to FastAPI and pauses execution (waits until endpoint sends a reponse)
	finally: # any code inside the finally clause will always run regardless of if there are any errors
		db.close() # closes session and returns connection back to db pool