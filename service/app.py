"""The main app."""

import os
from multiprocessing import Process
from pathlib import Path

from libs.listeners import http


def main():
    """Start all relevant listeners."""
    # - Get logs directory
    log_dir = Path(os.getenv("LOGDIR"))
    if not log_dir.exists():
        log_dir.mkdir(parents=True)
    if not log_dir.is_dir():
        raise RuntimeError(f"Given path '{log_dir}' already exists and is not a dir.")
    # - Start listeners
    http_listen_1 = http.Listener(name="http1", log_dir=log_dir)
    listener_1 = Process(target=http_listen_1.run, kwargs={"port": 5000})
    listener_1.start()


if __name__ == "__main__":
    main()
