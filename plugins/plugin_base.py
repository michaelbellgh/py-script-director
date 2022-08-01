from abc import ABC, abstractmethod
from enum import Enum

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InputArgType(Enum):
    input_string = 1
    input_filename = 2

class OutputArgType(Enum):
    download_file = 1
    html = 2


class InputOutputPlugin(ABC):
    '''
    A plugin which has defined input parameters, and defined output parameters. 
    Each input type must be a InputArgType, and each output value a OutputArgType
    '''
    def __init__(self, name: str, description: str, major_group: str, minor_group: str, input_args: dict, output_args: dict, tags: list=[], tenant: str=None):
        self.name = name
        self.description = description
        self.major_group = major_group
        self.minor_group = minor_group
        
        self.valid_input_types = {k:v for (k,v) in input_args.items() if v in InputArgType}
        self.valid_output_types = {k:v for (k,v) in output_args.items() if v in OutputArgType}

        if len(self.valid_input_types) < 1:
            logging.error("No valid input arguments: " + str(input_args)) 
            raise Exception("No valid input arguments: " + str(input_args))
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



