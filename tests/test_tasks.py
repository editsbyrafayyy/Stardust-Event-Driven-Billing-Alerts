import pytest
from unittest.mock import patch
from datetime import date, timedelta
from models import Subscription, Alert
from conftest import TestingSessionLocal
import tasks

def test_check_upcoming_subs_creates_and_deduplicates_alert(test_user):
	db = TestingSessionLocal()
	try:
		# Create a subscription renewing in 2 days (within the 3-day alert window)
		sub = Subscription(
			name="Claude Pro",
			cost=20.00,
			billing_cycle="monthly",
			description="AI assistant",
			renewal_date=date.today() + timedelta(days=2),
			owner_id=test_user.id
		)
		db.add(sub)
		db.commit()
		db.refresh(sub)

		# Patch SessionLocal and redis_client to isolate the test from production Redis
		with patch("tasks.SessionLocal", return_value=TestingSessionLocal()):
			with patch("tasks.redis_client.publish") as mock_publish:
				# 1. First run: should create 1 Alert and publish 1 message
				tasks.check_upcoming_subs()
				
				assert mock_publish.called
				alerts = db.query(Alert).filter(Alert.sub_id == sub.id).all()
				assert len(alerts) == 1
				assert alerts[0].renewal_date == sub.renewal_date

				mock_publish.reset_mock()

				# 2. Second run: duplicate check must kick in and NOT create a second alert
				tasks.check_upcoming_subs()
				assert not mock_publish.called
				alerts_after = db.query(Alert).filter(Alert.sub_id == sub.id).all()
				assert len(alerts_after) == 1
	finally:
		db.close()
