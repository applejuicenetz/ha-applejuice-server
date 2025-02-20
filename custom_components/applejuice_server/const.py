from homeassistant.const import Platform

DOMAIN = "applejuice_server"

PLATFORMS = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
]

CONF_URL = "url"
CONF_PORT = "port"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_TLS = "tls"
CONF_OPTION_POLLING_RATE = "polling_rate"

TIMEOUT = 10
