"""The main app."""

import pathlib
from multiprocessing import Process

from libs import helpers
from libs.listeners import http


if __name__ == "__main__":
    print(helpers.info("main"))
    log_dir = pathlib.Path(input("Full path to the logs dir: "))
    if not log_dir.exists():
        log_dir.mkdir(parents=True)
    if not log_dir.is_dir():
        raise RuntimeError(f"Given path '{log_dir}' already exists and is not a dir.")
    http_listen_1 = http.Listener(name="http1", log_dir=log_dir)
    http_listen_2 = http.Listener(name="http2", log_dir=log_dir)
    listener_1 = Process(target=http_listen_1.run, kwargs={"port": 5000})
    listener_2 = Process(target=http_listen_2.run, kwargs={"port": 5001})
    listener_1.start()
    listener_2.start()
    # listener_1.join()
