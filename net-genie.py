#!/usr/bin/env python

# no-such-anthony
# https://github.com/no-such-anthony/net-genie


from genie.testbed import load

from unicon.core.errors import ConnectionError
import argparse
import sys

from ng_testbeds import get_testbed
from ng_runners import Runner
from ng_task import ng_task
import ng_subtasks

import random


def main(args):

    # load testbed
    if args.testbed:
        # from file
        testbed = load(args.testbed)
    else:
        # from built in code
        testbed = load(get_testbed())
    
    # filter devices
    if args.device:
        # attempt at a basic filter with squeeze
        testbed.squeeze(*args.device, extend_devices_from_links=False)

    # what else could we filter with if we added extra keys to testbed?
    # https://pubhub.devnetcloud.com/media/pyats/docs/topology/schema.html
    # type, alias, role, series, model, platform, region, hardware, peripherals, power, custom
    #
    # hardware and peripherals are whatever you want them to be strings, lists, dicts, etc
    # everything but custom should be there on load if you intend to use them
    #
    # custom is an AttribDict 
    # https://pubhub.devnetcloud.com/media/pyats/docs/datastructures/attrdict.html
    # eg testbed.devices['r1'].custom.fred = 'says hi!'
    #
    # example filter attempt with role
    if args.role:
        f = []
        for device in testbed.devices.values():
            try:
                if device.role in args.role:
                    f.append(device.name)
            except AttributeError:
                pass
        testbed.squeeze(*f, extend_devices_from_links=False)

    # Other filtering options to explore
    # https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/apis/get_devices
    # https://pubhub.devnetcloud.com/media/pyats/docs/utilities/helper_functions.html#find
    #

    #print(testbed.devices.keys())
    #sys.exit()

    # Load multiprocess task runner
    runner = Runner(4)

    # A task array helps to separate the pyats/genie capabilities that I am attempting to make examples for.
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
            ]

    #tasks = tasks[-2:]
            
    output = runner.run(ng_task, name="Run example tasks", testbed=testbed, tasks=tasks)

    # print task results
    print(f"Task = {output['task']}")

    # print results
    for device, task_output in sorted(output['devices'].items()):
        print('='*20,f"Results for {device}",'='*20)
        if 'exception' not in task_output:
            # if no exception we should have a dictionary, so lets try to pretty it up
            for k,v in task_output['result'].items():
                print('-'*len(k))
                print(k)
                print('-'*len(k))
                if 'exception' in v:
                    print('*'*5,f"ERROR")
                print(v['result'])
                print()
        else:
            print('*'*5,f"ERROR")
            if isinstance(task_output['exception'], ConnectionError):
                print("unicon.core.errors.ConnectionError: failed to connect")
            else:
                print(f"{task_output['result']}")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', type=str, nargs='+', required=False)
    parser.add_argument('--role', type=str, nargs='+', required=False)
    parser.add_argument('--testbed', type=str, required=False)
    args = parser.parse_args()

    main(args)
