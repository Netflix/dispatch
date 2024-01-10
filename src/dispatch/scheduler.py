"""
.. module: dispatch.scheduler
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.

.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
.. moduleauthor:: Marc Vilanova <mvilanova@netflix.com>
"""
import logging
import time

from multiprocessing.pool import ThreadPool

import schedule

log = logging.getLogger(__name__)


#  See: https://schedule.readthedocs.io/en/stable/ for documentation on job syntax
class Scheduler:
    """Simple scheduler class that holds all scheduled functions."""

    registered_tasks = []
    running = True

    def __init__(self, num_workers=100):
        self.pool = ThreadPool(processes=num_workers)

    def add(self, job, *args, **kwargs):
        """Adds a task to the scheduler."""

        def decorator(func):
            if not kwargs.get("name"):
                name = func.__name__
            else:
                name = kwargs.pop("name")

            self.registered_tasks.append(
                {"name": name, "func": func, "job": job.do(self.pool.apply_async, func)}
            )

        return decorator

    def remove(self, task):
        """Removes a task from the scheduler."""
        schedule.cancel_job(task["job"])

    def start(self):
        """Runs all scheduled tasks."""
        log.info("Starting scheduler...")

        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def stop(self):
        """Stops the scheduler (letting existing threads finish)."""
        log.debug("Stopping scheduler...")
        self.pool.close()
        self.running = False


scheduler = Scheduler()


def stop_scheduler(signum, frame):
    scheduler.stop()
