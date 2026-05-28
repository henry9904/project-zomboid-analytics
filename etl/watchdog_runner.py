"""Live ingestion: watch ``data/raw/`` for new CSV chunks dropped by the Lua
mod and stream them straight into the warehouse without restarting the
pipeline. Use while a game session is running."""
from __future__ import annotations

import argparse
import logging
import time
from pathlib import Path

from watchdog.events import FileCreatedEvent, FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer

from etl import extract, load, transform
from etl.pipeline import DATASET_TO_TABLE, DEFAULT_SCHEMA

log = logging.getLogger(__name__)


class RawCSVHandler(FileSystemEventHandler):
    def __init__(self, engine) -> None:
        self.engine = engine

    def _process(self, path: Path) -> None:
        for dataset in DATASET_TO_TABLE:
            prefix = f"{dataset}_session_"
            if not path.name.startswith(prefix) or not path.name.endswith(".csv"):
                continue
            session = path.stem.removeprefix(prefix)
            raw = extract.RawFile(dataset, session, path)
            try:
                df = extract.read(raw)
                clean = transform.transform(dataset, df)
                load.load(self.engine, DATASET_TO_TABLE[dataset], clean)
            except Exception as exc:
                log.exception("failed to ingest %s: %s", path, exc)
            return

    def on_created(self, event: FileCreatedEvent) -> None:
        if not event.is_directory:
            self._process(Path(event.src_path))

    def on_modified(self, event: FileModifiedEvent) -> None:
        if not event.is_directory:
            self._process(Path(event.src_path))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=Path("data/raw"))
    p.add_argument("--db", type=Path, default=Path("data/processed/zomboid.db"))
    args = p.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args.input.mkdir(parents=True, exist_ok=True)
    engine = load.init_db(args.db, DEFAULT_SCHEMA)
    handler = RawCSVHandler(engine)
    obs = Observer()
    obs.schedule(handler, str(args.input), recursive=False)
    obs.start()
    log.info("watching %s -> %s", args.input, args.db)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
