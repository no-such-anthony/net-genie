#!/usr/bin/env python

# no-such-anthony
# https://github.com/no-such-anthony/net-genie


from genie.testbed import load
from genie.utils.diff import Diff
from genie.utils import Dq
from unicon.core.errors import ConnectionError
import argparse
import sys

from ng_testbeds import get_testbed
from ng_runners import Runner
import ng_tasks
#from ng_tasks import run_tasks


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--device', type=str, nargs='+', required=False)
    parser.add_argument('--role', type=str, nargs='+', required=False)
    parser.add_argument('--testbed', type=str, required=False)
    args = parser.parse_args()

    if args.testbed:
        # load testbed from file
        testbed = load(args.testbed)
    else:
        # load testbed built in code
        testbed = load(get_testbed())
        
    if args.device:
        # attempt at a basic filter
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

    # Other filtering options I need to explore
    # https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/apis/get_devices
    # https://pubhub.devnetcloud.com/media/pyats/docs/utilities/helper_functions.html#find
    #

    #print(testbed.devices.keys())
    #sys.exit()

    runner = Runner(4)

    tasks = [
            {
             'name': 'basic_command',
             'function': ng_tasks.basic_command,
             'kwargs': { 'command' : 'show version | inc uptime'}
            },
            {
             'name': 'dialog_command',
             'function': ng_tasks.dialog_command,
             'kwargs': { 
                        'command' : 'copy running-config tftp://192.168.204.1',
                        'dialog_helper': 'copy_tftp'
                       }
            },
            {
             'name': 'parse_command',
             'function': ng_tasks.parse_command,
             'kwargs': { 'command' : 'show version' }
            },
            {
             'name': 'send_config',
             'function': ng_tasks.send_config,
             'kwargs': { 
                      'configuration' : ("service timestamps debug datetime msec\n"
                                         "service timestamps log datetime msec\n") 
                     }
            },
            {
             'name': 'learn_feature',
             'function': ng_tasks.learn_feature,
             'kwargs':  { 'feature' : 'bgp' }
            },
            ]
            
    results = runner.run(ng_tasks.run_tasks, name="A Test Task", testbed=testbed, tasks=tasks)

    # print task results
    print(f"Task = {results['task']}")

    # print results
    for device, result in sorted(results['devices'].items()):
        print('='*20,f"Results for {device}",'='*20)
        if 'exception' not in result:
            # if no exception we should have a dictionary, so lets try to pretty it up
            for k,v in result['result'].items():
                print('-'*len(k))
                print(k)
                print('-'*len(k))
                print(v)
                print()
        else:
            print('*'*5,f"ERROR")
            if isinstance(result['exception'], ConnectionError):
                print("unicon.core.errors.ConnectionError: failed to connect")
            else:
                print(f"{result['result']}")
    print()


if __name__ == "__main__":
    main()
