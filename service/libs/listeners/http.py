"""The http listener."""

from flask import Flask, request

from libs import helpers


class Listener:
    """Represents an http listener object."""

    def __init__(self, name):
        """Initialize the http listener object."""
        self._app = None
        self.name = name

    @property
    def app(self):
        """Return the app property if set, otherwise instantiate the Flask app."""
        if self._app is None:
            self._app = Flask(self.name)
            self._app.add_url_rule(rule="/", endpoint="index", view_func=self.index)
        return self._app

    def run(self, port):
        """Run the Flask app."""
        helpers.info(f"{self.name} run")
        self.app.run(port=port)

    # App Routes
    def index(self):
        """Route requests to the index path."""
        helpers.info(f"{self.name} index")
        res_data = {"message": f"Hello from {self.name}", "request": str(request)}
        return self.app.make_response(res_data)
