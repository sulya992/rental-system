from typing import Any, Dict, List, Optional

import httpx


class BackendClient:
    def __init__(self, base_url: str):
        self._client = httpx.AsyncClient(base_url=base_url, timeout=10.0)

    async def close(self) -> None:
        await self._client.aclose()

    # --- Auth / Telegram ---

    async def login_or_register_telegram(
        self,
        telegram_id: int,
        phone: str,
        name: Optional[str] = None,
        role: str = "tenant",
    ) -> str:
        payload = {
            "telegram_id": str(telegram_id),
            "phone": phone,
            "name": name or "",
            "role": role,
        }
        resp = await self._client.post("/auth/telegram/login-or-register", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["access_token"]

    # --- Feed ---

    async def get_next_listing(self, token: str) -> Optional[Dict[str, Any]]:
        resp = await self._client.get(
            "/feed/next",
            headers={"Authorization": f"Bearer {token}"},
        )
        resp.raise_for_status()
        data = resp.json()
        return data  # либо dict, либо None

    async def send_feed_action(
        self,
        token: str,
        listing_id: int,
        action: str,
        source: str = "telegram",
    ) -> None:
        payload = {
            "listing_id": listing_id,
            "action": action,
            "source": source,
        }
        resp = await self._client.post(
            "/feed/action",
            headers={"Authorization": f"Bearer {token}"},
            json=payload,
        )
        resp.raise_for_status()

    # --- Favorites ---

    async def get_favorites(self, token: str) -> List[Dict[str, Any]]:
        resp = await self._client.get(
            "/favorites/",
            headers={"Authorization": f"Bearer {token}"},
        )
        resp.raise_for_status()
        return resp.json()

    # --- Leads ---

    async def get_my_leads(self, token: str) -> List[Dict[str, Any]]:
        resp = await self._client.get(
            "/leads/my",
            headers={"Authorization": f"Bearer {token}"},
        )
        resp.raise_for_status()
        return resp.json()
