from typing import Dict, Optional

_tokens: Dict[int, str] = {}


def set_token(telegram_id: int, token: str) -> None:
    _tokens[telegram_id] = token


def get_token(telegram_id: int) -> Optional[str]:
    return _tokens.get(telegram_id)
