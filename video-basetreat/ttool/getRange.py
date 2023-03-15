import numpy
import pandas as pd
import json


def getTheRange(id, video_id, screen_id, photo_id, camera_position,phoneSize, screen_frame_info, camera_frame_info, json_path,ScreenSize):
    article_info = {}
    data = json.loads(json.dumps(article_info))
    writer = {}
    x1, y1, w1, h1 = screen_frame_info.iloc[1, 1], screen_frame_info.iloc[1, 2], screen_frame_info.iloc[1, 3], \
                     screen_frame_info.iloc[1, 4]
    # print(frameinfo.shape[0])

    gaze_frame_list = []
    screen_frame_list = []
    count = 0
    text_bbox = []

    for i in range(0, screen_frame_info.shape[0]):

        camera_frame = camera_frame_info.iloc[i, 0]
        screen_frame = screen_frame_info.iloc[i, 0]
        x, y, w, h = screen_frame_info.iloc[i, 1], screen_frame_info.iloc[i, 2], screen_frame_info.iloc[i, 3], \
                     screen_frame_info.iloc[i, 4]
        # print(x, y, w, h)
        # 判断此处是否出现成语变换

        if (x < x1 - 40) or (x > x1 + 40) or (y < y1 - 30) or (y > y1 + 30):
            # print(count)

            # print("当前帧：" + str(i))
            # print(len(gaze_frame_list))

            if len(gaze_frame_list) > 15 :
                if count == 0:
                    count = count + 1
                else:
                    # print(count)
                    unit = {'text_bbox': str(text_bbox), 'gaze_frame': str(gaze_frame_list),
                            'screen_frame': str(screen_frame_list)}
                    cent = {count: unit}
                    # print(cent)
                    writer.update(cent)
                    count = count + 1




            gaze_frame_list = []
            screen_frame_list = []
            text_bbox = [x, y, x + w, y + h]
            gaze_frame_list.append(camera_frame_info.iloc[i, 0])
            screen_frame_list.append(screen_frame_info.iloc[i, 0])
        else:
            gaze_frame_list.append(camera_frame_info.iloc[i, 0])
            screen_frame_list.append(screen_frame_info.iloc[i, 0])

        x1 = x
        y1 = y
        w1 = w
        h1 = h

    # 最后一个成语不添加
    # count = count + 1
    # print(count)
    # unit = {'text_bbox': str(text_bbox), 'gaze_frame': str(gaze_frame_list),
    #         'screen_frame': str(screen_frame_list)}
    # cent = {count: unit}
    # print(cent)
    # writer.update(cent)

    article2 = {'gaza_video_id': video_id, 'screen_video_id': screen_id, 'photo_id': photo_id,
                'camera_position': str(camera_position),'phone_size':str(phoneSize), 'screen_size(px)': ScreenSize,'text': writer}
    data[int(id)] = article2

    article = json.dumps(data, ensure_ascii=False, indent=4)

    with open(json_path, 'w') as json_file:
        json_file.write(article)

    RecordInfo = [int(count) - 1]
    return RecordInfo
