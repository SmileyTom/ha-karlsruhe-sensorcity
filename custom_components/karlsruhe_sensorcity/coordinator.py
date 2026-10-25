"""DataUpdateCoordinator for Karlsruhe Sensor City."""
from __future__ import annotations

import logging
from datetime import timedelta
from urllib.parse import quote

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import BASE_URL, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


def _build_url(beschreibung: str, name_prefix: str) -> str:
    where = f"beschreibung = '{beschreibung}' AND name LIKE '{name_prefix}%'"
    params = (
        f"f=json"
        f"&where={quote(where)}"
        f"&outFields=*"
        f"&resultRecordCount=1"
        f"&orderByFields=measured_at%20DESC"
    )
    return f"{BASE_URL}?{params}"


class SensorCityCoordinator(DataUpdateCoordinator):
    """Fetches data for one Sensor City station."""

    def __init__(
        self,
        hass: HomeAssistant,
        name: str,
        sensor_type: str,
        beschreibung: str,
        name_prefix: str,
    ) -> None:
        self.url = _build_url(beschreibung, name_prefix)
        self.sensor_name = name
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{name_prefix}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
        except Exception as err:
            raise UpdateFailed(f"Fehler beim Abruf von Sensor City: {err}") from err

        features = data.get("features", [])
        if not features:
            raise UpdateFailed(f"Keine Daten für {self.sensor_name}")

        return features[0]["attributes"]
