import os
import sys
import time
import datetime
import configparser
import threading
import time_datetime_converter

config = configparser.ConfigParser()
config.read("config.ini")

SPACE_INT = int(config["Disk_clean_config"]["Critical disk free space (Gb)"])
RAW_SOURCE_LIST = eval(config["Disk_clean_config"]["Disk BRIO"])
RAW_ORIGINAL_LIST = eval(config["Disk_clean_config"]["Disk ORIGINAL"])
SUFFIX = config["Disk_clean_config"]["Suffix"]

deleted_files = 0
optimized_memory = 0
cant_delete = 0


def src_init(raw_dirs_list):  # Находим диски
    _src_list = []
    for s in raw_dirs_list:
        if os.path.isdir(s):
            _src_list.append(s)
            print("Найдены диски BRIO "+s)
    return _src_list


def dest_init(raw_dirs_list):  # Находим диски

    _dest_list = []
    for d in raw_dirs_list:
        if os.path.isdir(d):
            _dest_list.append(os.path.abspath(os.path.join(d, 'ORIGINAL')))
            print("ORIGINAL на диске "+d)
    return _dest_list


def welcome():     # Ввод пользователем days_old
    print('На диске BRIO осталось меньше '+str(SPACE_INT)+' гб свободного места')
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
            return _days_old

        except ValueError:
            print('Количество дней цифрами!')
            time.sleep(1)
            welcome()


def raw_del_list(_src_list, _days_old):   # Первоначальный список на удаление (по дате создания)

    print('Ищем старые файлы ...')

    x = threading.Thread(target=thread_function, args=(1,))

    first_del_list = []

    while True:

        print(1)

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

    print('Список файлов на удаление составлен')
    return first_del_list


def exist_check(_days_old_list, _dest):

    print("Идет сопоставление с ORIGINAL ...")
    _final_list = []

    for dests in _dest:

        for i in os.walk(dests):
            for j in i[2]:
                if j in _days_old_list:
                    _final_list.append(j)

        print("Сравнение файлов закончено")
        return _final_list


def remove(_final_delete_list, _src_list):

    print('Удаление файлов ...')

    for dirs in _src_list:

        for i in os.walk(dirs):
            for j in i[2]:
                if j in _final_delete_list:

                    cache_memory = os.path.getsize(str(i[0]))  # Память удаляемого файла

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

    print('Очистка закончена. Удалено ' + str(deleted_files) + ' файлов, освободилось '
          + str(int(optimized_memory / 1024 / 1024 / 1024)) + ' Гб')
    print(str(cant_delete)+' файлов только для чтения')
    time.sleep(10)


if __name__ == "__main__":

    days_old = welcome()

    src_list = src_init(RAW_SOURCE_LIST)
    dest = dest_init(RAW_ORIGINAL_LIST)

    days_old_list = raw_del_list(src_list, days_old)
    final_delete_list = exist_check(days_old_list, dest)

    remove(final_delete_list, src_list)

    time.sleep(2)
#    os.startfile('free_space.exe')
    sys.exit()
