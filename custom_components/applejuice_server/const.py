"""Constants for the appleJuice Server integration."""

from homeassistant.const import Platform

DOMAIN = "applejuice_server"

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.SENSOR,
]

CONF_URL = "url"
CONF_PORT = "port"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_TLS = "tls"
CONF_OPTION_POLLING_RATE = "polling_rate"

DEFAULT_PORT = 8001
DEFAULT_POLLING_RATE = 30
MIN_POLLING_RATE = 5
MAX_POLLING_RATE = 3600

TIMEOUT = 10
