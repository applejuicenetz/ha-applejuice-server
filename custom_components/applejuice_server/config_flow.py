from __future__ import annotations

import logging
from logging import Logger

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.util import network, slugify

from .api import get_raw_data

from .const import (
    CONF_URL,
    CONF_PORT,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_TLS,
    CONF_OPTION_POLLING_RATE,
    DOMAIN,
)

CONF_UPDATE_INTERVAL = "update_interval"

_LOGGER = logging.getLogger(__name__)


class AppleJuiceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow for appleJuice Server."""

    VERSION = 1

    def __init__(self):
        """Initialize."""
        _LOGGER.debug("loading appleJuice Server conf FlowHandler")
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        if user_input is not None:
            if not await self._test_host(user_input[CONF_URL]):
                self._errors[CONF_URL] = "host_error"
                return await self._show_config_form(user_input)

            if not await self._test_port(user_input[CONF_PORT]):
                self._errors[CONF_PORT] = "port_error"
                return await self._show_config_form(user_input)

            if not await self._test_connection(
                    user_input[CONF_URL],
                    user_input[CONF_PORT],
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                    user_input[CONF_TLS],
            ):
                self._errors[CONF_URL] = "core_connection_error"
                return await self._show_config_form(user_input)

            return self.async_create_entry(title=f"{user_input[CONF_URL]}:{user_input[CONF_PORT]}", data=user_input)

        user_input = {CONF_URL: "", CONF_PORT: 8001, CONF_TLS: False, CONF_USERNAME: "", CONF_PASSWORD: ""}

        return await self._show_config_form(user_input)

    async def _show_config_form(self, user_input):
        """Show the configuration form to edit location data."""

        _LOGGER.debug("Showing appleJuice Server conf")

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_URL, default=user_input[CONF_URL]): str,
                    vol.Required(CONF_PORT, default=user_input[CONF_PORT]): int,
                    vol.Required(CONF_USERNAME, default=user_input[CONF_USERNAME]): str,
                    vol.Required(CONF_PASSWORD, default=user_input[CONF_PASSWORD]): str,
                    vol.Optional(CONF_TLS, default=user_input[CONF_TLS]): bool,
                }
            ),
            errors=self._errors,
        )

    async def _test_host(self, host: str):
        return network.is_host_valid(host)

    async def _test_port(self, port):
        if port != "":
            if int(port) > 65535 or int(port) <= 1:
                return False
        return True

    async def _test_connection(self, host, port, username, password, tls):
        """Validate the connection by requesting /xml/information.xml."""

        xml_data = await get_raw_data(self.hass, host, port, username, password, tls, "/info.xml")

        if xml_data is None:
            return False

        if "applejuiceserver" in xml_data:
            return True

        return False

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry, ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
            self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_OPTION_POLLING_RATE,
                        default=self.config_entry.options.get(
                            CONF_OPTION_POLLING_RATE, 30
                        ),
                    ): int,
                }
            ),
        )
