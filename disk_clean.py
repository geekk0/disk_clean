import os
import logging
import time
import datetime
import configparser
import threading
import queue
import time_datetime_converter


current_path = os.path.dirname(os.path.realpath(__file__))

logger = logging.getLogger('simple_example')
logger.setLevel(logging.DEBUG)

cute_format = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S' )

debug_log = logging.FileHandler(os.path.join(current_path, 'debug.log'))     # to log debug messages
debug_log.setLevel(logging.DEBUG)
debug_log.setFormatter(cute_format)

error_log = logging.FileHandler(os.path.join(current_path, 'error.log'))     # to log errors messages
error_log.setLevel(logging.ERROR)
error_log.setFormatter(cute_format)

logger.addHandler(debug_log)
logger.addHandler(error_log)


config = configparser.ConfigParser()
config.read(os.path.join(os.getcwd(), "config.ini"), encoding='utf-8')
config.sections()

# SPACE_INT = int(config["Disk_clean_config"]["Critical disk free space (Gb)"])
RAW_SOURCE_LIST = eval(config["Disk_clean_config"]["Disk_BRIO"])
RAW_ORIGINAL_LIST = eval(config["Disk_clean_config"]["Disk_ORIGINAL"])
SUFFIX = config["Disk_clean_config"]["Suffix"]


deleted_files = 0
optimized_memory = 0
cant_delete = 0

q = queue.Queue()

q.put(False)


class Animation(object):
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

            if 3*'.' in wait_label:
                wait_label = old_wait_label +'.'

            else:
                wait_label += "."
            print(wait_label)
            time.sleep(1)


def src_init(raw_dirs_list):  # Находим диски BRIO
    _src_list = []
    for s in raw_dirs_list:
        if os.path.isdir(s):
            _src_list.append(s)
            logger.info("Найдены диски BRIO "+s)
    return _src_list


def dest_init(raw_dirs_list):  # Находим диски ORIGINAL

    _dest_list = []
    for d in raw_dirs_list:
        if os.path.isdir(d):
            _dest_list.append(os.path.abspath(os.path.join(d, 'ORIGINAL')))
            logger.info("ORIGINAL на диске "+d)
    return _dest_list


def welcome():     # Ввод пользователем days_old
    # print('На диске BRIO осталось меньше '+str(SPACE_INT)+' гб свободного места')
    print('Программа удалит старые '+SUFFIX+' файлы c диска BRIO, копии которых уже находятся в ORIGINAL, '
          'кроме тех, что находятся в папке "не удалять". Продолжить? y/n')
    answer = input()
    if answer == 'n':
        print('Выход')
        time.sleep(1)
        os.system('hide_current_console.exe')
        time.sleep(2000)
        exit()
    elif (answer != 'n') and (answer != 'y'):
        print('Продолжить - клавиша "y", отмена - клавиша "n"')
        time.sleep(1)
        welcome()
    elif answer == 'y':
        
        print('Файлы старше скольки дней удаляем? (количество дней цифрами)')

        try:
            _days_old = int(input())
            logger.info('Начало выполнения скрипта')
            return _days_old

        except ValueError:
            print('Количество дней цифрами!')
            time.sleep(1)
            welcome()


def raw_del_list(_src_list, _days_old):   # Первоначальный список на удаление (по дате создания)

    animation_thread_raw_list = threading.Thread(None, Animation, args=('Ищем старые файлы',), daemon=False)
    animation_thread_raw_list.start()

    first_del_list = []

    start_time = time.time()

    while True:

        for dirs in _src_list:

            for i in os.walk(dirs):

                for j in i[2]:

                    if j.endswith(SUFFIX):
                        path = os.path.join(os.path.abspath(i[0]), j)
                        file_create_date = time.ctime(os.path.getctime(path))
                        converted_file_create_date = time_datetime_converter.convert_to_datetime(
                            file_create_date)                              # Импортированная функция convert_to_datetime
                        now = datetime.date.today()
                        time_check = datetime.timedelta(days=_days_old)

                        if (now - converted_file_create_date) > time_check:
                            if 'не удалять' not in path and 'НЕ УДАЛЯТЬ' not in path:
                                first_del_list.append(j)
        break
    q.put(True)
    time.sleep(2)
    print('Список файлов на удаление составлен')
    logger.debug('Первоначальный список файлов на удаление '+str(first_del_list))
    return first_del_list


def exist_check(_days_old_list, _dest):

    q.put(False)
    animation_thread_exist_check = threading.Thread(None, Animation,
                                                    args=('Идет сравнение с ORIGINAL',), daemon=False)
    animation_thread_exist_check.start()
    _final_list = []

    for dests in _dest:

        for i in os.walk(dests):
            for j in i[2]:
                if j in _days_old_list:
                    _final_list.append(j)
    q.put(True)
    time.sleep(2)
    print("Сравнение файлов закончено")
    logger.debug('Финальный список на удаление '+str(_final_list))
    return _final_list


def remove(_final_delete_list, _src_list):

    q.put(False)
    animation_thread_remove = threading.Thread(None, Animation, args=('Удаление файлов',), daemon=False)
    animation_thread_remove.start()

    for dirs in _src_list:

        for i in os.walk(dirs):
            for j in i[2]:
                if j in _final_delete_list:

                    cache_memory = os.path.getsize(os.path.join(os.path.abspath(i[0]), j))  # Память удаляемого файла

                    try:
                        del_file_path = os.path.join(os.path.abspath(i[0]), j)
                        os.remove(del_file_path)

                        global deleted_files
                        global optimized_memory

                        deleted_files += 1
                        optimized_memory += cache_memory

                    except OSError:

                        global cant_delete

                        cant_delete += 1
                        pass

    q.put(True)
    time.sleep(2)
    print('Очистка закончена. Удалено ' + str(deleted_files) + ' файлов, освободилось '
          + str(int(optimized_memory / 1024 / 1024 / 1024)) + ' Гб')
    print(str(cant_delete)+' файлов только для чтения')
    logger.debug('Скрипт закончил выполнение.')


if __name__ == "__main__":

    days_old = welcome()

    src_list = src_init(RAW_SOURCE_LIST)
    dest = dest_init(RAW_ORIGINAL_LIST)

    q.qsize()

    days_old_list = raw_del_list(src_list, days_old)
    final_delete_list = exist_check(days_old_list, dest)

    remove(final_delete_list, src_list)

    input()
#   time.sleep(2)
#    os.startfile('free_space.exe')
#    sys.exit()
