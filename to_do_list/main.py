# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。


"""
用户应能够添加新任务。
用户应能够查看任务列表。
用户应能够标记任务为已完成。
用户应能够删除任务。
可以按照不同的状态（未完成、已完成）显示任务。
可以保存任务列表到文件，以便下次启动应用程序时加载之前的任务
"""

from list import List


def showMenu():
    l = List('')
    comm = ''
    while comm != 'q':
        comm = input('1.add task\n2.show task list\n3.update task finished\n4.show unfinished task\n5.delete task'
                     '\n6.show high priority task\n7.show low priority task\n8.show rest time\n9.save/load task list'
                     'list\nq.quit\n')
        if comm == '1':
            l.add_task()
        elif comm == '2':
            l.get_tasks()
        elif comm == '3':
            l.update_task_status(input('input task status:'), int(input('input task index:')))
        elif comm == '4':
            l.get_unfinished_task()
        elif comm == '5':
            l.remove_task(int(input('input delete task index:')))
        elif comm == '6':
            l.get_high_task()
        elif comm == '7':
            l.get_low_task()
        elif comm == '8':
            l.get_rest_time()
        elif comm == '9':
            cho = input('1.save\n2.load\n')
            if cho == '1':
                l.save()
            elif cho == '2':
                l.load(input('input list file name:')[:-5])
        elif comm == 'q':
            print('Thanks for using!')
            break


def __main__():
    showMenu()


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    __main__()

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
