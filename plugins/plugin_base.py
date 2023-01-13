from abc import ABC, abstractmethod
from enum import Enum

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InputArgType(Enum):
    input_string = 1
    input_filename = 2
    input_number = 3
    input_checkbox = 4
    input_textarea = 5

class InputArgParameter():
    def __init__(self, name: str, default, type: InputArgType) -> None:
        self.name = name
        self.default = default
        self.type = type

class OutputArgParameter():
    def __init__(self, name: str, default, type: InputArgType) -> None:
        self.name = name
        self.default = default
        self.type = type

class OutputArgType(Enum):
    download_file = 1
    html = 2

class OutputArgObject():
    def __init__(self, name: str, type: OutputArgType, value, metaname: str=""):
        self.name = name
        self.type = type
        self.value = value
        self.metaname = metaname

class BasePlugin(ABC):
    def __init__(self, name: str, description: str, major_group: str, minor_group: str, input_args: list, output_args: dict, plugin_type: type, tags: list=[], tenant: str=None):
        self.name = name
        self.description = description
        self.major_group = major_group
        self.minor_group = minor_group
        self.tags = [x for x in tags if isinstance(x, str)]
        self.tenant = tenant if isinstance(tenant, str) else None
        self.plugin_type = type(self)

class InputOutputPlugin(BasePlugin, ABC):
    '''
    A plugin which has defined input parameters, and defined output parameters. 
    Each input type must be a InputArgType, and each output value a OutputArgType
    '''
    def __init__(self, name: str, description: str, major_group: str, minor_group: str, input_args: list, output_args: dict, tags: list=[], tenant: str=None):
        self.name = name
        self.description = description
        self.major_group = major_group
        self.minor_group = minor_group
        
        self.valid_inputs = [x for x in input_args if isinstance(x, InputArgParameter)]
        self.valid_outputs = [x for x in output_args if isinstance(x, OutputArgParameter)]

        if len(self.valid_inputs) < 1:
            logging.error("No valid input arguments: " + str(input_args)) 
            raise Exception("No valid input arguments: " + str(input_args))
        if len(self.valid_outputs) < 1:
            logging.error("No valid output types: " + str(output_args)) 
            raise Exception("No valid output types: " + str(output_args))

        self.tags = [x for x in tags if isinstance(x, str)]
        self.tenant = tenant if isinstance(tenant, str) else None

    @abstractmethod
    def plugin_setup(self):
        ...
    
    @abstractmethod
    def execute_plugin(self, input_dict: dict) -> dict:
        ...



class InfoPlugin(ABC):
    '''
    A simple, no input parameter plugin type.
    Output args are strictly defined
    '''
    def __init__(self, name: str, description: str, major_group: str, minor_group: str, output_args: dict, tags: list=[], tenant: str=None):
        self.name = name
        self.description = description
        self.major_group = major_group
        self.minor_group = minor_group
        
        self.valid_output_types = {k:v for (k,v) in output_args.items() if v in OutputArgType}

        if len(self.valid_output_types) < 1:
            logging.error("No valid output types: " + str(output_args)) 
            raise Exception("No valid output types: " + str(output_args))

        self.tags = [x for x in tags if isinstance(x, str)]
        self.tenant = tenant if isinstance(tenant, str) else None

    @abstractmethod
    def plugin_setup(self):
        ...

    @abstractmethod
    def execute_plugin(self) -> dict:
        ...



