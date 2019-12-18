
import cv2
import time
import numpy as np
import cupy as cp
from PIL import Image
import sys
import asyncio
import base64
import json
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED, FIRST_COMPLETED
import glob
import traceback
import os

IsOdd = 0
BasePath = ""

def main():
    global IsOdd
    global BasePath
    FileArray = []
    print('正在获取文件')
    T1 = time.time()
    if(len(sys.argv) > 1):
        if(os.path.isdir(sys.argv[1])):
            BasePath = sys.argv[1]
            FileArray = SearchFile()
        else:
            BasePath = os.getcwd()
            FileArray = SearchFile()
    else:
        BasePath = os.getcwd()
        FileArray = SearchFile()
    print("一共",FileArray.shape[0],"个有效项目,",FileArray.shape[0] * 2,"张原图")
    T2 = time.time()
    print("耗时:",round(T2 - T1,3),"秒")
    executor = ThreadPoolExecutor(max_workers=30)
    all_task = [executor.submit(Run, (value)) for value in FileArray]
    wait(all_task, return_when=ALL_COMPLETED)
    T3 = time.time()
    print("阶段耗时:",round(T3 - T2,3),"秒")
    print("总耗时:",round(T3 - T1,3),"秒")
    print("均速:",round(((FileArray.shape[0]) / (T3 - T2)),3),"张/每秒")
    print("处理结束")

def Run(Dict):
    global BasePath
    global Threads
    (RGB,Alpha) = Dict
    RGBImage = cv2.imread(RGB,cv2.IMREAD_UNCHANGED)#cv2.IMREAD_UNCHANGED
    AlphaImage = cp.array(cv2.imread(Alpha))
    RGBImage = cp.array(cv2.cvtColor(RGBImage, cv2.COLOR_BGRA2RGBA))
    if(RGBImage.shape[0] > AlphaImage.shape[0]):
        AlphaImage = cp.kron(AlphaImage, cp.ones((2,2,1)))
        NewAlpha = cp.ones((RGBImage.shape[0],RGBImage.shape[0],1))
    elif(RGBImage.shape[0] < AlphaImage.shape[0]):
        RGBImage = cp.kron(RGBImage, cp.ones((2,2,1)))
        NewAlpha = cp.ones((AlphaImage.shape[0],AlphaImage.shape[0],1))
    else:
        NewAlpha = cp.ones((1024,1024,1))
    NewAlpha[:,:,0] = (AlphaImage[:,:,0] + AlphaImage[:,:,1] + AlphaImage[:,:,2]) / 3
    RGBImage[:,:,3:] = AlphaImage[:,:,:1]
    im = Image.fromarray(cp.asnumpy(RGBImage))
    #im = Image.fromarray(RGBImage)\
    im.save(BasePath + "/OutPut/" + RGB)

def SearchFile():
    global BasePath
    files = np.asanyarray(os.listdir(BasePath))
    FileArray = []
    for FileNameId in range(files.shape[0]):
        if "[alpha]" in files[FileNameId]:
            if (files[FileNameId].split("[alpha]")[0] + files[FileNameId].split("[alpha]")[1]) in files:
                FileArray.append([files[FileNameId].replace("[alpha]",""),files[FileNameId]])
    return np.asanyarray(FileArray)

print("程序已启动....")
print("正在引导主函数")
main()
