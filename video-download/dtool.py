import gzip
import os
import cv2
import requests


class RecordInfo:
    __column_string = ''
    __Info_string = []
    __Info_path = ''
    __Info_name = 'record.label'

    def __init__(self, file_path, file_name, column_list):
        """

        :param file_path: the file location
        :param file_name: the log file name
        :param column_list: the column in the log
        """
        column_string = ""
        for i in range(len(column_list)):

            if i == 0:
                column_string = column_string + str(column_list[i])
            else:
                column_string = column_string + " " + str(column_list[i])

        self.__column_string = column_string
        self.__Info_path = file_path
        self.__Info_name = file_name

    def addNewString(self, info_list):
        self.__Info_string.append(info_list)

    def outTheFile(self):
        label_outpath = os.path.join(self.__Info_path, self.__Info_name)
        outfile = open(label_outpath, 'w')
        outfile.write(self.__column_string + "\n")

        for i in range(len(self.__Info_string)):
            current_string = ''
            for j in range(len(self.__Info_string[i])):
                if j == 0:
                    current_string = current_string + str(
                        self.__Info_string[i][j])
                else:
                    current_string = current_string + " " + str(
                        self.__Info_string[i][j])

            current_string = current_string + "\n"
            outfile.write(current_string)


def un_gz(file_name):
    '''

    :param file_name: 需要解压的以gz为后缀的文件路径
    :return:
    '''
    # 获取文件的名称，去掉后缀名
    f_name = file_name.replace(".gz", "")
    # 开始解压
    g_file = gzip.GzipFile(file_name)
    # 读取解压后的文件，并写入去掉后缀名的同名文件（即得到解压后的文件）
    open(f_name, "wb+").write(g_file.read())
    g_file.close()


def downAndDealTheFile(url, file_path, file_name, kind):
    '''

    :param url: 待下载的url
    :param file_path: 待下载的文件路径
    :param file_name: 待下载的文件名
    :param kind: url类型，1,2,3 === camera,screen,photo
    :return: [camera,kind,width,height]
    kind{1,2,3,4 === 200,404,黑屏,error}
    :return: [screen,kind,width,height]
    :return: [photo,kind]
    :return: []

    '''
    filepath = os.path.join(file_path, file_name)
    if kind == 3:
        '''
        下载图片
        '''
        try:
            f = requests.get(url)
            if f.status_code == 404:
                return [kind, 2]
            if f.status_code == 200:
                with open(filepath, "wb") as code:
                    code.write(f.content)

                code.close()
        except IOError:

            return [kind, 4]
        else:
            return [kind, 1]

    if kind == 1 or kind == 2:
        try:
            kind = url.split(".mp4")[1][:3]
            if kind == ".gz":
                filepath_gz = filepath + ".gz"
                f = requests.get(url)
                if f.status_code == 404:
                    return [kind, 2]
                if f.status_code == 200:
                    with open(filepath_gz, "wb") as code:
                        code.write(f.content)
                    code.close()
                un_gz(filepath_gz)
                video = cv2.VideoCapture(filepath)
                width = video.get(3)
                height = video.get(4)
                if width == 0.0 or height == 0.0:
                    return [kind, 3]
                else:
                    return [kind, 1, width, height]
            else:
                f = requests.get(url)
                if f.status_code == 404:
                    return [kind, 2]
                if f.status_code == 200:
                    with open(filepath, "wb") as code:
                        code.write(f.content)
                    code.close()
                # un_gz(filepath_gz)
                video = cv2.VideoCapture(filepath)
                width = video.get(3)
                height = video.get(4)
                if width == 0.0 or height == 0.0:
                    return [kind, 3]
                else:
                    return [kind, 1, width, height]

        except:
            print(url)
            return [kind, 4]


def getTheInfo(index, camera_result, screen_result, photo_result):
    '''
    根据上面的下载方法返回的结果，整理成写入日志的一行标签
    :param camera_result:
    :param screen_result:
    :param photo_result:
    :return:
    '''

    label = ""

    try:
        user_id = str(index)
        camera_state = ""
        screen_state = ""
        swidth = "-1"
        sheight = "-1"
        photo_count = 0

        if camera_result[1] == 1:
            camera_state = "下载成功"
        elif camera_result[1] == 2:
            camera_state = "NoSuchKey"
        elif camera_result[1] == 3:
            camera_state = "黑屏"
        elif camera_result[1] == 4:
            camera_state = "Error"

        if screen_result[1] == 1:
            screen_state = "下载成功"
            swidth = str(screen_result[2])
            sheight = str(screen_result[3])

        elif screen_result[1] == 2:
            screen_state = "NoSuchKey"
        elif screen_result[1] == 3:
            screen_state = "黑屏"
        elif screen_result[1] == 4:
            screen_state = "Error"

        for i in range(24):
            if photo_result[i][1] == 1:
                photo_count = photo_count + 1

        label = " ".join([
            str(user_id), camera_state, screen_state, swidth, sheight,
            str(photo_count)
        ])
    except IOError:
        label = "生成标签过程错误"

    return label
