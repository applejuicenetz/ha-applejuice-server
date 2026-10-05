#!/usr/bin/env python3
"""Provision a fresh Home Assistant test instance and verify the appleJuice Server integration.

Usage: ha_provision.py [PORT] [SERVER_HOST] [USER] [PASSWORD]
Defaults: 8125, 198.51.100.11, aj, aj. Login afterwards: admin / admin.
"""
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

PORT = sys.argv[1] if len(sys.argv) > 1 else "8125"
SERVER = sys.argv[2] if len(sys.argv) > 2 else "198.51.100.11"
USER = sys.argv[3] if len(sys.argv) > 3 else "aj"
PW = sys.argv[4] if len(sys.argv) > 4 else "aj"
SERVER_PORT = 8001
B = f"http://127.0.0.1:{PORT}"
CID = B + "/"
P = "_" + SERVER.replace(".", "_") + f"_{SERVER_PORT}_"


def req(path, data=None, token=None, form=False, method=None):
    headers = {} if form else {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    body = urllib.parse.urlencode(data).encode() if form else (json.dumps(data).encode() if data is not None else None)
    r = urllib.request.Request(B + path, body, headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=90) as resp:
            return json.loads(resp.read() or b"null")
    except urllib.error.HTTPError as e:
        return {"_http": e.code, "_body": e.read().decode()[:300]}


def token_from_code(code):
    return req("/auth/token", {"grant_type": "authorization_code", "code": code, "client_id": CID}, form=True)["access_token"]


for _ in range(90):
    try:
        urllib.request.urlopen(B + "/manifest.json", timeout=3)
        break
    except Exception:
        time.sleep(3)
else:
    sys.exit("HA not reachable")

steps = req("/api/onboarding")
if isinstance(steps, list) and any(not s["done"] for s in steps):
    r = req("/api/onboarding/users", {"client_id": CID, "name": "Admin", "username": "admin", "password": "admin", "language": "de"})
    token = token_from_code(r["auth_code"])
    for step in ("core_config", "analytics"):
        req(f"/api/onboarding/{step}", {}, token, method="POST")
    req("/api/onboarding/integration", {"client_id": CID, "redirect_uri": CID}, token, method="POST")
else:
    f = req("/auth/login_flow", {"client_id": CID, "handler": ["homeassistant", None], "redirect_uri": CID})
    r = req("/auth/login_flow/" + f["flow_id"], {"username": "admin", "password": "admin", "client_id": CID})
    token = token_from_code(r["result"])

print("HA", req("/api/config", token=token)["version"])

if not any(e["domain"] == "applejuice_server" for e in req("/api/config/config_entries/entry", token=token)):
    flow = req("/api/config/config_entries/flow", {"handler": "applejuice_server", "show_advanced_options": False}, token, method="POST")
    fid = "/api/config/config_entries/flow/" + flow["flow_id"]
    data = {"url": SERVER, "port": SERVER_PORT, "username": USER, "password": PW, "tls": False}
    bad = req(fid, {**data, "password": "falsch"}, token, method="POST")
    print("wrong password ->", bad.get("errors"))
    ok = req(fid, data, token, method="POST")
    print("config flow ->", ok.get("type"), ok.get("title"))
    time.sleep(8)

states = {s["entity_id"]: s for s in req("/api/states", token=token)}
mine = {k: v for k, v in states.items() if P in k or "applejuice_network" in k}
broken = [k for k, v in mine.items() if v["state"] in ("unavailable", "unknown")]
print(len(mine), "applejuice entities; unavailable/unknown:", broken or "keine")
for k in sorted(mine):
    if any(x in k for x in ("_users", "open_connections", "server_status", "global_users")):
        print(" ", k, mine[k]["state"])
sys.exit(1 if any(k.startswith(("sensor.", "binary_sensor.")) and "applejuice" in k and mine[k]["state"] == "unavailable" for k in mine) else 0)
