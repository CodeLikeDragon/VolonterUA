# app/models_registry.py
# Імпортує усі модулі з моделями, щоб вони зареєстрували свої таблиці в Base.metadata
from app.users.users import models as _users_models    # noqa: F401
from app.users.credentials import models as _credentials_models    # noqa: F401
from app.users.email_verifications import models as _email_verifications_models    # noqa: F401
from app.users.oauth_accounts import models as _OAuth_accounts_models    # noqa: F401
from app.users.password_resets import models as _password_resets_models    # noqa: F401
from app.users.refresh_tokens import models as _refresh_tokens_models    # noqa: F401

from app.requests.requests import models as _requests_models  # noqa: F401
from app.requests.request_item_assignment import models as _request_item_assignment_models # noqa: F401
from app.requests.request_items import models as _request_items_models  # noqa: F401
from app.requests.request_offers import models as _request_offers_models  # noqa: F401
from app.requests.request_images import models as _request_images_models  # noqa: F401

from app.geo.cities import models as _cities_models  # noqa: F401
from app.geo.countries import models as _countries_models  # noqa: F401

from app.chats.chats import models as _chats_models  # noqa: F401
from app.chats.messages import models as _messages_models  # noqa: F401
from app.chats.chat_participants import models as _chat_participants_models  # noqa: F401

from app.notifications import models as _notif_models  # noqa: F401

from app.consents import models as _consents_models    # noqa: F401

from app.audit import models as _audit_models    # noqa: F401

from app.reviews import models as _reviews_models
