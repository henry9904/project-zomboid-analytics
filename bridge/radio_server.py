"""
Radio Bridge Server — Phase 3
Watches game_state.json written by Lua mod → calls Claude API → writes response.json

Usage:
    pip install anthropic watchdog
    python bridge/radio_server.py --watch-dir "C:/Users/YOU/Zomboid/Lua"
"""

import argparse
import json
import time
from pathlib import Path

import anthropic
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

WATCH_FILE = "game_state.json"
RESPONSE_FILE = "response.json"

SYSTEM_PROMPT = (
    "You are a crackling emergency radio broadcaster in a zombie apocalypse. "
    "Generate a single short radio transmission (2-3 sentences max) that reflects "
    "the player's current situation. Be atmospheric, terse, slightly ominous. "
    "No greetings, no sign-offs. Just the transmission content."
)


def build_user_prompt(state: dict) -> str:
    return (
        f"Day {state.get('day', '?')} of the outbreak. "
        f"Survivor at grid ({state.get('x', '?')}, {state.get('y', '?')}). "
        f"Weather: {state.get('weather', 'unknown')}. "
        f"Kills today: {state.get('kills_today', 0)}. "
        f"Hunger level: {state.get('hunger', 0):.0%}. "
        f"Generate a radio transmission."
    )


def call_claude(state: dict) -> str:
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",  # fast + cheap for real-time use
        max_tokens=120,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_prompt(state)}],
    )
    return message.content[0].text.strip()


class GameStateHandler(FileSystemEventHandler):
    def __init__(self, watch_dir: Path):
        self.watch_dir = watch_dir
        self._last_mtime = 0.0

    def on_modified(self, event):
        if Path(event.src_path).name != WATCH_FILE:
            return
        mtime = Path(event.src_path).stat().st_mtime
        if mtime == self._last_mtime:
            return
        self._last_mtime = mtime

        try:
            state = json.loads(Path(event.src_path).read_text(encoding="utf-8"))
            print(f"[RadioBridge] State received: day={state.get('day')}")
            transmission = call_claude(state)
            print(f"[RadioBridge] Transmission: {transmission}")
            response_path = self.watch_dir / RESPONSE_FILE
            response_path.write_text(
                json.dumps({"text": transmission, "ts": time.time()}, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception as e:
            print(f"[RadioBridge] Error: {e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--watch-dir",
        default=str(Path.home() / "Zomboid" / "Lua"),
        help="Directory where Lua mod writes game_state.json",
    )
    args = parser.parse_args()
    watch_dir = Path(args.watch_dir)
    watch_dir.mkdir(parents=True, exist_ok=True)

    print(f"[RadioBridge] Watching {watch_dir / WATCH_FILE}")
    handler = GameStateHandler(watch_dir)
    observer = Observer()
    observer.schedule(handler, str(watch_dir), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
