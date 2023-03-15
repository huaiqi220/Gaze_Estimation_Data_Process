import time
from datetime import datetime

import pandas as pd


def getTheLeadTime(camera_url, screen_url):
    '''
    输入录屏，人脸录像url，从中取出时间字符串，划为毫秒级时间戳，求出时间差
    ->还没测试，功能是否正确，累了，明天写
    :param camera_url:
    :param screen_url:
    :return:
    '''
    camera_time_list = camera_url.split(".mp4")[0].split("_camera_")[1].split("%3A")
    screen_time_list = screen_url.split(".mp4")[0].split("_screen_")[1].split("%3A")
    nct = camera_time_list[0].replace("_", " ") + ":" + camera_time_list[1] + ":" + camera_time_list[2]
    ct = time.mktime(datetime.strptime(nct, '%Y-%m-%d %H:%M:%S').timetuple())
    ct_lead = int(camera_time_list[3]) / 1000
    nst = screen_time_list[0].replace("_", " ") + ":" + screen_time_list[1] + ":" + screen_time_list[2]
    st = time.mktime(datetime.strptime(nst, '%Y-%m-%d %H:%M:%S').timetuple())
    st_lead = int(screen_time_list[3]) / 1000
    camera_time = ct + ct_lead
    screen_time = st + st_lead

    return camera_time - screen_time


if __name__ == '__main__':

    '''
    运行脚本可统计1000条数据启动时间差
    
    '''

    file_path = 'C:/Users/zhuziyang/Desktop/final_data.txt'

    file_data = pd.read_table(file_path)

    file_need = file_data[file_data['当前状态'] == "已回收"].copy()

    for i in range(int(file_need.shape[0])):
        user_camera_url = file_need.iloc[i, 17]
        user_screen_url = file_need.iloc[i, 18]

        print(str(i) + ": " + str(getTheLeadTime(user_camera_url, user_screen_url)))
