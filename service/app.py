"""The main app."""

import os
from multiprocessing import Process
from pathlib import Path

from libs import helpers
from libs.listeners import http
from libs.senders import gmail


if __name__ == "__main__":
    print(helpers.info("main"))
    log_dir = Path(input("Full path to the logs dir: "))

    if not log_dir.exists():
        log_dir.mkdir(parents=True)
    if not log_dir.is_dir():
        raise RuntimeError(f"Given path '{log_dir}' already exists and is not a dir.")
    # http_listen_1 = http.Listener(name="http1", log_dir=log_dir)
    # http_listen_2 = http.Listener(name="http2", log_dir=log_dir)
    # listener_1 = Process(target=http_listen_1.run, kwargs={"port": 5000})
    # listener_2 = Process(target=http_listen_2.run, kwargs={"port": 5001})
    # listener_1.start()
    # listener_2.start()
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    recipient = os.getenv("RECIPIENT")
    gmail_sender_1 = gmail.Sender(
        email, password, recipient, name="gmail1", log_dir=log_dir
    )
    sender_1 = Process(target=gmail_sender_1.run)
    sender_1.start()
