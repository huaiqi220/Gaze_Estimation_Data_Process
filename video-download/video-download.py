"""
从质检平台的报表里下载指定数据
"""

import multiprocessing
import time
import logging
import numpy as np
import pandas as pd
import dtool
import os
from multiprocessing import Lock

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [*] %(processName)s %(message)s")


def down_process(count, file_need, dataset_path, log_path, lock):

    while count.value < int(file_need.shape[0]):
        current_index = count.value
        with count.get_lock():  # 仍然需要使用 get_lock 方法来获取锁对象
            count.value += 1

        # 获得url
        user_index = file_need.iloc[current_index, 0]
        print("正在处理: " + str(user_index) + " 号数据")
        user_camera_url = file_need.iloc[current_index, 17]
        user_screen_url = file_need.iloc[current_index, 18]
        user_photo_url_list = file_need.iloc[current_index, 15].split("|")[:24]
        '''
        
        dataset_path 数据集根目录
        current_path  本条数据根目录
        screen_path 录屏目录
        camera_path 人像目录
        photo_path 限界相片目录
        
        '''
        current_path = dataset_path + str(user_index) + "/"
        if not os.path.exists(current_path):
            os.mkdir(current_path)
        screen_path = current_path + "screen/"
        if not os.path.exists(screen_path):
            os.mkdir(screen_path)
        camera_path = current_path + "camera/"
        if not os.path.exists(camera_path):
            os.mkdir(camera_path)
        photo_path = current_path + "photo/"
        if not os.path.exists(photo_path):
            os.mkdir(photo_path)

        camera_name = 'camera_' + str(user_index) + '_.mp4'
        camera_result = dtool.downAndDealTheFile(user_camera_url, camera_path,
                                                 camera_name, 1)
        screen_name = 'screen_' + str(user_index) + '_.mp4'
        screen_result = dtool.downAndDealTheFile(user_screen_url, screen_path,
                                                 screen_name, 1)

        photo_result = []
        photo_count = 1
        for i in range(24):
            curr_photo_url = user_photo_url_list[i]
            photo_name = 'photo_' + str(user_index) + '_' + str(
                photo_count) + '_.png'
            photo_count = photo_count + 1
            curr_photo_result = dtool.downAndDealTheFile(
                curr_photo_url, photo_path, photo_name, 3)
            photo_result.append(curr_photo_result)
        '''
        根据camera_result,screen_result,photo_result得出日志文件写法，并添加到文件中

        '''
        label = dtool.getTheInfo(user_index, camera_result, screen_result,
                                 photo_result)
        with lock:
            f = open(log_path, 'a+')
            f.write(label + "\n")
            f.close()


def main_process(ctx, file_data, dataset_path, log_path, lock):
    v = ctx.Value("i", 0)  # 使用 value 来标明全局进度
    # print("主进程开始")
    # 若value大于1000，进程停止

    # file_data = pd.read_table(record_path)

    # file_need = file_data[file_data['当前状态'] == "已回收"].copy()

    processList = [
        ctx.Process(target=down_process,
                    args=(v, file_data, dataset_path, log_path, lock))
        for _ in range(9)
    ]
    [task.start() for task in processList]
    [task.join() for task in processList]
    logging.info(v.value)


if __name__ == '__main__':

    # record_path = './mate30.txt'
    # 报表文件路径，从审核平台下载

    file_path = "./data"

    list = os.listdir(file_path)

    file_table_list = []

    for file in list:

        file_table_list.append(pd.read_table(os.path.join(file_path, file)))

    res = pd.concat(file_table_list, axis=0)

    file_need = res[res["当前状态"] == "不回收"]

    print(file_need.shape)

    log_path = './Download_log_5000.label'
    # 生成日志文件位置
    dataset_path = '/disk2/repository/DGaze-5000/data_origin/'
    # 视频文件下载位置

    outfile = open(log_path, 'w')
    outfile.write(
        'index camera_state screen_state screen_width screen_height photo_num\n'
    )
    outfile.close()

    multiprocessing.set_start_method('spawn')
    ctx = multiprocessing.get_context('spawn')
    lock = Lock()
    main_process(ctx, file_need, dataset_path, log_path, lock)
