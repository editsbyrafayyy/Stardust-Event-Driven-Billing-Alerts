from celery import Celery
from celery.schedules import crontab
from config import settings

celery_app = Celery(
	"subscriptions_tasks", # name for the celery app, will be mainly used internally
	broker=settings.redis_url, # broker where celery will send/reads tasks from
	backend=settings.redis_url, # backend where celery stores results
	include=["tasks"],
	)

celery_app.conf.beat_schedule = {
	"check_upcoming_subs_daily": {
		"task": "tasks.check_upcoming_subs",
		"schedule": crontab(hour=8, minute=0)
	},

}