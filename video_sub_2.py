import cv2
import numpy
import os

VIDEO_PATH = "test.flv" # 视频地址
VIDEO_SVAE_PATH = "images/" # 图片保存地址
IMAGELISTSIZE = 20 # 图片拼接数量
SAVE_AS_GRAY = True # 图片保存是否是灰色 True 是，False 则保存成原样

picutre_x1 = 480 # 左上角x坐标
picutre_y1 = 960 # 左上角y坐标
picutre_x2 = 1620 # 右下角x坐标
picutre_y2 = 1020 # 右下角y坐标

# 程序参数设置 若不会则保持原样

VIDEO_SIMILAR = 0.05 # 图像方差


# 图像方差计算
def cal_stderr(img,imgo = None):
    if imgo is None:
        return (img ** 2).sum() / img.size
    else:
        similar  = ((img - imgo) ** 2).sum() / img.size
        return similar

# 切割图片
def slip_picture1(image) :
    image = image[picutre_y1:picutre_y2,picutre_x1:picutre_x2]
    return image

# 合并图片
def merge_image(images):
    image = images[0]
    for i in range(images.__len__()):
        if i == 0:
            continue
        image = numpy.vstack((image,images[i]))
    return image

# 保存图片
def save_image(image,start_time,current_time):
    if not os.path.exists(VIDEO_SVAE_PATH) :
        os.mkdir(path=VIDEO_SVAE_PATH)
        print("创建文件夹"+VIDEO_SVAE_PATH)
    timeline = format_time(start_time)+"_"+format_time(current_time)
    cv2.imwrite(VIDEO_SVAE_PATH + str(timeline) + ".jpg", image)
    return

# 时间格式化
def format_time(second):
   m,s = divmod(second,60)
   h,m = divmod(m,60)
   return str(h)+"-"+str(m)+"-"+str(s)

def vidoe_sub():
    success = True
    last_frame = None
    current_frame = 1
    imglist = []
    start_frames = 1
    save_frame = None

    videoCap = cv2.VideoCapture(VIDEO_PATH)
    # 帧频
    fps = videoCap.get(cv2.CAP_PROP_FPS)
    # 视频总帧数
    total_frames = int(videoCap.get(cv2.CAP_PROP_FRAME_COUNT))
    # 图像尺寸
    image_size = (int(videoCap.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(videoCap.get(cv2.CAP_PROP_FRAME_WIDTH)))

    VIDEO_HEGITH = image_size[0]
    VIDEO_WITH = image_size[1]

    if picutre_x1 < 0 or picutre_x1 > VIDEO_WITH or picutre_x1 > picutre_x2:
        print("视频截取宽度设置不正确")
        return

    if picutre_y1 < 0 or picutre_y2 > VIDEO_HEGITH or picutre_y1 > picutre_y2:
        print("视频截取高度设置不正确")
        return

    while success:
        success, frames = videoCap.read()
        current_frame = current_frame + 1
        if not success:
            if imglist.__len__() != 0:
                image = merge_image(imglist)
                save_image(image, int(start_frames / fps), int(current_frame / fps))
            print("完成")
            break

        # 图片预处理
        frames = slip_picture1(frames)

        frames_gray = cv2.cvtColor(frames, cv2.COLOR_BGR2GRAY)
        thresh = 128  # 阈值设置
        _, frames_gray = cv2.threshold(frames_gray, thresh, 255, cv2.THRESH_BINARY)
        # cv2.imwrite(VIDEO_SVAE_PATH+str(current_frame)+".jpg",frames)

        if SAVE_AS_GRAY:
            save_frame = frames_gray
        else:
            save_frame = frames

        if (last_frame is None):
            imglist.append(save_frame)
            last_frame = frames_gray
            continue

        similary = cal_stderr(frames_gray)
        if similary == 1 or similary == 0:
            continue

        if cal_stderr(last_frame, frames_gray) > VIDEO_SIMILAR:
            last_frame = frames_gray
            imglist.append(save_frame)
            if imglist.__len__() == IMAGELISTSIZE:
                image = merge_image(imglist)
                save_image(image, int(start_frames / fps), int(current_frame / fps))
                start_frames = current_frame
                imglist.clear()
                print("保存一张 进度 : (%s/100) " % int(current_frame * 100 / total_frames))


if __name__ == '__main__':
    vidoe_sub()