# schema
# https://pubhub.devnetcloud.com/media/pyats/docs/topology/schema.html
# connection credentials
# https://pubhub.devnetcloud.com/media/unicon/docs/user_guide/connection.html#unicon-credentials
# creation
# https://pubhub.devnetcloud.com/media/pyats/docs/topology/creation.html


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
    #'%CALLABLE{path.to.callable(param1,param2,param3)}'
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