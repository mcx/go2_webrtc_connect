"""Obstacle-avoidance example — toggle on/off and query the current state.

All requests go to RTC_TOPIC["OBSTACLES_AVOID"] (= rt/api/obstacles_avoid/request).
api_ids in OBSTACLES_AVOID_API (constants.py).
"""

import asyncio
import json
import logging
import os
import sys

from unitree_webrtc_connect.webrtc_driver import UnitreeWebRTCConnection, WebRTCConnectionMethod
from unitree_webrtc_connect.constants import RTC_TOPIC, OBSTACLES_AVOID_API

logging.basicConfig(level=logging.FATAL)

ROBOT_IP = os.environ.get("UNITREE_ROBOT_IP", "192.168.8.181")


async def switch_set(conn, enable: bool):
    response = await conn.datachannel.pub_sub.publish_request_new(
        RTC_TOPIC["OBSTACLES_AVOID"],
        {"api_id": OBSTACLES_AVOID_API["SWITCH_SET"], "parameter": {"enable": enable}},
    )
    code = response.get("data", {}).get("header", {}).get("status", {}).get("code", -1)
    return code


async def switch_get(conn):
    """Returns (code, enabled) where enabled is True/False/None."""
    response = await conn.datachannel.pub_sub.publish_request_new(
        RTC_TOPIC["OBSTACLES_AVOID"],
        {"api_id": OBSTACLES_AVOID_API["SWITCH_GET"]},
    )
    code = response.get("data", {}).get("header", {}).get("status", {}).get("code", -1)
    data = response.get("data", {}).get("data", "")
    if code == 0 and data:
        try:
            return code, json.loads(data).get("enable")
        except Exception:
            return code, None
    return code, None


async def main():
    conn = UnitreeWebRTCConnection(WebRTCConnectionMethod.LocalSTA, ip=ROBOT_IP)
    await conn.connect()

    print("\nObstacle avoidance — pick a command:")
    print("  1: Enable")
    print("  2: Disable")
    print("  3: Query current state")
    print("  q: Quit")

    while True:
        raw = await asyncio.to_thread(input, "\nCommand: ")
        raw = raw.strip().lower()
        if raw == "q":
            break
        if raw == "1":
            code = await switch_set(conn, True)
            print(f"  Enabled  (code={code})")
        elif raw == "2":
            code = await switch_set(conn, False)
            print(f"  Disabled (code={code})")
        elif raw == "3":
            code, enabled = await switch_get(conn)
            state = "enabled" if enabled else ("disabled" if enabled is False else "?")
            print(f"  State: {state}  (code={code})")
        else:
            print("Invalid input")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting")
        sys.exit(0)
