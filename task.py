import time

class Task():
    start_time = 0
    RETRY_INTERVAL = 2

    class TaskTimeoutError(Exception):
        pass
    class TaskError(Exception):
        pass

    def __init__(self):
        self.start()
 
    def start(self):
        self.start_time = time.time()

    def sleep(self, retry_interval):
        time.sleep(retry_interval)

    def wait(self, taskid, timeout=(4*RETRY_INTERVAL), retry_interval=RETRY_INTERVAL):
        if time.time() > (self.start_time + timeout):
            raise self.TaskTimeoutError("Task %s timeout." % (taskid))
        print("Task=%s sleep." % (taskid))
        self.sleep(retry_interval)