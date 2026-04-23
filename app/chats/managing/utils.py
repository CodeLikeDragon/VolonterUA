from app.common.enums import MessageType


def map_file_type(mime: str) -> MessageType:
    if mime.startswith("image/"):
        return MessageType.IMAGE
    if mime.startswith("video/"):
        return MessageType.VIDEO
    return MessageType.FILE
