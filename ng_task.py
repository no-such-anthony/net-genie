import ng_subtasks
import random

#task_wrapper comes in handy for handling subtasks
from ng_runners import task_wrapper


# A task list helps to separate the pyats/genie capabilities that I am attempting to make examples for.
# With the side effect that it kind of looks like an ansible playbook...
tasks = [
        {
            'name': 'basic_command',
            'function': ng_subtasks.basic_command,
            'kwargs': { 'command' : 'show version | inc uptime'}
        },
        {
            'name': 'dialog_command',
            'function': ng_subtasks.dialog_command,
            'kwargs': { 
                    'command' : 'copy running-config tftp://192.168.204.1',
                    'dialog_helper': 'copy_tftp'
                    }
        },
        {
            'name': 'parse_command',
            'function': ng_subtasks.parse_command,
            'kwargs': { 'command' : 'show version' }
        },
        {
            'name': 'send_config',
            'function': ng_subtasks.send_config,
            'kwargs': { 
                    'configuration' : ("service timestamps debug datetime msec\n"
                                        "service timestamps log datetime msec\n") 
                    }
        },
        {
            'name': 'learn_feature',
            'function': ng_subtasks.learn_feature,
            'kwargs':  { 'feature' : 'bgp' }
        },
        {
            'name': 'configure_diff',
            'function': ng_subtasks.configure_diff,
            'kwargs':  { 'configuration':  (f"interface lo100\n"
                                            f"description random={random.randrange(100, 1000, 3)}\n")
                    }
        },
        {
            'name': 'ping_ips',
            'function': ng_subtasks.ping_ips,
            'kwargs':  { 'ips':  ['10.0.12.1','10.0.12.2','10.0.1.1'],
                       }
        },
        ]

#tasks = tasks[-1:]


# The primary task
def ng_task(device, **kwargs):

    # pop out any additional kwargs you may have passed
    #example = kwargs.pop('example', [])

    # will return a dictionary
    output = {}

    # connect to device
    device.connect(log_stdout=False, learn_hostname=True)

    for task in tasks:
        # inject ret as run_dict in case you wanted to use the output from previous subtasks.
        # kind of like ansible register but automatic and accessible in subtasks functions with
        # run_dict = kwargs.pop('run_dict', {})
        # basic_command = run_dict.get('basic_command', {})
        # where basic_command is also a dict with result as a key
        task['kwargs']['run_dict'] = output

        # run subtask
        output[task['name']] = task_wrapper(task=task['function'], device=device, **task['kwargs'])

        # subtasks may return an 'exception', as we are using task_wrapper,
        # or you could add a 'failure' key in the return output
        # you could choose to break out of this task loop here
        # instead of continuing through the remaining subtasks


    #disconnect from device
    device.disconnect()
    return output
