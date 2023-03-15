from ttool import vtool
from ttool import getRange
from ttool import videoSync
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

# import vtool
# import getRange
# import videoSync
# import multiprocessing
# import time
# import logging
# import numpy as np
# import pandas as pd
# # import dtool
# import getLeadTime
# import os
# from multiprocessing import Lock
# from pathlib import Path
# import predeal


def dealTheVideo(kind,screen_video_path, camera_video_path, id, camera_name, screen_name, photo_id, camera_location,
                 lead_time, json_path, phoneSize):
    res, screenInfo,ScreenSize = vtool.getScreenVideoFrame(kind,screen_video_path)

    screen_frame, camera_frame, dealInfo = videoSync.videoSync(res, screen_video_path, camera_video_path, lead_time)

    RecordInfo = getRange.getTheRange(id, camera_name, screen_name, photo_id, camera_location, phoneSize, screen_frame,
                                      camera_frame,
                                      json_path,ScreenSize)
    '''
    log添加
    screenInfo [fps,total_frame,无目标帧数量]
    dealInfo = [dealFrame,screen_frame_total,camera_frame_total]
    删除提前帧数量，录屏删除后总数量，人脸视频总帧数
    RecordInfo = [成语个数]
    
    '''
    return screenInfo, dealInfo, RecordInfo


def getTheLabel(id, photoNum, screenInfo, dealInfo, RecordInfo):
    label = str(id) + " " + str(photoNum) + " " + str(screenInfo[0]) + " " \
            + str(screenInfo[2]) + " " + str(dealInfo[0]) + " " + str(dealInfo[1]) + " " + str(dealInfo[2]) \
            + " " + str(RecordInfo[0])

    return label


if __name__ == '__main__':
    '''
    精细处理脚本
    
    '''


    record_path = '/home/work/didonglin/GazeTR/new-code/video-download/final_data.txt'
    log_path = '/home/work/didonglin/GazeTR/new-code/video-basetreat/Deal_log.label'
    dataset_path = '/disk1/repository/DGaze-New1000/dataset_origin/'
    phoneFilePath = './PhoneInfo.csv'
    outfile = open(log_path, 'w')
    outfile.write('数据集本处理情况记录\n')
    outfile.write('编号 相片个数 录屏fps 无成语帧数量 删除提前帧数量 录屏删除后总数量 人脸视频总帧数 成语总数\n')
    outfile.close()

    record = pd.read_table(record_path)
    phoneInfo = pd.read_csv(phoneFilePath)

    file_need  = record[record['当前状态'] == '已回收']

    for i in range(file_need.shape[0]):

            user_index = file_need.iloc[i, 0]

            if user_index != 36277:
                continue

            print("正在处理: " + str(user_index) + " 号数据")
            user_camera_url = file_need.iloc[i, 17]
            user_screen_url = file_need.iloc[i, 18]
            leadTime = getLeadTime.getTheLeadTime(user_camera_url, user_screen_url)
            model_display = file_need.iloc[i, 14]

            if model_display == 'PDCM00_11_C':
                model_display = 'PDCM00'

            if model_display == 'PEGM00_11_A.32':
                model_display = 'PEGM00'
            
            if model_display == 'LYA-AL00%2010.1.0.163(C00E160R1P8)':
                model_display = 'LYA-AL00'

            kind = 0
            if model_display == 'MI%209':
                # 型号为小米那款，需要后面进行裁，黑边处理
                kind = 1


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
                photo_name = 'photo_' + str(user_index) + '_' + str(i) + '_.png'
                currPhotoFile = Path(os.path.join(photo_path, photo_name))
                if currPhotoFile.exists():
                    photoId.append(i)

                photoCount = photoCount + 1

            '''
            预处理数据准备工作完成

            '''

            # try:
            file_camera = Path(camera_video)
            file_screen = Path(screen_video)
            if file_camera.exists() and file_screen.exists():
                screenInfo, dealInfo, RecordInfo = predeal.dealTheVideo(kind,screen_video, camera_video, user_index,
                                                                        camera_name, screen_name,
                                                                        photoId, camera_location, leadTime,
                                                                        label_path,
                                                                        screen_size)

                label = predeal.getTheLabel(user_index, photoCount, screenInfo, dealInfo, RecordInfo)
                # with lock:
                f = open(log_path, 'a+')
                f.write(label + "\n")
                f.close()
                print(label)
            else:
                label = "编号" + str(user_index) + "视频丢失"
                print(label)
                # with lock:
                f = open(log_path, 'a+')
                f.write(label + "\n")
                f.close()
            # except:
            #     label = "编号" + str(user_index) + "处理出错"
            #     print(label)
            #     # with lock:
            #     f = open(log_path, 'a+')
            #     f.write(label + "\n")
            #     f.close()

