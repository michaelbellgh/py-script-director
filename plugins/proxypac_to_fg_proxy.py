import re, argparse
from . import plugin_base
from jinja2 import Template

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_proxy_pac_entries(proxy_pac_contents) -> dict:
    content = str(proxy_pac_contents.read())
    shell_expression_matches = re.findall('shExpMatch\([\\s]?host[\\s]?,[\\s]?["\']([^\'"]*)[\'"][\\s]?\)', content)
    domain_matches = re.findall('dnsDomainIs\([\\s]?host[\\s]?,[\\s]?["\']([^\'"]*)[\'"][\\s]?\)', content)

    return [x.strip() for x in (shell_expression_matches + domain_matches)]



def remove_suffix(input_string: str, suffix: str) -> str:
    '''Python <= 3.8 support'''
    if input_string.endswith(suffix):
        return input_string[input_string[:-len(suffix)]]
    else:
        return input_string

def create_policy_package_cli_config(entries: list, url_policy_name: str, action: str="monitor", existing_list_id: int=0) -> str:
    output = "config webfilter urlfilter\n\tedit " + str(existing_list_id) + "\n" + ("\t" * 2) + "set name \"" + url_policy_name + "\"\n" + ("\t" * 2) + "config entries"

    position = 1
    for entry in entries:
        url_type, url_action, url = "","",""
        if "*" in entry:
            #Its a wildcard entry
            url_type = "wildcard"
        else: 
            url_type = "simple"

        output += "\n" + ("\t" * 3) + "edit " + str(position) + "\n" + ("\t" * 4)
        output += "set url \"" + entry + "\"\n" + ("\t" * 4)
        output += "set type " + url_type + "\n" + ("\t" * 4)
        output += "set action " + action + "\n" + ("\t" * 3) + "next"
        position += 1
    
    output += "\n" + ("\t" * 3) + "edit " + str(position) + "\n" + ("\t" * 4) + "set url \"*.*\"\n" + ("\t" * 4) + "set type wildcard\n" + ("\t" * 4) + "set action block\n" + ("\t" * 3) + "next\n" + ("\t" * 2) + "end\n\tnext\nend"
    
    
    return output

def create_proxy_address_group(entries: list, proxy_address_group_name: str) -> str:

    script_output = ""

    address_template = """
config firewall proxy-address
edit "{{ name }}"
    set type host-regex
    set host-regex "{{ host_regex }}"
next
end
"""
    names = []

    for entry in entries:
        name = ("url_" + entry.replace("*.", ""))[:35]
        names.append(name)
        host_regex = "^" + remove_suffix(entry.replace(".", "\.").replace("*", ".+").strip(), "/") + "$"

        rendered_address = Template(address_template).render(name=name, host_regex=host_regex)

        script_output += rendered_address

    group_template = """
config firewall proxy-addrgrp
edit "{{ name }}"
    set type dst
    set member {{ names }}
next
end

"""
    list_names = " ".join(names)

    template = Template(group_template)
    script_output += template.render(name=proxy_address_group_name, names=list_names)

    return script_output





    





def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-file", default="output.txt", help="Output file for FortiGate/Manager script")
    parser.add_argument("--action", default="monitor")
    parser.add_argument("--proxy-address-group", action="store_true")
    parser.add_argument("--proxy-group-name", default=None)
    parser.add_argument("--proxy-addresses-file", default=None)
    parser.add_argument("--list-id", default=0)
    parser.add_argument("--is-proxy-pac", action="store_true", help="Specifies that the the proxy-addresses-file argument is a proxy.pac file")

    args = parser.parse_args()

    output_file = open(args.output_file, "w")
    contents = ""

    addresses = []
    if args.is_proxy_pac:
        addresses = get_proxy_pac_entries(args.proxy_addresses_file)
    elif args.proxy_address_group and args.proxy_group_name is not None and args.proxy_addresses_file is not None:
        addresses = [x.strip() for x in open(args.proxy_addresses_file).readlines()]
    
    contents = create_proxy_address_group(addresses, args.proxy_group_name)
    output_file.write(contents)

    #Old method
    #output_file.write(create_policy_package_cli_config(contents, args.url_filter_name, args.action, args.list_id))


class ProxyPACToFG(plugin_base.InputOutputPlugin):
    '''
    '''
    def plugin_setup(self):
        logger.info("ProxyPACtoFG Plugin")
    def __init__(self):
        super().__init__("ProxyPACtoFG", "Takes a proxy.pac file or line separated hostnames and converts to a proxy address group for use in FortiGates/FortiManager", "Utilities", "Fortinet",
             input_args=[plugin_base.InputArgParameter("Proxy Group Name", "MyGroup", plugin_base.InputArgType.input_string),
              plugin_base.InputArgParameter("Action", "monitor", plugin_base.InputArgType.input_string),
              plugin_base.InputArgParameter("List ID", "0", plugin_base.InputArgType.input_number),
              plugin_base.InputArgParameter("Is Proxy PAC", "", plugin_base.InputArgType.input_checkbox),
              plugin_base.InputArgParameter("Proxy.pac file", "", plugin_base.InputArgType.input_filename),
              plugin_base.InputArgParameter("Domains", "", plugin_base.InputArgType.input_textarea)
              ],
             output_args=[plugin_base.OutputArgParameter("CLI", "", plugin_base.OutputArgType.download_file)])
    def execute_plugin(self, input_dict) -> dict:
        if "Is Proxy PAC" in input_dict["form_inputs"] and input_dict["form_inputs"]["Is Proxy PAC"] == "on" and len(input_dict["files"]) > 0:
            addresses = get_proxy_pac_entries(input_dict["files"]["Proxy.pac file"])
            content = create_proxy_address_group(addresses, input_dict["form_inputs"]["Proxy Group Name"])
            return [plugin_base.OutputArgObject("CLI", plugin_base.OutputArgType.download_file, content)]
        else:
            addresses = [x.strip() for x in input_dict["form_inputs"]["Domains"].splitlines()]
            content = create_proxy_address_group(addresses, input_dict["form_inputs"]["Proxy Group Name"])
            return [plugin_base.OutputArgObject("CLI", plugin_base.OutputArgType.download_file, content)]