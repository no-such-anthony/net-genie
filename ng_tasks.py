from unicon.eal.dialogs import Statement, Dialog
from genie.libs.parser.utils.common import ParserNotFound
from genie.metaparser.util.exceptions import SchemaEmptyParserError


def basic_command(device, command):
    output = device.execute(command)
    return output


def dialog_command(device, command, dialog):
    # https://pubhub.devnetcloud.com/media/unicon/docs/user_guide/services/generic_services.html#execute
    output = device.execute(command, reply=dialog)
    return output


def parse_command(device, command):
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


def send_config(device, configuration):
    output = device.configure(configuration)
    return output


def learn_feature(device, feature):
    output = device.learn(feature)
    return output.info


def run_tasks(device, **kwargs):

    # just to show we can use additional kwargs if we wanted to
    tasks = kwargs.pop('tasks', [])

    # will return a dictionary
    ret = {}

    # connect to device
    device.connect(log_stdout=False, learn_hostname=True)

    if 'basic_command' in tasks:
        # send a command
        command = 'show version | inc uptime'
        output = basic_command(device, command)
        ret['send_a_command'] = output

    if 'dialog_command' in tasks:
        # cater to extra dialog/interaction?
        dialog = Dialog([
            Statement(pattern=r'.*Address or name of remote host.*',
                            action='sendline()',
                            loop_continue=True,
                            continue_timer=False),
            Statement(pattern=r'.*Destination filename.*',
                            action='sendline()',
                            loop_continue=True,
                            continue_timer=False)
        ])
        command = 'copy running-config tftp://192.168.204.1'
        output = dialog_command(device, command, dialog)
        ret['command_with_reply_dialog'] = output

    if 'parse_command' in tasks:
        # send a command and parse it
        command = 'show version'
        output = parse_command(device, command)
        ret['parse_a_command'] = output

    if 'send_config' in tasks:
        # send some config
        configuration = ("service timestamps debug datetime msec\n"
                        "service timestamps log datetime msec\n")

        output = send_config(device, configuration)
        ret['send_some_config'] = output

    if 'learn_feature' in tasks:
        # do some learn
        feature = 'bgp'
        if feature:
            output = learn_feature(device, feature)
            ret['learn_a_feature'] = output

    #disconnect from device
    device.disconnect()
    return ret