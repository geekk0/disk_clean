import threading
import time
import os
import queue

q = queue.Queue()

q.put(False)


class counter(object):
    def __init__(self, args):

        wait_label = args

        old_wait_label = wait_label

        self.stop_flag = q.get()

        while not self.stop_flag:
            try:
                self.stop_flag = q.get_nowait()
            except:
                pass
            os.system('cls') # might need to change this command for linux

            if 5*'.' in wait_label:
                wait_label = old_wait_label +'.'

            else:
                wait_label += "."
            print(wait_label)
            time.sleep(1)




label = 'Загрузка'
counter_thread = threading.Thread(None, counter, args=('Загрузка',), daemon=False)
counter_thread.start()

time.sleep(5)

q.put(True)
time.sleep(2)
print('5 секунд прошло')
print(q.task_done())
print(q.empty())
print(q.task_done())
