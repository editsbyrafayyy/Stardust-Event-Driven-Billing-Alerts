from celery_app import celery_app
from datetime import date, timedelta
from db import SessionLocal
from models import Subscription

@celery_app.task # this decorator enables the python function to run async in the background. It provides the function with extra methods such as delay, apply_asynca
def check_upcoming_subs():
	db = SessionLocal() # we create a session specifically just for this task

	try:
		# the query filter has 2 components, first the renewal date should be of today/future AND it should be of all subs within 3 days from today.
		# this ensures that only subs that are due within 3 days max including today are displayed and not all the subs up for renewal in the future.
		upcoming = db.query(Subscription).filter(Subscription.renewal_date >= date.today(), Subscription.renewal_date <= date.today() + timedelta(days=3)).all()
		# for each sub show its name and renewal date that was found by the query
		for sub in upcoming:
			print(f"Subscription: {sub.name} is due on {sub.renewal_date}")
	finally:
		# this runs unconditionally
		db.close()