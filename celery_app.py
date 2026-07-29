from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
	"subscriptions_tasks", # name for the celery app, will be mainly used internally
	broker="redis://redis:6379/0", # broker here means where celery will send/reads tasks from, which in this case is redis
	backend="redis://redis:6379/0", # backend is where celery will be storing the results for the tasks at (not entirly needed here but standard practice to include)
	# the /0 signals database 0 as redis organizes data into databases 0-15
	include=["tasks"],
	)

celery_app.conf.beat_schedule = {
	"check_upcoming_subs_daily": {
		"tasks": "tasks.check_upcoming_subs",
		"schedule": crontab(hour=8, minute=0)
	},

}