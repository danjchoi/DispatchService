"""The main app."""

from multiprocessing import Process

from libs import helpers
from libs.listeners import http


if __name__ == "__main__":
    helpers.info("main")
    http_listen_1 = http.Listener("First Listener")
    http_listen_2 = http.Listener("Second Listener")
    listener_1 = Process(target=http_listen_1.run, kwargs={"port": 5000})
    listener_2 = Process(target=http_listen_2.run, kwargs={"port": 5001})
    listener_1.start()
    listener_2.start()
    # listener_1.join()
