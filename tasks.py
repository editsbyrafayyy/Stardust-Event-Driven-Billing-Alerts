from celery_app import celery_app
from datetime import date, timedelta
from db import SessionLocal
from models import Subscription, Alert

@celery_app.task # this decorator enables the python function to run async in the background. It provides the function with extra methods such as delay, apply_asynca
def check_upcoming_subs():
	db = SessionLocal() # we create a session specifically just for this task

	try:
		# the query filter has 2 components, first the renewal date should be of today/future AND it should be of all subs within 3 days from today.
		# this ensures that only subs that are due within 3 days max including today are displayed and not all the subs up for renewal in the future.
		upcoming = db.query(Subscription).filter(Subscription.renewal_date >= date.today(), Subscription.renewal_date <= date.today() + timedelta(days=3)).all()
		# for each sub show its name and renewal date that was found by the query
		for sub in upcoming:
			# we are checking to see if 1. the sub id's match for the sub and alert (both from the same service) 2. Their renewal date match, so new entries
			# are not made for already existing alerts (an alert that has 3 days left will otherwise create 3 new entries for each day it will run which we don't want)
			result = db.query(Alert).filter(Alert.sub_id == sub.id, Alert.renewal_date == sub.renewal_date).first()
			if not result:
				print(f"Subscription: {sub.name} is due on {sub.renewal_date}")
				# create a Alert type object with all the needed attributes (that match the shape properly)
				new_alert = Alert(sub_id = sub.id, renewal_date = sub.renewal_date, created_at = date.today())
				db.add(new_alert) # add that to the db
			else:
				continue # if it already exists then no need to add again

		db.commit()
	finally:
		# this runs unconditionally
		db.close()