from app.notifications.notifications.models import Notification


async def _create_and_commit(self, notification: Notification):
    try:
        await self.repo.create(notification)
        await self.session.commit()
    except Exception:
        await self.session.rollback()
        raise

    return notification
