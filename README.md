# Karlsruhe Sensor City — Home Assistant Integration

Ruft aktuelle Messwerte vom [Karlsruhe Sensor City Geoportal](https://geoportal.karlsruhe.de/sensorcity/Dashboard/) ab und stellt sie als Sensoren in Home Assistant bereit.

## Unterstützte Sensortypen

| Typ | Felder |
|-----|--------|
| **Wind-Sensor** | Windgeschwindigkeit (Ø), Windrichtung, Böenstärke 1s, Böenstärke 3s |
| **Temperatur-Sensor** | Temperatur, Luftdruck, Luftfeuchte, Sonnenstrahlung |

## Installation via HACS

1. HACS → Integrationen → ⋮ → **Benutzerdefinierte Repositories**
2. URL: `https://github.com/SmileyTom/ha-karlsruhe-sensorcity`, Kategorie: **Integration**
3. Integration installieren, Home Assistant neustarten

## Konfiguration

1. **Einstellungen → Integrationen → Integration hinzufügen → Karlsruhe Sensor City**
2. Sensor-Nummer eingeben (z.B. `154` für Wind, `155` für Temperatur)
3. Sensor-Typ wählen

### Beispiel-Sensoren

| Sensor-Nr. | Name | Typ |
|-----------|------|-----|
| 154 | Zündhütle - Südtangente | Wind |
| 155 | Steinkreuzstraße | Temperatur |

## Technische Details

- Datenquelle: Stadt Karlsruhe, Lizenz: [Datenlizenz Deutschland – Namensnennung – Version 2.0](https://www.govdata.de/dl-de/by-2-0)
- API: ArcGIS FeatureServer (`Sensordaten_NodeRED`)
- Abfrageintervall: 5 Minuten
