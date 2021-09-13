"""The http listener."""

import logging
import time
from multiprocessing import Process

import flask
from dateutil import parser
from flask import Flask
from libs import helpers


class Listener:
    """Represents an http listener object."""

    KNOWN_EVENT_TYPES = ["market_dispatch"]
    KNOWN_PROGRAMS = {"1": "Voltus Interviews"}

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
            self._app.add_url_rule(
                rule="/", endpoint="index", view_func=self.index, methods=["POST"]
            )
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
        self.logger.debug(helpers.info(self.listener_name))
        self.app.run(port=port)

    # App Routes
    def index(self):
        """Handle requests to the index path."""
        res_data = {}

        # - Check for missing fields
        required_fields = ["start_time", "program_id", "event_type"]
        missing_fields = [
            field for field in required_fields if field not in flask.request.json
        ]
        if missing_fields:
            msg = f'Required fields "{missing_fields}" missing.'
            res_data["error_message"] = msg
            self.logger.info(f"Request rejected with message: ({msg})")
            return flask.make_response(res_data, 400)

        # - Check field types
        program_id = flask.request.json["program_id"]
        event_type = flask.request.json["event_type"]
        if type(program_id) is not str:
            msg = f'Field "program_id", value `{program_id}`, is not of type string.'
            res_data["error_message"] = msg
            self.logger.info(f"Request rejected with message: ({msg})")
            return flask.make_response(res_data, 400)
        if type(event_type) is not str:
            msg = f'Field "event_type", value `{event_type}`, is not of type string.'
            res_data["error_message"] = msg
            self.logger.info(f"Request rejected with message: ({msg})")
            return flask.make_response(res_data, 400)

        # - Check formatting of timestamps
        try:
            start_time = parser.parse(flask.request.json["start_time"])
        except parser.ParserError:
            msg = f'Field "start_time", value `{flask.request.json["start_time"]}`, is not a parsable datetime'
            res_data["error_message"] = msg

            self.logger.info(f"Request rejected with message: ({msg})")
            return flask.make_response(res_data, 400)
        end_time = None
        try:
            if "end_time" in flask.request.json:
                end_time = parser.parse(flask.request.json["end_time"])
                diff = end_time - start_time
                if diff.total_seconds() < 0:
                    raise ValueError("end_time comes before start_time")
        except parser.ParserError:
            msg = f'Field "end_time", value `{flask.request.json["end_time"]}`, is not a parsable datetime'
            res_data["error_message"] = msg
            self.logger.info(f"Request rejected with message: ({msg})")
            return flask.make_response(res_data, 400)
        except ValueError as err:
            if "end_time comes before start_time" not in str(err):
                raise
            msg = (
                f'Field "end_time", value `{flask.request.json["end_time"]}`, '
                'cannot come before "start_time", '
                f'value `{flask.request.json["start_time"]}`'
            )
            res_data["error_message"] = msg
            self.logger.info(f"Request rejected with message: ({msg})")
            return flask.make_response(res_data, 400)

        # - Assess event_type
        if event_type not in self.KNOWN_EVENT_TYPES:
            msg = f'Field "event_type", value `{event_type}`, is unknown.'
            res_data["error_message"] = msg
            self.logger.info(f"Request rejected with message: ({msg})")
            return flask.make_response(res_data, 400)

        # - Assess program_id
        if program_id not in self.KNOWN_PROGRAMS:
            msg = f'Field "program_id", value `{program_id}`, is unknown.'
            res_data["error_message"] = msg
            self.logger.info(f"Request rejected with message: ({msg})")
            return flask.make_response(res_data, 400)

        # - Create message
        msg = self._create_msg(self.KNOWN_PROGRAMS[program_id], start_time, end_time)

        # - Start sender processes
        # gmail_sender_1 = gmail.Sender(
        #     email, password, recipient, name="gmail1", log_dir=log_dir
        # )
        # sender_1 = Process(target=gmail_sender_1.run)
        # sender_1.start()

        return flask.make_response(msg, 200)

    def _create_msg(self, program_name, start_time, end_time):
        """Create message body."""
        # - Date format like "Monday Sep 25"
        date_format = "%A %b %d"
        # - Time format like "1:01 PM"
        time_format = "%I:%M %p"
        formatted_start_date = start_time.strftime(date_format)
        formatted_start_time = start_time.strftime(time_format)
        # - Create message
        msg = (
            "Hello Voltan,\n\n"
            f'You have been dispatched as part of the Program "{program_name}"\n\n'
            "Please have your full curtailment plan in effect starting on "
            f"{formatted_start_date} at {formatted_start_time}"
        )
        if end_time is not None:
            formatted_end_date = end_time.strftime(date_format)
            formatted_end_time = end_time.strftime(time_format)
            msg += f" ending on {formatted_end_date} at {formatted_end_time}"
        msg += ".\n\nSincerely,\nVoltus"
        return msg
