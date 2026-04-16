from enum import StrEnum
from sqlalchemy import Enum as SAEnum

class Gender(StrEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"
    UNSPECIFIED = "UNSPECIFIED"

class RequestStatus(StrEnum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    FULFILLED = "FULFILLED"
    CANCELED = "CANCELED"

class NotificationChannel(StrEnum):
    IN_APP = "IN_APP"
    EMAIL = "EMAIL"
    SMS = "SMS"
    TELEGRAM = "TELEGRAM"

class ConsentType(StrEnum):
    TERMS = "TERMS"
    PRIVACY = "PRIVACY"
    EMAIL_NOTIFICATIONS = "EMAIL_NOTIFICATIONS"
    SMS_NOTIFICATIONS = "SMS_NOTIFICATIONS"
    DATA_PROCESSING = "DATA_PROCESSING"

class ChatStatus(StrEnum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    CANCELED = "CANCELED"

class ChatParticipantRole(StrEnum):
    CREATOR = "CREATOR"
    MEMBER = "MEMBER"


# Хелпер: у SQLite немає нативних ENUM, тому ставимо native_enum=False і зберігаємо як TEXT
def sa_enum(enum_cls):
    return SAEnum(enum_cls, name=f"{enum_cls.__name__.lower()}", native_enum=False, validate_strings=True)
