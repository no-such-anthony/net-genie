#!/usr/bin/env python

# no-such-anthony
# https://github.com/no-such-anthony/net-genie

from pyats.async_ import pcall
from genie.testbed import load
from genie.utils.diff import Diff
from genie.utils import Dq
from unicon.eal.dialogs import Statement, Dialog
from unicon.core.errors import ConnectionError
import argparse
import traceback
import sys


def get_testbed():

    devices = ['r1','r2','r3','r4']

    testbed = {}
    testbed['testbed'] = {}
    testbed['testbed']['name'] = 'dev'
    testbed['testbed']['credentials'] = {}
    testbed['testbed']['credentials']['default'] = {}
    testbed['testbed']['credentials']['default']['username'] = "fred"
    testbed['testbed']['credentials']['default']['password'] = "bedrock"
    #'%ASK{}'
    #'%ENV{GENIE_USERNAME}'
    testbed['devices'] = {}

    for device in devices:
        d = {}
        d['connections'] = {}
        d['connections']['cli'] = {}
        d['connections']['cli']['ip'] = device
        d['connections']['cli']['port'] = 22
        d['connections']['cli']['protocol'] = 'ssh'
        d['os'] = 'ios'
        d['type'] = 'dev'
        testbed['devices'][device] = d

    # assign a role to filter with
    testbed['devices']['r1']['role'] = 'test-role'

    return testbed


def task_wrapper(**kwargs):

    task = kwargs.pop('task', None)
    device = kwargs.pop('device', None)
    result = {}
    result['device'] = device.name

    try:
        result['result'] = task(device, **kwargs)

    except Exception as e:
        result['exception'] = e
        result['result'] = traceback.format_exc()

    return result


class Runner(object):

    def __init__(self, num_workers: int = 20) -> None:
        self.num_workers = num_workers

    def chunker(self, seq):
        size = self.num_workers
        return (seq[pos:pos + size] for pos in range(0, len(seq), size))

    def run(self, task, name = None, testbed = None, **kwargs):

        # inject positional argument 'task' into kwargs for use in pcall
        kwargs['task'] = task
        results = {}
        results['task'] = name or task.__name__
        results['devices'] = {}

        # https://pubhub.devnetcloud.com/media/pyats/docs/async/pcall.html
        # pcall has no pool size
        # get device chunks the size of num_workers
        chunks = self.chunker(list(testbed.devices.keys()))
        for chunk in chunks:
            chunk_result = pcall(task_wrapper, device=(testbed.devices[device] for device in chunk), ckwargs=kwargs)
            for worker_result in chunk_result:
                results['devices'][worker_result['device']] = worker_result

        return results


def run_command(device, **kwargs):

    # just to show we can use additional kwargs if we wanted to
    feature = kwargs.pop('feature', None)

    # will return a dictionary
    ret = {}

    device.connect(log_stdout=False, learn_hostname=True)

    # send a command
    output = device.execute('show version | inc uptime')
    ret['send_a_command'] = output

    # send a command and parse it
    output = device.parse('show version')
    ret['parse_a_command'] = output

    # send some config
    configuration = ("service timestamps debug datetime msec\n"
                     "service timestamps log datetime msec\n")
    output = device.configure(configuration)
    ret['send_some_config'] = output

    # do some learn
    if feature:
        output = device.learn(feature)
        ret['learn_a_feature'] = output.info

    # cater to extra dialog/interaction?
    # https://pubhub.devnetcloud.com/media/unicon/docs/user_guide/services/generic_services.html#execute
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

    output = device.execute('copy running-config tftp://192.168.204.1', reply=dialog)
    ret['command_with_reply_dialog'] = output
    
    device.disconnect()
    return ret


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
    # type, alias, role, series, model, platform, region, hardware, peripherals, power
    #
    # example attempt with role
    # is squeeze the best way to do this?
    # alternatively we could pass the information to the task and filter there?
    if args.role:
        f = []
        for device in testbed.devices.values():
            try:
                if device.role in args.role:
                    f.append(device.name)
            except AttributeError:
                pass
        testbed.squeeze(*f, extend_devices_from_links=False)

    #print(testbed.devices.keys())
    #sys.exit()

    runner = Runner(4)
    # feature='bgp' is being used to verify kwargs functionality
    # name= is optional
    results = runner.run(run_command, name="A Test Task", testbed=testbed, feature='bgp')

    # print task results
    print(f"Task = {results['task']}")

    # print results that didn't raise exception
    for device, result in sorted(results['devices'].items()):
        if 'exception' not in result:
            print('='*20,f"Results for {device}",'='*20)
            # if no exception we should have a dictionary, so lets try to pretty it up
            for k,v in result['result'].items():
                print('-'*len(k))
                print(k)
                print('-'*len(k))
                print(v)
                print()

    # print results that did raise exception
    for device, result in sorted(results['devices'].items()):
        if 'exception' in result:
            print('='*20,f"{device} error message",'='*20)
            if isinstance(result['exception'], ConnectionError):
                print("unicon.core.errors.ConnectionError: failed to connect")
            else:
                print(f"{result['result']}")
    print()


if __name__ == "__main__":
    main()