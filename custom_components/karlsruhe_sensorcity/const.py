DOMAIN = "karlsruhe_sensorcity"

BASE_URL = (
    "https://geoportal.karlsruhe.de/ags04/rest/services/Hosted/"
    "Sensordaten_NodeRED/FeatureServer/1/query"
)

DEFAULT_SCAN_INTERVAL = 300  # 5 minutes

CONF_SENSORS = "sensors"

SENSOR_TYPE_WIND = "wind"
SENSOR_TYPE_TEMPERATURE = "temperature"

SENSOR_TYPES = {
    SENSOR_TYPE_WIND: {
        "beschreibung": "Wind-Sensor",
        "label": "Wind",
    },
    SENSOR_TYPE_TEMPERATURE: {
        "beschreibung": "Temperatur-Sensor",
        "label": "Temperatur",
    },
}
