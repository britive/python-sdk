from .notifications import Notifications
from .task_services import TaskServices
from .tasks import Tasks


class Workflows:
    def __init__(self, britive) -> None:
        self.notifications = Notifications(britive)
        self.task_services = TaskServices(britive)
        self.tasks = Tasks(britive)
