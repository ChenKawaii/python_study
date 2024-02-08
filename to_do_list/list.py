# -*- coding: utf-8 -*-
# @Time    : 2024/1/31 11:02
# @File    : list.py
from task import Task
import re
from datetime import datetime


class List:
    __slots__ = ('_name', '_tasks', '_task_index')

    def __init__(self, name):
        self._name = name
        self._tasks = {}
        self._task_index = 0

    def load_task(self, task: Task):
        if isinstance(task, Task):
            self._task_index += 1
            self._tasks[self._task_index] = task
            return True
        return False

    def add_task(self):
        name = input('请输入任务名称：')
        priority = input('请输入任务优先级：')
        deadline_pattern = r"\d{4}-\d{2}-\d{2}"
        while True:
            deadline = input('请输入任务截止日期（格式：YYYY-MM-DD）：')
            if re.match(deadline_pattern, deadline):
                # 检验输入日期是否是未来的时间
                current_date = datetime.now().strftime("%Y-%m-%d")
                if deadline >= current_date:
                    break
                else:
                    print("截止日期应为未来的时间，请重新输入。")
            else:
                print("日期格式错误，请重新输入。")

        created_at = datetime.now().strftime("%Y-%m-%d")

        task = Task(name, priority, deadline, created_at)

        if isinstance(task, Task):
            self._task_index += 1
            self._tasks[self._task_index] = task
            return True
        return False

    def remove_task(self, index):
        if index < self._task_index:
            del self._tasks[index]
            return True
        else:
            return False

    def __len__(self):
        return self._task_index

    def get_tasks(self):

        if len(self._tasks) == 0:
            print('no task')
        else:
            print('tasks:')
            for index, task in self._tasks.items():
                print(f'{index}:{task.name}')

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    def get_task_by_index(self, index):
        if index < self._task_index:
            print(f'{index}:{self._tasks[index].name}')
        else:
            return None

    def get_task_by_name(self, name):
        for index, task in self._tasks.items():
            if task.name == name:
                return f'{index}:{task.name}'

    def get_low_task(self):
        if len(self._tasks) == 0:
            print('no task')
        else:
            low_task = [task.name for index, task in self._tasks.items() if task.priority == 'low']
            if len(low_task) == 0:
                print('no low priority task')
            else:
                print(low_task)

    def get_high_task(self):
        # print('high priority task:')
        if len(self._tasks) == 0:
            print('no task')
        else:
            high_task = [task.name for index, task in self._tasks.items() if task.priority == 'high']
            if len(high_task) == 0:
                print('no high priority task')
            else:
                print(high_task)

    def get_overdue_task(self):
        if len(self._tasks) == 0:
            print('no task')
        else:
            task = [task.name for index, task in self._tasks.items() if task.is_overdue()]
            if len(task) == 0:
                print('no overdue task')
            else:
                print(task)

    def get_finished_task(self):
        if len(self._tasks) == 0:
            print('no task')
        else:
            task = [task.name for index, task in self._tasks.items() if task.is_finished()]
            if len(task) == 0:
                print('no finished task')
            else:
                print(task)

    def get_unfinished_task(self):
        if len(self._tasks) == 0:
            print('no task')
        else:
            task = [task.name for index, task in self._tasks.items() if not task.is_finished()]
            if len(task) == 0:
                print('no unfinished task')
            else:
                print(task)

    def update_task_status(self, status, index):
        if len(self._tasks) == 0:
            print('no task')
        else:
            if index < 0 or index > len(self._tasks):
                print('index out of range')
            else:
                self._tasks[index].status = status

    def get_rest_time(self):
        content = ''
        for index, task in self._tasks.items():
            content += f'{task.check_time()}\n'
        print(content)

    def save(self):
        with open(f'{self._name}.txt', 'w') as f:
            for index, task in self._tasks.items():
                f.write(f'{index}: {task}')

    def load(self, string):
        try:
            with open(f'{string}.txt', 'r') as f:
                for line in f.readlines():
                    parts = line.split()
                    # print(parts)

                    task_index = parts[0][:-1]  # 去掉冒号
                    task_name = parts[1][5:]
                    task_priority = parts[3][9:]
                    task_deadline = parts[4][9:]
                    task_created_at = parts[5][11:]

                    task = Task(task_name, task_priority, task_deadline, task_created_at)

                    self._tasks[int(task_index)] = task
                # print(f'加载{self._name}任务列表成功！')
        except FileNotFoundError:
            print(f'加载{self._name}任务列表失败！')
