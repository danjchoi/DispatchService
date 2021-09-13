"""The gmail sender."""

import email
import logging
import smtplib
import ssl
import time

from libs import helpers


class Sender:
    """Represents a gmail sender object."""

    SMTP_SSL_PORT = 465
    GMAIL_SMTP_HOST = "smtp.gmail.com"

    def __init__(
        self,
        email,
        password,
        recipient,
        subject,
        body,
        name=None,
        log_dir=None,
        log_level=logging.DEBUG,
    ):
        """Initialize the gmail sender object."""
        self.email = email
        self.password = password
        self.recipient = recipient
        self.subject = subject
        self.body = body
        self.name = name or helpers.rand_alphanumeric()
        self.sender_name = f"{self.name}_sender"
        self.log_dir = log_dir
        self.log_level = log_level
        self._logger = None

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
        log_file_path = f"{self.sender_name}.log"
        if self.log_dir is not None:
            log_file_path = f"{self.log_dir}/{log_file_path}"
        # - Create handler
        handler = logging.FileHandler(log_file_path)
        handler.setFormatter(formatter)
        # - Create logger
        self._logger = logging.getLogger(self.sender_name)
        self._logger.setLevel(self.log_level)
        self._logger.addHandler(handler)
        return self._logger

    def run(self):
        """Run the sender."""
        msg = self._build_message()
        self.logger.debug(helpers.info(self.sender_name))
        self.logger.debug(f'Sending message "{msg.as_string()}"')
        try:
            self._send_message(msg)
        finally:
            self.logger.debug("Sender closing")

    def _build_message(self):
        """Build the message to send."""
        headers = {
            "From": self.email,
            "To": self.recipient,
            "Subject": self.subject,
        }
        message = email.message.Message()
        for key, val in headers.items():
            message.add_header(key, val)
        message.set_payload(self.body)
        return message

    def _send_message(self, message):
        """Send the message."""
        context = ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL(
                self.GMAIL_SMTP_HOST, self.SMTP_SSL_PORT, context=context
            ) as server:
                server.login(self.email, self.password)
                rejected = server.send_message(message)
                for key, val in rejected.items():
                    self.logger.warn(f'Failed to send to "{key}", Error: "{val}"')
        except Exception as err:
            self.logger.error(f"Received error while sending: {err}")
            raise
