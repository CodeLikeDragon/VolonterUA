from uuid import UUID

from app.chats.messages.models import Message


def serialize_message(message: Message) -> dict:

    return {
        "id": str(message.id),
        "sender_id": str(message.sender_id),
        "text": message.text,
        "file_url": message.file_url,
        "file_type": (
            message.file_type.value
            if message.file_type
            else None
        ),
        "created_at": message.created_at.isoformat(),
        "status": message.status.value
    }


def serialize_messages(messages: list[Message]) -> list[dict]:
    return [
        serialize_message(message)
        for message in messages
    ]


def serialize_message_delivered(message_id: UUID):
    return {
        "message_id": str(message_id)
    }
