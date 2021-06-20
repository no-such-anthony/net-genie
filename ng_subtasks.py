from unicon.eal.dialogs import Statement, Dialog
from genie.libs.parser.utils.common import ParserNotFound
from genie.metaparser.util.exceptions import SchemaEmptyParserError
from genie.libs.sdk.apis.utils import compare_config_dicts
from genie.utils.diff import Diff
from genie.utils import Dq
from unicon.core.errors import SubCommandFailure
import re


def basic_command(device, command=None, **kwargs):
    # device.execute runs command, gathers raw output, and returns as string

    if command:
        output = device.execute(command)
    else:
        output = 'No command to run.'

    return output


def dialog_command(device, command=None, dialog_helper=None, **kwargs):
    # https://pubhub.devnetcloud.com/media/unicon/docs/user_guide/services/generic_services.html#execute


    dialog = { 'copy_tftp': Dialog([
                                    Statement(pattern=r'.*Address or name of remote host.*',
                                                    action='sendline()',
                                                    loop_continue=True,
                                                    continue_timer=False),
                                    Statement(pattern=r'.*Destination filename.*',
                                                    action='sendline()',
                                                    loop_continue=True,
                                                    continue_timer=False)
                                    ])
            }

    if command and dialog_helper:
        output = device.execute(command, reply=dialog[dialog_helper])
    else:
        output = 'You need send both a command and its dialog_helper'

    return output


def parse_command(device, command=None, **kwargs):
    # send a command and parse it

    if command:
        try: 
            output = device.parse(command)
            return {"type": "parsed", "output": output}
        except ParserNotFound: 
            print(f"  Error: pyATS lacks a parser for device {device.name} with os {device.os}. Gathering raw output of '{command}' to return.")
        except SchemaEmptyParserError: 
            print(f"  Error: No valid data found from output from device {device.name}. Gathering raw output of '{command}' to return.")

        # device.execute runs command, gathers raw output, and returns as string
        output = device.execute(command)
        return {"type": "raw", "output": output}
        
    else:
        return 'No command to run.'

    
def send_config(device, configuration=None, **kwargs):

    if configuration:
        output = device.configure(configuration)
    else:
        output = "No configuration to send."
    return output


def learn_feature(device, feature=None, **kwargs):

    if feature:
        output = device.learn(feature)
        return output.info
    else:
        output = 'No feature to gather.'
        return output


def configure_diff(device, configuration=None, **kwargs):

    if configuration:
        # get running config as dict
        config_pre = device.api.get_running_config_dict()

        # deploy
        device.configure(configuration)

        # get running config as dict
        config_post = device.api.get_running_config_dict()

        # diff
        diff = compare_config_dicts(config_pre, config_post)

        # as diff is built from a dict diff you may want to tidy up and remove the trailing : from each line
        output = re.sub(r":$", "", str(diff), flags=re.M)
    else:
        output = 'You need a configuration to deploy for this example.'

    return output


def ping_ips(device, ips=[], **kwargs):

    output = ''
    for ip in ips:
        prefix = 'Success'
        try:
            ping_result = device.ping(ip)
        except SubCommandFailure as e:
            prefix = 'Failed'
            if ['Success rate is 0 percent'] in e.args:
                ping_result = e.args[-1]
            else:
                ping_result = e

        output += f'{ip}: {prefix}\n{ping_result}\n'
        
    return output
