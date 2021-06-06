from unicon.eal.dialogs import Statement, Dialog
from genie.libs.parser.utils.common import ParserNotFound
from genie.metaparser.util.exceptions import SchemaEmptyParserError


def basic_command(device, command=None):
    # device.execute runs command, gathers raw output, and returns as string

    if command:
        output = device.execute(command)
    else:
        output = 'No command to run.'

    return output


def dialog_command(device, command=None, dialog_helper=None):
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


def parse_command(device, command=None):
    # send a command and parse it

    if command:
        try: 
            output = device.parse(command)
            return {"type": "parsed", "output": output}
        except ParserNotFound: 
            print(f"  Error: pyATS lacks a parser for device {device.name} with os {device.os}. Gathering raw output to return.")
        except SchemaEmptyParserError: 
            print(f"  Error: No valid data found from output from device {device.name}. Gathering raw output to return.")

        # device.execute runs command, gathers raw output, and returns as string
        output = device.execute(command)
        return {"type": "raw", "output": output}
        
    else:
        return 'No command to run.'

    
def send_config(device, configuration=None):

    if configuration:
        output = device.configure(configuration)
    else:
        output = "No configuration to send."
    return output


def learn_feature(device, feature=None):

    if feature:
        output = device.learn(feature)
        return output.info
    else:
        output = 'No feature to gather.'
        return output


def run_tasks(device, **kwargs):

    # just to show we can use additional kwargs if we wanted to
    tasks = kwargs.pop('tasks', [])

    # will return a dictionary
    ret = {}

    # connect to device
    device.connect(log_stdout=False, learn_hostname=True)

    for task in tasks:
        ret[task['name']] = task['function'](device, **task['kwargs'])


    #disconnect from device
    device.disconnect()
    return ret