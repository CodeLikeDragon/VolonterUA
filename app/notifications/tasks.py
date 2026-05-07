from json import dumps
from uuid import UUID
from datetime import datetime, timezone

from app.common.enums import NotificationChannel
from app.core.celery_app import celery_app
from app.core.database_sync import SessionLocal
from app.core.redis import redis_client
from app.notifications.models import Notification


# @celery_app.task                                           # test code
# def send_notification(user_id: UUID, message: str):
#     print(f"[NOTIFICATION] user={user_id}: {message}")


@celery_app.task
def create_notification(
    user_id: str,
    title: str,
    body: str | None,
    meta: dict | None,
    channel: str | None = None
):

    db = SessionLocal()

    try:

        notification = Notification(
            user_id=UUID(user_id),
            title=title,
            body=body,
            channel=channel or NotificationChannel.IN_APP,
            sent_at=datetime.now(timezone.utc),
            meta=meta
        )

        db.add(notification)
        db.commit()

        redis_client.publish(
            f"user:{user_id}",
            dumps({
                "title": title,
                "body": body,
                "meta": meta
            })
        )

    finally:
        db.close()
