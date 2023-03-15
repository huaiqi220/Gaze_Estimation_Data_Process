import numpy as np
import cv2
import pandas as pd


def videoSync(frameinfo, screen_video_path, camera_video_path, lead):
    # lead:提前量，即screenVideo相对cameraVideo提前开始的时间（s/秒）
    # state状态位 state=1 screen先开始、state=2 camera先开始
    # print(frameinfo.shape)
    screen_cap = cv2.VideoCapture(screen_video_path)
    camera_cap = cv2.VideoCapture(camera_video_path)
    # 获得录屏及人脸视频帧率
    screen_fps = screen_cap.get(5)
    screen_frame_total = screen_cap.get(7)
    # print(screen_frame_total)
    camera_frame_total = camera_cap.get(7)

    camera_frame = pd.DataFrame(columns=['frame_id'])

    for i in range(0, int(camera_frame_total)):
        camera_frame = camera_frame.append([{
            "frame_id": i + 1,
        }], ignore_index=True)

    # print(camera_frame_total)
    # print("===================开始处理==================")
    # print("===================删去screen多余帧===============")
    # 根据数据检验，1000条数据中不存在camera比screen更早启动的情况，故此处只可能从screen中删除多余帧

    head_lead = lead * screen_fps

    # print("screen 多余帧为前" + str(head_lead) + "帧")
    if head_lead < 1:
        head_lead = 1
    
    for i in range(0, int(head_lead)):
        frameinfo.drop(index=[i], inplace=True)

    # print("===============已删除多余帧==============")

    screen_frame_total = screen_frame_total - int(head_lead)

    if (screen_frame_total > camera_frame_total):
        # print("==============开始抽帧================")
        # 计算多余帧数
        lead = screen_frame_total - camera_frame_total
        # print(lead)
        # 计算抽帧周期，取整
        # print(int(screen_frame_total / lead))
        # 循环抽帧

        for i in range(0, int(lead)):
            count = (screen_frame_total / lead) * i + int(head_lead)
            # print(int(count))
            frameinfo.drop(index=[int(count)], inplace=True)

        # frameinfo.index = range(len(frameinfo))
    else:
        if screen_frame_total < camera_frame_total:

            lead = camera_frame_total - screen_frame_total
            # print(lead)
            # 计算抽帧周期，取整
            # print(int(camera_frame_total / lead))
            # 循环抽帧

            for i in range(0, int(lead)):
                count = (camera_frame_total / lead) * i
                # print(int(count))
                camera_frame.drop(index=[int(count)], inplace=True)

            camera_frame.index = range(len(frameinfo))

    frameinfo.index = range(len(frameinfo))

    dealFrame = int(head_lead)

    dealInfo = [dealFrame,screen_frame_total,camera_frame_total]

    return frameinfo, camera_frame,dealInfo



