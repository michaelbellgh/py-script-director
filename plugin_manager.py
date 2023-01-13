from flask import Flask, render_template, Blueprint, request, Response
from plugins import plugin_base
import inspect, importlib, logging
import glob, os, multidict



plugin_manager_blueprint = Blueprint('plugin_manager', __name__)
supported_classes = [plugin_base.InputOutputPlugin, plugin_base.InfoPlugin]
loaded_plugins = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@plugin_manager_blueprint.route("/plugins/list", methods=["GET"])
def list_plugins() -> str:
    '''
    Present the user with a list of plugins available
    '''
    if len(loaded_plugins) < 1:
        populate_plugins()
    return render_template("plugin_list.html", plugins=loaded_plugins)

@plugin_manager_blueprint.route("/plugins/populate", methods=["GET"])
def populate_plugins() -> str:
    '''
    Load all available plugins (.py extension) from plugins/*
    Have to change plugins/myplugin.py to plugin.myplugin for importlib to work
    '''
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
    '''
    Pring the name and description of a plugin.
    Needs the query string parameter ?name=<mypluginname> to work
    '''
    if len(loaded_plugins) < 1: 
        populate_plugins()
    if "name" in request.args:
        matched_plugin = None
        for name, plugin in loaded_plugins.items():
            if name.lower() == request.args["name"].lower():
                matched_plugin = plugin
        if matched_plugin is not None:
            return render_template("plugin_info.html", item=matched_plugin, plugin_html=render_input_form(matched_plugin))
        else:
            return Response("Cannot find plugin " + request.args["name"], status=404)
    else:
        return Response("Must specify ?name=PluginName", status=400)

def normalise_ids(input: str) -> str:
    return input.replace(" ", "_") 


def render_input_form(plugin) -> str:
    html = '<form action="/plugins/execute?plugin_name=' + plugin.name + '" method="post" enctype=multipart/form-data>\n'
    if isinstance(plugin, plugin_base.InputOutputPlugin):
        for v in plugin.valid_inputs:
            html += f'<div class="mb-3"><label for="{normalise_ids(v.name)}">{v.name}</label><br>\n'
            if v.type == plugin_base.InputArgType.input_string:
                html += '<input type="text" class="form-control" id="' + normalise_ids(v.name) + '" name="' + v.name + '">\n'
            if v.type == plugin_base.InputArgType.input_number:
                html += '<input type="number" class="form-control" min=0 id="' + normalise_ids(v.name) + '" name="' + v.name + '">\n'
            if v.type == plugin_base.InputArgType.input_checkbox:
                checked = " checked " if v.default == "checked" else ""
                html += '<input type="checkbox" class="form-check-input" ' + checked + 'id="' + normalise_ids(v.name) + '" name="' + v.name + '">\n'
            if v.type == plugin_base.InputArgType.input_filename:
                html += '<input type="file" class="form-control" id="' + normalise_ids(v.name) + '" name="' + v.name + '">\n'
            if v.type == plugin_base.InputArgType.input_textarea:
                html += '<textarea cols="180" rows="50" id="' + normalise_ids(v.name) + '" name="' + v.name + '"></textarea>\n'
            
            html += "</div>"
    
    html += '<input type="submit" class="btn btn-primary" value="Submit">\n</form>'
    return html
            
        

def get_module_plugins(filepath: str):
    '''
    Using importlib and inspect, loads all classes that are listed in supported_classes, from a .py module
    '''
    module = importlib.import_module(filepath)
    if module is None:
        logger.warn("No classes found in " + filepath)
        return None
    classes = inspect.getmembers(module, inspect.isclass)
    if len(classes) <  1:
        logger.warn("No classes found in " + filepath)
        return None
    #inspect.getmembers returns a tuple of (ClassName, ClassObject), so we need to filter the parent classes out against supported_classes
    supported_types = [x for x in classes if x[1].__base__ in supported_classes]
    #Create a default constructor class instance for each supported, found class plugin we have
    instances = {v[0]:v[1]() for v in supported_types}
    return instances

def request_to_dict(plugin: plugin_base.InputOutputPlugin, request):
    converted_dict = {"form_inputs" : multidict.MultiDict(), "files": list()}
    converted_dict["form_inputs"].update(request.form)
    converted_dict["files"] = (request.files)

    return converted_dict

@plugin_manager_blueprint.route("/plugins/execute", methods=["POST", "GET"])
def plugin_execute():
    '''
    Call execute_plugin on each instance we have in loaded_plugins. Syntax: /plugins/execute?plugin_name=MyPluginHere
    Currently, only runs InfoPlugin (no parameters for input)
    '''
    if len(loaded_plugins) < 1:
        populate_plugins()
    if "plugin_name" in request.args:
        matched_plugin = None
        for name, plugin in loaded_plugins.items():
            if name.lower() == request.args["plugin_name"].lower():
                matched_plugin = plugin
        if matched_plugin is not None:
            if isinstance(matched_plugin, plugin_base.InfoPlugin):
                response_dict = matched_plugin.execute_plugin()
                return render_template("plugin_infoplugin.html", response=response_dict)
            if isinstance(matched_plugin, plugin_base.InputOutputPlugin):
                request_params = request_to_dict(matched_plugin, request)
                response = matched_plugin.execute_plugin(request_params)
                #If theres a a download_file in output, we grab the first one and return that
                download_responses = [x for x in response if x.type == plugin_base.OutputArgType.download_file]
                if len(download_responses) > 0:
                    return Response(download_responses[0].value, mimetype="text/plain", headers={"Content-Disposition": "attachment;filename=fmg_proxy_output.txt"}, direct_passthrough=True)
                else: 
                    return render_template("plugin_inputoutput.html", response=response)