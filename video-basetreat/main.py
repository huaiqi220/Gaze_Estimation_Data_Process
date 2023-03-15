import multiprocessing
import time
import logging
import numpy as np
import pandas as pd
# import dtool
from ttool import getLeadTime
import os
from multiprocessing import Lock
from pathlib import Path
from ttool import predeal

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [*] %(processName)s %(message)s")


def down_process(count, file_need, dataset_path, log_path, lock, phoneInfo):
    while count.value < file_need.shape[0]:
        current_index = count.value
        with count.get_lock():  # 仍然需要使用 get_lock 方法来获取锁对象
            count.value += 1
        try:
            user_index = file_need.iloc[current_index, 0]
            print("正在处理: " + str(user_index) + " 号数据")
            user_camera_url = file_need.iloc[current_index, 17]
            user_screen_url = file_need.iloc[current_index, 18]
            leadTime = getLeadTime.getTheLeadTime(user_camera_url,
                                                    user_screen_url)
            model_display = file_need.iloc[current_index, 14]

            if model_display == 'PDCM00_11_C.10':
                model_display = 'PDCM00'

            if model_display == 'PEGM00_11_A.32':
                model_display = 'PEGM00'

            if model_display == 'SEA-AL10%202.0.0.210(C00E205R1P6)':
                model_display = 'SEA-AL10'

            if model_display == 'LYA-AL00%2010.1.0.163(C00E160R1P8)':
                model_display = 'LYA-AL00'

            kind = 0
            if model_display == 'MI%209':
                # 型号为小米那款，需要后面进行裁，黑边处理
                kind = 1

            if model_display == 'LYA-AL00':
                # 型号为小米那款，需要后面进行裁，黑边处理
                kind = 2

            phoneSize = phoneInfo[phoneInfo['型号'] == model_display]
            camera_x = phoneSize.iloc[0, 3]
            camera_y = phoneSize.iloc[0, 4]
            screen_width = phoneSize.iloc[0, 5]
            screen_height = phoneSize.iloc[0, 6]
            camera_location = [camera_x, camera_y]
            screen_size = [screen_width, screen_height]
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
            label_path = current_path + 'label.json'

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
            screen_name = 'screen_' + str(user_index) + '_.mp4'
            '''
            加载视频，检测视频是否存在，进行处理
            检查相片数量，检测现存相片编号
            
            '''

            camera_video = os.path.join(camera_path, camera_name)
            screen_video = os.path.join(screen_path, screen_name)

            photoCount = 0
            photoId = []

            for i in range(1, 25):
                photo_name = 'photo_' + str(user_index) + '_' + str(
                    i) + '_.png'
                currPhotoFile = Path(os.path.join(photo_path, photo_name))
                if currPhotoFile.exists():
                    photoId.append(i)

                photoCount = photoCount + 1
            '''
            预处理数据准备工作完成
            
            '''

            file_camera = Path(camera_video)
            file_screen = Path(screen_video)
            if file_camera.exists() and file_screen.exists():
                # print(screen_video)
                screenInfo, dealInfo, RecordInfo = predeal.dealTheVideo(
                    kind, screen_video, camera_video, user_index,
                    camera_name, screen_name, photoId, camera_location,
                    leadTime, label_path, screen_size)

                label = predeal.getTheLabel(user_index, photoCount,
                                            screenInfo, dealInfo,
                                            RecordInfo)
                with lock:
                    f = open(log_path, 'a+')
                    f.write(label + "\n")
                    f.close()
            else:
                label = "编号" + str(user_index) + "视频丢失"
                with lock:
                    f = open(log_path, 'a+')
                    f.write(label + "\n")
                    f.close()
        except:
            label = "编号" + str(user_index) + "处理出错"
            with lock:
                f = open(log_path, 'a+')
                f.write(label + "\n")
                f.close()


def main_process(ctx, file_need, dataset_path, log_path, lock, phoneInfo):
    '''
    多进程主进程
    '''
    v = ctx.Value("i", 0)  # 使用 value 来标明全局进度
    # print("主进程开始")
    # 若value大于1000，进程停止

    # file_data = pd.read_table(record_path)

    # file_need = file_data[file_data['当前状态'] == "不回收"].copy()

    # print(file_need.shape)

    processList = [
        ctx.Process(target=down_process,
                    args=(
                        v,
                        file_need,
                        dataset_path,
                        log_path,
                        lock,
                        phoneInfo,
                    )) for _ in range(16)
    ]
    [task.start() for task in processList]
    [task.join() for task in processList]
    logging.info("主处理进程退出")


if __name__ == '__main__':
    file_path = '/home/work/didonglin/Gaze-PrecClk/video-download/data'

    list = os.listdir(file_path)

    file_table_list = []

    for file in list:

        file_table_list.append(pd.read_table(os.path.join(file_path, file)))

    res = pd.concat(file_table_list, axis=0)

    file_need = res[res["当前状态"] == "不回收"]

    print(file_need.shape)
    log_path = '/home/work/didonglin/Gaze-PrecClk/video-basetreat/Deal_log_5000.label'
    dataset_path = '/disk2/repository/DGaze-5000/data_origin/'
    phoneFilePath = './PhoneInfo.csv'
    outfile = open(log_path, 'w')
    outfile.write('数据集本处理情况记录\n')
    outfile.write('编号 相片个数 录屏fps 无成语帧数量 删除提前帧数量 录屏删除后总数量 人脸视频总帧数 成语总数\n')
    outfile.close()
    phoneInfo = pd.read_csv(phoneFilePath)
    multiprocessing.set_start_method('spawn')
    ctx = multiprocessing.get_context('spawn')
    lock = Lock()
    main_process(ctx, file_need, dataset_path, log_path, lock, phoneInfo)
