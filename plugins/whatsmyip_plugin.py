
from . import plugin_base
import logging, requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhatsMyIPPlugin(plugin_base.InfoPlugin):
    def plugin_setup(self):
        logger.info("Loaded WhatsMyIPPlugin")
    def __init__(self):
        super().__init__("WhatsMyIPPlugin", "A simple test to check my IP", "Utilities", "Demos", {"IP" : plugin_base.OutputArgType.html})
    def execute_plugin(self):
        response = requests.get("http://ifconfig.me").text
        return {"IP": response }


