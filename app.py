from flask import Flask
import logging
from plugin_manager import plugin_manager_blueprint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

app.register_blueprint(plugin_manager_blueprint)

if __name__ == "__main__":
    app.run(debug=True)