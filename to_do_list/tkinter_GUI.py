import re
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, simpledialog
from list import List
import datetime
from task import Task
import pickle
import tkinter.filedialog


class TaskManagerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Task Manager")

        self.task_label = tk.Label(master, text="Tasks:")
        self.task_label.pack()

        self.List = List("list.txt")

        self.add_task_button = tk.Button(master, text="Add Task", command=lambda: self.add_task)
        self.add_task_button.place(x=100, y=100)
        self.add_task_button.config(state="disabled")

        self.load_list_button = tk.Button(master, text="Load List", command=lambda: self.load_list)
        self.load_list_button.place(x=100, y=200)

        self.save_list_button = tk.Button(master, text="Save List", command=lambda: self.save_list)
        self.save_list_button.place(x=100, y=300)
        self.save_list_button.config(state="disabled")

        self.new_list_button = tk.Button(master, text="New List", command=lambda: self.new_list)
        self.new_list_button.place(x=100, y=400)

        self.show_task_button = tk.Button(master, text="Show Tasks", command=lambda: self.show_tasks)
        self.show_task_button.place(x=100, y=500)
        self.show_task_button.config(state="disabled")

    def new_list(self):
        name = simpledialog.askstring("New List", "Enter List Name:")
        self.List.name = name

    def add_task(self):
        task_name = simpledialog.askstring("Add Task", "Enter Task Name:")
        task_priority = simpledialog.askstring("Add Task", "Enter Task Priority:")
        deadline_pattern = r"\d{4}-\d{2}-\d{2}"
        while True:
            deadline = simpledialog.askstring("Add Task", "Enter Task Deadline:")
            if re.match(deadline_pattern, deadline):
                # 检验输入日期是否是未来的时间
                current_date = datetime.now().strftime("%Y-%m-%d")
                if deadline >= current_date:
                    break
                else:
                    print("截止日期应为未来的时间，请重新输入。")
            else:
                print("日期格式错误，请重新输入。")
        create_at = datetime.now().strftime("%Y-%m-%d")
        task = Task(task_name, task_priority, deadline, create_at)
        if isinstance(task, Task):
            if self.List.load_task(task):
                print("Task added!")
                self.List.save()
            else:
                print("Task not added!")

    def show_tasks(self):
        tasks = self.List.get_tasks()
        if tasks:
            messagebox.showinfo("Tasks", tasks)
        else:
            messagebox.showwarning("No Tasks", "No tasks available!")

    def load_list(self):
        self.List.load(simpledialog.askstring("Load List", "Enter List Name:"))

    def save_list(self):
        self.List.save()


def main():
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.geometry("1600x1000")  # 设置窗口大小为800x600像素

    root.mainloop()


if __name__ == "__main__":
    main()
