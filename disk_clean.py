import os
import time
import datetime
import time_datetime_converter

from free_space_config import RAW_SOURCE_LIST, RAW_ORIGINAL_LIST


def src_init(raw_dirs_list):  # Находим диски
    _src_list = []
    for s in raw_dirs_list:
        if os.path.isdir(s):
            _src_list.append(s)
            print('найден диск '+s)
    return _src_list


def dest_init(raw_dirs_list):  # Находим диски

    _dest_list = []
    for d in raw_dirs_list:
        if os.path.isdir(d):
            _dest_list.append(os.path.abspath(os.path.join(d, 'ORIGINAL')))
            print('найден диск '+d)
    return _dest_list


def welcome():     # Ввод пользователем days_old
    print('Программа поможет удалить старые .mxf файлы c диска BRIO, кроме тех, '
          'что находятся в папке "не удалять". Продолжить? y/n')
    answer = input()
    if answer == 'n':
        print('Выход')
        time.sleep(2)
        exit()
    elif (answer != 'n') and (answer != 'y'):
        print('Продолжить - клавиша "y", отмена - клавиша "n"')
        time.sleep(2)
        welcome()
    elif answer == 'y':
        
        print('Файлы старше скольки дней удаляем? (количество дней цифрами)')
        _days_old = int(input())

    return(_days_old)


def raw_del_list(_src_list, _days_old):   # Первоначальный список на удаление (по дате создания)

    first_del_list = []

    for dirs in _src_list:

        for i in os.walk(dirs):

            for j in i[2]:
                if j.endswith('.mxf'):
                    path = os.path.join(os.path.abspath(i[0]), j)
                    file_create_date = time.ctime(os.path.getctime(path))
                    converted_file_create_date = time_datetime_converter.convert_to_datetime(
                        file_create_date)                              # Импортированная функция convert_to_datetime
                    now = datetime.date.today()
                    time_check = datetime.timedelta(days=_days_old)

                    if (now - converted_file_create_date) > time_check:
                        if 'не удалять' not in path and 'НЕ УДАЛЯТЬ' not in path:
                            first_del_list.append(j)
    return first_del_list


def exist_check(_days_old_list, _dest):

    _final_list = []

    for dests in _dest:

        for i in os.walk(dests):
            for j in i[2]:
                if j in _days_old_list:
                    _final_list.append(j)

        return _final_list


def remove(_final_delete_list, _src_list):

    deleted_files = 0
    optimized_memory = 0
    cant_delete = 0

    for dirs in _src_list:

        for i in os.walk(dirs):
            for j in i[2]:
                if j in _final_delete_list:
                    cache_memory = os.path.getsize(str(i[0]))  # Память удаляемого файла

                    try:
                        del_file_path = os.path.join(os.path.abspath(i[0]), j)
                        os.remove(del_file_path)
                        deleted_files += 1
                        optimized_memory += cache_memory
                    except:
                        cant_delete += 1
                        pass

    print('Очистка закончена. Удалено ' + str(deleted_files) + ' файлов, освободилось '
          + str(int(optimized_memory / 1024 / 1024 / 1024)) + ' Гб')
    print(str(cant_delete)+' файлов только для чтения')
    time.sleep(10)


if __name__ == "__main__":
    days_old = 'none'
    while type(days_old) is str:
        days_old = welcome()

    src_list = src_init(RAW_SOURCE_LIST)
    dest = dest_init(RAW_ORIGINAL_LIST)

    days_old_list = raw_del_list(src_list, days_old)
    final_delete_list = exist_check(days_old_list, dest)

    remove(final_delete_list, src_list)

    time.sleep(2)
    os.startfile('free_space.exe')



