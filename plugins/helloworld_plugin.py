
from . import plugin_base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HelloWorldPlugin(plugin_base.InputOutputPlugin):
    '''
    A simple test plugin, returns {Example output: Hello World}
    '''
    def plugin_setup(self):
        logger.info("Loaded HelloWorldPlugin")
    def __init__(self):
        super().__init__("HelloWorldPlugin", "A simple test", "Utilities", "Demos", {"Name": plugin_base.InputArgType.input_string}, {"Example output": plugin_base.OutputArgType.html})
    def execute_plugin(self, input_dict) -> dict:
        return {"Example output:": "Hello World, "  + input_dict["Name"]}


