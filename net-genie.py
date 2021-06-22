#!/usr/bin/env python

# no-such-anthony
# https://github.com/no-such-anthony/net-genie


from genie.testbed import load

import argparse
import sys

from ng_testbeds import get_testbed
from ng_runners import Runner
from ng_task import ng_task


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

    # You can also send additional arguments which will be passed to the task        
    output = runner.run(ng_task, name="Run example tasks", testbed=testbed)

    # Print task results
    print(f"Task = {output['task']}")
    
    for device, task_output in sorted(output['devices'].items()):
        print('='*20,f"Results for {device}",'='*20)
        if 'exception' not in task_output:
            # if no exception in main loop we should have a dictionary
            for k,v in task_output['result'].items():
                print('-'*len(k))
                print(k)
                print('-'*len(k))
                print(v['result'])
                print()
        else:
            print(task_output['result'])
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', type=str, nargs='+', required=False)
    parser.add_argument('--role', type=str, nargs='+', required=False)
    parser.add_argument('--testbed', type=str, required=False)
    args = parser.parse_args()

    main(args)
