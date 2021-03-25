import os
import sys
import psutil


from free_space_config import SPACE_INT, RAW_SOURCE_LIST, SUFFIX


def disk_init (source_list):  #Находим диски
    
    disks = []
    for s in source_list:
        if os.path.isdir(s):
            disks.append(s)
    return disks


disks = disk_init(RAW_SOURCE_LIST)

os.system('hide_current_console.exe')
    
cycle = True                         
while cycle:
    for d in disks:
        free = psutil.disk_usage(d).free/(1024*1024*1024)
        if free < SPACE_INT:
            cycle = False
os.startfile('disk_clean.exe')
sys.exit()