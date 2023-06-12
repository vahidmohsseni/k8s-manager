from threading import Lock


class Task:
    def __init__(self, name, args_to_run, return_type) -> None:
        self.name = name
        self.args_to_run = args_to_run
        self.status = "created"
        self.return_type = return_type
        self.assigned_to = None
        self.lock = Lock()
        self.return_value = None

    def change_status(self, status, return_value=None):
        """
        Accepted Values: created, scheduled, running, finished, failed, deleted
        created: task is created but not scheduled
        scheduled: task is scheduled but not running
        running: task is running
        finished: task is finished
        failed: task is failed
        deleted: task is deleted
        stopeed: task is stopped
        """
        self.status = status
        if return_value is not None:
            self.return_value = return_value

    def set_assigned_node(self, node_name):
        self.assigned_to = node_name
