# -*- coding: utf-8 -*-
# @Time    : 2024/1/31 10:51
# @File    : task.py
from datetime import datetime


class Task:
    # 任务 由name，index, description，status，priority，deadline，created_at组成
    __slots__ = ('_name', '_status', '_priority', '_deadline', '_created_at')

    def __init__(self, name, priority, deadline, created_at):
        self._name = name
        self._status = 'unfinished'
        self._priority = priority
        self._deadline = deadline
        self._created_at = created_at

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status

    def is_finished(self):
        return self._status == 'finished'

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, value):
        if value.lower() in ['high', 'low']:
            self._priority = value.lower()
        else:
            raise ValueError("Priority must be 'high' or 'low'")

    @property
    def deadline(self):
        return self._deadline

    @deadline.setter
    def deadline(self, deadline):
        self._deadline = deadline

    def is_overdue(self):
        # ddl_str = datetime.strftime(self._deadline, "%Y-%m-%d")
        now = datetime.now()

        ddl = datetime.strptime(self._deadline, "%Y-%m-%d")

        return now > ddl

    def check_time(self):
        if self.is_overdue():
            return 'task overdue'
        else:
            rest_time = datetime.strptime(self._deadline, "%Y-%m-%d") - datetime.now()
            if rest_time.days == 0 and rest_time.seconds < 60:
                return f'Task {self._name} will be finished in %s seconds' % rest_time.seconds
            elif rest_time.days == 0 and rest_time.seconds >= 60:
                return f'Task {self._name} will be finished in %s minutes' % (rest_time.seconds // 60)
            elif rest_time.days > 0:
                return f'Task {self._name} will be finished in %s days' % rest_time.days

    @property
    def created_at(self):
        return self._created_at

    @created_at.setter
    def created_at(self, created_at):
        self._created_at = created_at

    def __str__(self):
        return 'name:%s status:%s priority:%s deadline:%s created_at:%s' % \
               (self._name, self._status, self._priority, self._deadline, self._created_at)

    def __repr__(self):
        return self.__str__()

