from flask import render_template, Blueprint, request, Response
import requests
from plugins import plugin_base
import inspect, importlib, logging
import glob, os



plugin_manager_blueprint = Blueprint('plugin_manager', __name__)
supported_classes = [plugin_base.InputOutputPlugin, plugin_base.InfoPlugin]
loaded_plugins = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@plugin_manager_blueprint.route("/plugins/list", methods=["GET"])
def list_plugins() -> str:
    if len(loaded_plugins) < 1:
        populate_plugins()
    return render_template("plugin_list.html", plugins=loaded_plugins)

@plugin_manager_blueprint.route("/plugins/populate", methods=["GET"])
def populate_plugins() -> str:
    global loaded_plugins
    loaded_plugins = {}
    potential_plugins = glob.glob("plugins" + os.path.sep + "*.py")
    for filepath in [x.replace(os.path.sep, ".") for x in potential_plugins]:
        new_plugins = get_module_plugins(filepath.removesuffix(".py"))
        if len(new_plugins) > 0:
            loaded_plugins.update(new_plugins)
    return str(loaded_plugins)


@plugin_manager_blueprint.route("/plugins/info", methods=["GET"])
def plugin_info():
    if len(loaded_plugins) < 1: 
        populate_plugins()
    if "name" in request.args:
        matched_plugin = None
        for name, plugin in loaded_plugins.items():
            if name.lower() == request.args["name"].lower():
                matched_plugin = plugin
        if matched_plugin is not None:
            return render_template("plugin_info.html", item=matched_plugin)
        else:
            return Response("Cannot find plugin " + request.args["name"], status=404)
    else:
        return Response("Must specify ?name=PluginName", status=400)
    


def get_module_plugins(filepath: str):
    module = importlib.import_module(filepath)
    if module is None:
        logger.warn("No classes found in " + filepath)
        return None
    classes = inspect.getmembers(module, inspect.isclass)
    if len(classes) <1:
        logger.warn("No classes found in " + filepath)
        return None
    supported_types = [x for x in classes if x[1].__base__ in supported_classes]
    instances = {v[0]:v[1]() for v in supported_types}
    return instances

@plugin_manager_blueprint.route("/plugins/execute", methods=["POST", "GET"])
def plugin_execute():
    if len(loaded_plugins) < 1:
        populate_plugins()
    if "name" in request.args:
        matched_plugin = None
        for name, plugin in loaded_plugins.items():
            if name.lower() == request.args["name"].lower():
                matched_plugin = plugin
        if matched_plugin is not None:
            response_dict = matched_plugin.execute_plugin()
            if isinstance(matched_plugin, plugin_base.InfoPlugin):
                return render_template("plugin_infoplugin.html", response=response_dict)
