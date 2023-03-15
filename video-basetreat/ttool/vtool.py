import cv2
import numpy as np
import pandas as pd


def getScreenVideoFrame(kind, screen_video_path):
    screen_cap = cv2.VideoCapture(screen_video_path)
    # lower_red_p = np.array([0, 43, 46])
    # higher_red_p = np.array([10, 255, 255])
    # lower_red_b = np.array([156, 43, 46])
    # higher_red_b = np.array([180, 255, 255])
    lower_red_p = np.array([0, 120, 120])
    higher_red_p = np.array([10, 255, 255])

    lower_red_b = np.array([156, 120, 120])
    higher_red_b = np.array([180, 255, 255])

    res = pd.DataFrame(columns=('frame_id', 'x', 'y', 'w', 'h'))
    x1, y1, w1, h1 = 0, 0, 0, 0

    mark = True
    ScreenSize = []

    while (True):

        ret, frame = screen_cap.read()

        if frame is None:
            break

        if kind == 1:
            # 型号为小米那款，带黑边，需要进行去黑边操作
            frame = change_size_x(frame)

        if kind == 2:
            # 型号为小米那款，带黑边，需要进行去黑边操作
            frame = change_size_y(frame)


        if mark:
            ScreenSize = str([frame.shape[0], frame.shape[1]])
            mark = False
            # print(ScreenSize)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask_red_1 = cv2.inRange(hsv, lower_red_p, higher_red_p)
        mask_red_2 = cv2.inRange(hsv, lower_red_b, higher_red_b)
        mask_red = mask_red_1 + mask_red_2
        ret, dst = cv2.threshold(mask_red, 100, 255, cv2.THRESH_BINARY_INV)
        # 膨胀，让红色连一起
        kernel1 = cv2.getStructuringElement(cv2.MORPH_RECT, (45, 40))
        erosion_dst = cv2.erode(dst, kernel1)
        contours, hierarchy = cv2.findContours(erosion_dst, cv2.RETR_TREE,
                                               cv2.CHAIN_APPROX_SIMPLE)
        sp = erosion_dst.shape

        for i in range(0, len(contours)):
            x, y, w, h = cv2.boundingRect(contours[i])
            if w / h > 2 and w > sp[1] * 0.2 and y > sp[1] * 0.1:
                # print(screen_cap.get(1), x, y, w, h)
                # 发现符合要求矩形块，认为是成语位置，返回x,y,w,h

                x1 = x
                y1 = y
                w1 = w
                h1 = h
                # print(frame.dtype, screen_cap.get(1), x1, y1, w1, h1)

                # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)  # 将检测到的颜色框起来
                break

            # 考虑一下这个地方怎么写更符合逻辑
            x1 = -1
            y1 = -1
            w1 = -1
            h1 = -1

        res = res.append([{
            "frame_id": screen_cap.get(1),
            "x": x1,
            "y": y1,
            "w": w1,
            "h": h1
        }],
                         ignore_index=True)

    screen_fps = int(screen_cap.get(5))
    screen_total_frame = int(screen_cap.get(7))
    noneNum = int(res[res['w'] == -1].shape[0])
    screenInfo = [screen_fps, screen_total_frame, noneNum]
    screen_cap.release()
    # cv2.destroyAllWindows()
    return res, screenInfo, ScreenSize


def change_size_x(image):
    '''
    沿x方向去黑边
    '''
    img = cv2.medianBlur(image, 5)  #中值滤波, 去除黑色边际中可能含有的噪声干扰
    b = cv2.threshold(img, 15, 255, cv2.THRESH_BINARY)  #调整裁剪效果
    binary_image = b[1]  #二值图 -- 具有三通道
    binary_image = cv2.cvtColor(binary_image, cv2.COLOR_BGR2GRAY)
    # print(binary_image.shape)       #改为单通道
    x = binary_image.shape[0]
    # print("高度 x=",x)
    y = binary_image.shape[1]
    # print("宽度 y=",y)
    edges_y = []
    for j in range(y):
        if binary_image[100][j] == 255:
            edges_y.append(j)  #宽度
    bottom = min(edges_y)  #底部
    top = max(edges_y)  #顶部
    height = top - bottom  #高度
    pre1_picture = image[:, bottom:bottom + height]  #图片截取
    return pre1_picture


def change_size_y(image):
    img = cv2.medianBlur(image, 5)  #中值滤波, 去除黑色边际中可能含有的噪声干扰
    b = cv2.threshold(img, 15, 255, cv2.THRESH_BINARY)  #调整裁剪效果
    binary_image = b[1]  #二值图 -- 具有三通道
    binary_image = cv2.cvtColor(binary_image, cv2.COLOR_BGR2GRAY)
    # print(binary_image.shape)       #改为单通道
    x = binary_image.shape[0]
    # print("高度 x=",x)
    y = binary_image.shape[1]
    # print("宽度 y=",y)
    edges_x = []
    for i in range(x):
        if binary_image[i][200] == 255:
            edges_x.append(i)  #宽度
    bottom = min(edges_x)  #底部
    top = max(edges_x)  #顶部
    height = top - bottom  #高度
    pre1_picture = image[bottom:bottom + height, :]  #图片截取
    return pre1_picture


if __name__ == '__main__':
    '''
    此方法用于检查某一视频成语定位
    
    '''
    screen_path = '/disk1/repository/DGaze-New1000/dataset_origin/36469/screen/screen_36469_.mp4'

    res, screenInfo, ScreenSize = getScreenVideoFrame(0, screen_path)

    print(res)
    print(res.shape)
    print(screenInfo)
