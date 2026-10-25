"""Config flow for Karlsruhe Sensor City."""
from __future__ import annotations

import logging
from urllib.parse import quote

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .const import BASE_URL, DOMAIN, SENSOR_TYPE_TEMPERATURE, SENSOR_TYPE_WIND

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPE_LABELS = {
    SENSOR_TYPE_WIND: "Wind-Sensor",
    SENSOR_TYPE_TEMPERATURE: "Temperatur-Sensor",
}

STEP_SCHEMA = vol.Schema(
    {
        vol.Required("name_prefix"): str,
        vol.Required("sensor_type", default=SENSOR_TYPE_WIND): vol.In(
            list(SENSOR_TYPE_LABELS.keys())
        ),
    }
)


async def _validate_sensor(hass: HomeAssistant, name_prefix: str, sensor_type: str) -> dict:
    """Fetch one record to validate and get the station name."""
    beschreibung = SENSOR_TYPE_LABELS[sensor_type]
    where = f"beschreibung = '{beschreibung}' AND name LIKE '{name_prefix}%'"
    url = (
        f"{BASE_URL}?f=json"
        f"&where={quote(where)}"
        f"&outFields=name,measured_at"
        f"&resultRecordCount=1"
        f"&orderByFields=measured_at%20DESC"
    )
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
            resp.raise_for_status()
            data = await resp.json()

    features = data.get("features", [])
    if not features:
        raise ValueError(f"Kein Sensor mit Name '{name_prefix}' gefunden")

    return {"station_name": features[0]["attributes"].get("name", name_prefix)}


class KarlsruheSensorCityConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Karlsruhe Sensor City."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            name_prefix = user_input["name_prefix"].strip()
            sensor_type = user_input["sensor_type"]
            try:
                info = await _validate_sensor(self.hass, name_prefix, sensor_type)
            except ValueError as err:
                errors["name_prefix"] = "sensor_not_found"
                _LOGGER.warning("Sensor nicht gefunden: %s", err)
            except Exception as err:
                errors["base"] = "cannot_connect"
                _LOGGER.error("Verbindungsfehler: %s", err)
            else:
                station_name = info["station_name"]
                await self.async_set_unique_id(
                    f"{name_prefix.lower().replace(' ', '_')}_{sensor_type}"
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=station_name,
                    data={
                        "name_prefix": name_prefix,
                        "sensor_type": sensor_type,
                        "station_name": station_name,
                        "beschreibung": SENSOR_TYPE_LABELS[sensor_type],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_SCHEMA,
            errors=errors,
            description_placeholders={
                "example_wind": "154",
                "example_temp": "155",
            },
        )
