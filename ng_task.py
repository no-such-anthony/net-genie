# The primary task

#task_wrapper comes in handy if you are doing subtasks
from ng_runners import task_wrapper


def ng_task(device, **kwargs):

    # pop out the task list from kwargs
    tasks = kwargs.pop('tasks', [])

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
