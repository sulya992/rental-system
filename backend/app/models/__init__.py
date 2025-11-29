from sqlalchemy.orm import declarative_base

Base = declarative_base()

from .user import User  # noqa: E402,F401
from .listing import Listing  # noqa: E402,F401
from .preferences import TenantPreference  # noqa: E402,F401
from .feed_action import FeedAction  # noqa: E402,F401
from .favorite import Favorite  # noqa: E402,F401
from .lead import Lead  # noqa: E402,F401

__all__ = [
    "Base",
    "User",
    "Listing",
    "TenantPreference",
    "FeedAction",
    "Favorite",
    "Lead",
]
