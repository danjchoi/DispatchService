"""The http listener."""

import logging
import time

from flask import Flask, request
from libs import helpers


class Listener:
    """Represents an http listener object."""

    def __init__(self, name=None, log_dir=None, log_level=logging.DEBUG):
        """Initialize the http listener object."""
        self._app = None
        self.log_dir = log_dir
        self.log_level = log_level
        self.name = name or helpers.rand_alphanumeric()
        self.listener_name = f"{self.name}_listener"
        self._logger = None

    @property
    def app(self):
        """Return the app property if set, otherwise instantiate the Flask app."""
        if self._app is None:
            self._app = Flask(self.name)
            self._app.add_url_rule(rule="/", endpoint="index", view_func=self.index)
        return self._app

    @property
    def logger(self):
        """Return the logger if set, otherwise get the configured logger and return it."""
        if self._logger is not None:
            return self._logger
        # - Create formatter
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s: %(filename)s,%(lineno)d %(funcName)s: %(message)s"
        )
        formatter.converter = time.gmtime
        # - Logs to execution dir if log_dir not provided
        log_file_path = f"{self.listener_name}.log"
        if self.log_dir is not None:
            log_file_path = f"{self.log_dir}/{log_file_path}"
        # - Create handler
        handler = logging.FileHandler(log_file_path)
        handler.setFormatter(formatter)
        # - Create logger
        self._logger = logging.getLogger(self.listener_name)
        self._logger.setLevel(self.log_level)
        self._logger.addHandler(handler)
        return self._logger

    def run(self, port):
        """Run the Flask app."""
        self.logger.debug(helpers.info(self.name))
        self.app.run(port=port)

    # App Routes
    def index(self):
        """Route requests to the index path."""
        res_data = {"message": f"Hello from {self.name}", "request": str(request)}
        return self.app.make_response(res_data)
