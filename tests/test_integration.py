"""Integration tests against a mocked appleJuice Server."""

import aiohttp
import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.applejuice_server.const import DOMAIN

HOST, PORT = "server.local", 8001
URL = f"http://{HOST}:{PORT}/info.json"


def _m(value, kind="gauge"):
    return {"help": "x", "type": kind, "value": value}


INFO = {
    "applejuice_build_info": _m("0.85.1"),
    "applejuice_local_users": _m(103),
    "applejuice_firewalled_users": _m(22),
    "applejuice_local_files": _m(767897),
    "applejuice_local_file_size_bytes": _m(297121984843801),
    "applejuice_global_users": _m(447),
    "applejuice_global_files": _m(3582999),
    "applejuice_global_file_size_bytes": _m(1342270903481172),
    "applejuice_open_connections": _m(106),
    "applejuice_socket_tasks_open": _m(0),
    "applejuice_memory_used_bytes": _m(258189848),
    "applejuice_memory_free_bytes": _m(580670952),
    "applejuice_memory_max_bytes": _m(8136949760),
    "applejuice_upload_bytes_per_sec": _m(1299),
    "applejuice_download_bytes_per_sec": _m(1098),
    "applejuice_sources_sent": _m(15903, "counter"),
    "applejuice_server_health": _m(1),
}


def make_entry() -> MockConfigEntry:
    return MockConfigEntry(
        domain=DOMAIN,
        unique_id=f"{HOST}:{PORT}",
        data={"url": HOST, "port": PORT, "username": "aj", "password": "aj", "tls": False},
    )


async def setup(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


def eid(hass: HomeAssistant, platform: str, key: str, entry) -> str | None:
    return er.async_get(hass).async_get_entity_id(platform, DOMAIN, f"{entry.entry_id}_{key}")


async def test_setup_states_and_devices(hass: HomeAssistant, aioclient_mock) -> None:
    aioclient_mock.get(URL, json=INFO)
    entry = make_entry()
    await setup(hass, entry)
    assert entry.state is ConfigEntryState.LOADED

    assert hass.states.get(eid(hass, "sensor", "users", entry)).state == "103"
    assert hass.states.get(eid(hass, "sensor", "globaluser", entry)).state == "447"
    assert hass.states.get(eid(hass, "sensor", "open_connections", entry)).state == "106"
    assert hass.states.get(eid(hass, "sensor", "memory used", entry)).state == "258189848"
    # nicht gelieferte Metriken -> unknown statt Fehler
    assert hass.states.get(eid(hass, "sensor", "searches", entry)).state == "unknown"
    assert hass.states.get(eid(hass, "binary_sensor", "serverstatus_ok", entry)).state == "off"

    registry = dr.async_get(hass)
    server = registry.async_get_device({(DOMAIN, entry.entry_id)})
    network = registry.async_get_device({(DOMAIN, f"{entry.entry_id}_network")})
    assert server.sw_version == "0.85.1"
    assert network.via_device_id == server.id


async def test_server_full_is_problem(hass: HomeAssistant, aioclient_mock) -> None:
    aioclient_mock.get(URL, json={**INFO, "applejuice_server_health": _m(0)})
    entry = make_entry()
    await setup(hass, entry)
    assert hass.states.get(eid(hass, "binary_sensor", "serverstatus_ok", entry)).state == "on"


async def test_credentials_sent_as_basic_auth(hass: HomeAssistant) -> None:
    """The client passes username and password as aiohttp.BasicAuth."""
    from unittest.mock import MagicMock

    from custom_components.applejuice_server.api import AppleJuiceClient

    response = MagicMock(status=200)
    response.text = MagicMock(return_value=_async_value('{"applejuice_server_health": {"value": 1}}'))
    response.raise_for_status = MagicMock()
    ctx = MagicMock()
    ctx.__aenter__ = MagicMock(return_value=_async_value(response))
    ctx.__aexit__ = MagicMock(return_value=_async_value(False))
    session = MagicMock()
    session.get = MagicMock(return_value=ctx)

    await AppleJuiceClient(session, HOST, PORT, "aj", "geheim", False).get_info()
    kwargs = session.get.call_args.kwargs
    assert kwargs["auth"] == aiohttp.BasicAuth("aj", "geheim")
    assert "geheim" not in session.get.call_args.args[0]


def _async_value(value):
    async def _inner(*args, **kwargs):
        return value

    return _inner()


async def test_wrong_credentials_trigger_reauth(hass: HomeAssistant, aioclient_mock) -> None:
    aioclient_mock.get(URL, status=401)
    entry = make_entry()
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.SETUP_ERROR
    assert any(hass.config_entries.flow.async_progress_by_handler(DOMAIN))


async def test_unreachable_retries(hass: HomeAssistant, aioclient_mock) -> None:
    aioclient_mock.get(URL, exc=aiohttp.ClientError)
    entry = make_entry()
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    assert entry.state is ConfigEntryState.SETUP_RETRY


async def test_invalid_json_retries(hass: HomeAssistant, aioclient_mock) -> None:
    aioclient_mock.get(URL, text="<html>nope</html>")
    entry = make_entry()
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    assert entry.state is ConfigEntryState.SETUP_RETRY


async def test_config_flow(hass: HomeAssistant, aioclient_mock) -> None:
    aioclient_mock.get(URL, json=INFO)
    data = {"url": HOST, "port": PORT, "username": "aj", "password": "aj", "tls": False}
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    result = await hass.config_entries.flow.async_configure(result["flow_id"], data)
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert isinstance(result["data"]["port"], int)

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    result = await hass.config_entries.flow.async_configure(result["flow_id"], data)
    assert result["type"] is FlowResultType.ABORT and result["reason"] == "already_configured"


async def test_config_flow_errors(hass: HomeAssistant, aioclient_mock) -> None:
    aioclient_mock.get(URL, status=401)
    data = {"url": HOST, "port": PORT, "username": "aj", "password": "x", "tls": False}
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    result = await hass.config_entries.flow.async_configure(result["flow_id"], data)
    assert result["errors"] == {"base": "invalid_auth"}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {**data, "url": "http://bad"})
    assert result["errors"] == {"url": "host_error"}


async def test_config_flow_not_a_server(hass: HomeAssistant, aioclient_mock) -> None:
    aioclient_mock.get(URL, json={"foo": 1})
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"url": HOST, "port": PORT, "username": "aj", "password": "aj", "tls": False}
    )
    assert result["errors"] == {"base": "core_connection_error"}


async def test_reauth_flow(hass: HomeAssistant, aioclient_mock) -> None:
    aioclient_mock.get(URL, json=INFO)
    entry = make_entry()
    entry.add_to_hass(hass)
    result = await entry.start_reauth_flow(hass)
    assert result["step_id"] == "reauth_confirm"
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {"username": "aj", "password": "new"})
    assert result["type"] is FlowResultType.ABORT and result["reason"] == "reauth_successful"
    assert entry.data["password"] == "new"


async def test_options_flow_reloads(hass: HomeAssistant, aioclient_mock) -> None:
    aioclient_mock.get(URL, json=INFO)
    entry = make_entry()
    await setup(hass, entry)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"polling_rate": 60})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert entry.runtime_data.update_interval.total_seconds() == 60


async def test_unload(hass: HomeAssistant, aioclient_mock) -> None:
    aioclient_mock.get(URL, json=INFO)
    entry = make_entry()
    await setup(hass, entry)
    assert await hass.config_entries.async_unload(entry.entry_id)
    assert entry.state is ConfigEntryState.NOT_LOADED
