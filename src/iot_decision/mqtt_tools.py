"""Extraction et préchargement MQTT pour le laboratoire local."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path


def _mqtt():
    try:
        import paho.mqtt.client as mqtt
    except ImportError as exc:
        raise SystemExit("Installer paho-mqtt: python3 -m pip install paho-mqtt") from exc
    return mqtt


def seed(sample: Path, host: str, port: int, username: str | None = None, password: str | None = None) -> int:
    mqtt = _mqtt()
    records = [json.loads(line) for line in sample.read_text(encoding="utf-8").splitlines() if line]
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="s01-seeder")
    if username:
        client.username_pw_set(username, password)
    client.connect(host, port, 60)
    client.loop_start()
    for record in records:
        payload = json.dumps(record["payload"], ensure_ascii=False, separators=(",", ":"))
        info = client.publish(record["topic"], payload, qos=1, retain=True)
        info.wait_for_publish()
    client.loop_stop()
    client.disconnect()
    return len(records)


def extract(destination: Path, host: str, port: int, topic: str, idle: float,
            username: str | None = None, password: str | None = None) -> int:
    mqtt = _mqtt()
    messages: list[dict] = []
    last_message = time.monotonic()

    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code != 0:
            raise RuntimeError(f"connexion MQTT refusée: {reason_code}")
        client.subscribe(topic, qos=1)

    def on_message(client, userdata, message):
        nonlocal last_message
        payload_text = message.payload.decode("utf-8")
        messages.append({
            "topic": message.topic,
            "received_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "retained": bool(message.retain),
            "payload": json.loads(payload_text),
        })
        last_message = time.monotonic()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="s01-extractor")
    if username:
        client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(host, port, 60)
    client.loop_start()
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline and (not messages or time.monotonic() - last_message < idle):
        time.sleep(0.05)
    client.loop_stop()
    client.disconnect()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="\n") as stream:
        for record in messages:
            stream.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
    return len(messages)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Outils MQTT de la séquence 1")
    parser.add_argument("action", choices=("seed", "extract"))
    parser.add_argument("path", type=Path)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=1883)
    parser.add_argument("--topic", default="airbase/batch001/#")
    parser.add_argument("--idle", type=float, default=1.0)
    parser.add_argument("--username", default=None, help="requis par le broker protégé de la séquence 7")
    parser.add_argument("--password", default=None)
    args = parser.parse_args(argv)
    count = seed(args.path, args.host, args.port, args.username, args.password) if args.action == "seed" else extract(
        args.path, args.host, args.port, args.topic, args.idle, args.username, args.password)
    print(f"{count} messages {'publiés' if args.action == 'seed' else 'extraits'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
