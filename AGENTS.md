# ha-applejuice-server

Home-Assistant-Integration für den appleJuice Server (`custom_components/applejuice_server`). Nutzer-Doku steht in `README.md`, alles andere hier.

## Aufbau

- `api.py`: `AppleJuiceClient` holt `/info.json` mit HTTP Basic Auth. 401/403 wird zu `AppleJuiceAuthError`, alles andere (Timeout, Verbindung, kein gültiges JSON) zu `AppleJuiceConnectionError`.
- `coordinator.py`: bildet die Metriken aus `/info.json` über die Tabelle `METRICS` auf Coordinator-Schlüssel ab. Fehlende oder nicht numerische Metriken werden `None` (Sensor `unknown`). `serverstatus_ok` ist `health == 1`. Die Server-Version kommt aus `applejuice_build_info`.
- `entity.py`: `AppleJuiceServerEntity` und `AppleJuiceNetworkEntity`.
- Plattformen: `sensor`, `binary_sensor`. Daten liegen in `entry.runtime_data`, kein `hass.data`.
- Server- und Network-Device werden in `__init__.py` registriert. Network hängt über `via_device_id` am Server; `via_device` in `DeviceInfo` ist deprecated.
- Der Binary Sensor `Server Status` ist `PROBLEM`: an, wenn der Server meldet, dass er voll ist (`health != 1`).
- Entity-Keys `memory used` und `memory max` enthalten ein Leerzeichen. Sie bleiben so, weil die Unique-IDs bestehender Installationen daran hängen.

## Tests

Unit- und Integrationstests laufen gegen echtes Home Assistant mit gemocktem Server:

```bash
python3 -m venv $TMPDIR/hav
$TMPDIR/hav/bin/pip install homeassistant pytest-homeassistant-custom-component
$TMPDIR/hav/bin/python -m pytest -q -p no:sugar
```

Auf dieser Maschine scheitert der Build von `lru-dict` (gepinnt). Dann `homeassistant` und `pytest-homeassistant-custom-component` mit `--no-deps` installieren, die Abhängigkeiten aus `importlib.metadata.requires(...)` ohne `lru-dict` per `pip install -r` nachziehen und `lru-dict` ungepinnt installieren. `defusedxml` ist hier nicht nötig.

## Test mit echtem Home Assistant und Server (`test-env/`)

`test-env/compose.yaml` startet Home Assistant im Docker-Netz `applejuice-isolated_isolated` (aus `isolated-network/`, muss laufen) gegen den vorhandenen Test-Server `server-a`.

| Dienst | Adresse | Zugang |
| --- | --- | --- |
| Server `server-a` (aus `isolated-network/`) | `198.51.100.11:8001` | Login `aj` / `aj` |
| `homeassistant` (Image `:stable`) | `http://127.0.0.1:8125`, im Netz `198.51.100.33` | Login `admin` / `admin` |
| `homeassistant-beta` (Image `:beta`, Profil `beta`) | `http://127.0.0.1:8126`, im Netz `198.51.100.34` | Login `admin` / `admin` |

Die Ports sind nur an `127.0.0.1` gebunden. Von einem anderen Rechner per SSH-Tunnel erreichen: `ssh -L 8125:127.0.0.1:8125 -L 8126:127.0.0.1:8126 <host>`.

Ablauf:

1. Bilder müssen lokal vorhanden sein (`docker pull ghcr.io/home-assistant/home-assistant:stable` und `:beta`). Die Compose-Datei setzt `pull_policy: never`. Der Platz auf `/` ist knapp: vorher `df -h /` prüfen.
2. In `test-env/` mit `docker compose up -d homeassistant` und `docker compose --profile beta up -d homeassistant-beta` starten. Das Terminal-Tool hält `up -d` für einen Dauerprozess; mit `background=true` und `notify=true` starten.
3. `python3 test-env/ha_provision.py <PORT>` (8125 oder 8126) legt beim ersten Lauf Benutzer und Onboarding an, richtet die Integration per Config-Flow ein (prüft auch das falsche Passwort), und listet die Entities. Das Skript ist idempotent. Exit-Code 1, wenn Sensoren `unavailable` sind.
4. Reauth live prüfen: Container stoppen, im Volume `.storage/core.config_entries` das Passwort ändern, Container starten. Der Entry geht auf `setup_error invalid_auth`. Wiederherstellen über den Reconfigure-Flow (`source: reconfigure`).
5. Home Assistant liest `custom_components/applejuice_server` direkt als Read-only-Bind-Mount. Nach Code-Änderungen den Container neu starten und `docker logs` auf `applejuice` und Deprecation-Meldungen prüfen.

Getestete Stände: Home Assistant `2026.9.4` (Python 3.14.6) und `2026.10.0b1`. Beide ohne Warnungen des Plugins im Log.
