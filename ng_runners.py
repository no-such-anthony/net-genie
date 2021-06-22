from pyats.async_ import pcall
import unicon.core.errors as unicon_err
import traceback


def get_original_exception(e):
    last_exception = e
    while last_exception.__cause__:
        last_exception = last_exception.__cause__
    return last_exception

    
def task_wrapper(**kwargs):

    task = kwargs.pop('task', None)
    device = kwargs.pop('device', None)
    result = {}
    result['device'] = device.name

    try:
        result['result'] = task(device, **kwargs)

    except unicon_err.ConnectionError as e:
        reason = get_original_exception(e)
        if isinstance(reason, unicon_err.TimeoutError):
            result['exception'] = e
            result['result'] = "Timed out connecting to device."
        else:
            result['exception'] = e
            result['result'] =  traceback.format_exc()

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
        # if you have a lot of devices in your task you could have a progress bar with updates per chunk?
        chunks = self.chunker(list(testbed.devices.keys()))
        for chunk in chunks:
            chunk_result = pcall(task_wrapper, device=(testbed.devices[device] for device in chunk), ckwargs=kwargs)
            for worker_result in chunk_result:
                results['devices'][worker_result['device']] = worker_result

        return results