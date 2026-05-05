from uuid import UUID
from datetime import datetime

from app.core.celery_app import celery_app
from app.core.database_sync import SessionLocal
from app.notifications.models import Notification


# @celery_app.task                                           # test code
# def send_notification(user_id: UUID, message: str):
#     print(f"[NOTIFICATION] user={user_id}: {message}")


@celery_app.task
def create_notification(user_id: UUID, message: str):
    db = SessionLocal()

    try:
        notification = Notification(
            user_id=user_id,
            title="Notification created",
            body=message,
            sent_at=datetime.utcnow()
        )

        db.add(notification)
        db.commit()

    finally:
        db.close()
