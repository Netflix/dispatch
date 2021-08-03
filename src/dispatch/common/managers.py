"""
.. module: dispatch.common.managers
    :platform: Unix
    :copyright: (c) 2019 by Netflix Inc., see AUTHORS for more
    :license: Apache, see LICENSE for more details.

.. moduleauthor:: Kevin Glisson <kglisson@netflix.com>
"""
import logging
from dispatch.exceptions import InvalidConfigurationError

logger = logging.getLogger(__name__)


# inspired by https://github.com/getsentry/sentry
class InstanceManager(object):
    def __init__(self, class_list=None, instances=True):
        if class_list is None:
            class_list = []
        self.instances = instances
        self.update(class_list)

    def get_class_list(self):
        return self.class_list

    def add(self, class_path):
        self.cache = None
        if class_path not in self.class_list:
            self.class_list.append(class_path)

    def remove(self, class_path):
        self.cache = None
        self.class_list.remove(class_path)

    def update(self, class_list):
        """
        Updates the class list and wipes the cache.
        """
        self.cache = None
        self.class_list = class_list

    def all(self):
        """
        Returns a list of cached instances.
        """
        class_list = list(self.get_class_list())
        if not class_list:
            self.cache = []
            return []

        if self.cache is not None:
            return self.cache

        results = []
        for cls_path in class_list:
            module_name, class_name = cls_path.rsplit(".", 1)
            try:
                module = __import__(module_name, {}, {}, class_name)
                cls = getattr(module, class_name)
                if self.instances:
                    results.append(cls())
                else:
                    results.append(cls)

            except InvalidConfigurationError as e:
                logger.warning(f"Plugin '{class_name}' may not work correctly. {e}")

            except Exception as e:
                logger.exception(f"Unable to import {cls_path}. Reason: {e}")
                continue

        self.cache = results

        return results
