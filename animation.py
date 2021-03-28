import threading
import time
import os
import queue

q = queue.Queue()

q.put(False)



class counter(object):
    def __init__(self):

        wait_label = "Loading"

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


class other(counter):
    def __init__(self):

        time.sleep(10)

        q.put(True)


counter_thread = threading.Thread(None, counter)
counter_thread.start()

other_thread = threading.Thread(None, other)
other_thread.start()