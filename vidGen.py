#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import cv2
import random
import datetime
from PIL import *
import numpy as np
from moviepy.editor import *

def compare_image(imageA, imageB):
    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
    
    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return err

def GivemMeARandomNumber(count):
    return random.randrange(1,count)

def destroyAllFrames(pathOfVideo,count): 
    for i in range(1,count+1):
        pathToremove = os.path.join(pathOfVideo,'frame%d.jpg' %i)
        if os.path.isfile(pathToremove):
            os.remove(pathToremove)

#Function to generate an array of frames from the video
def GenerateFrames(videoLocation):
    vidcap = cv2.VideoCapture(videoLocation) 
    success,image = vidcap.read()
    count = 1
    vidDirectory = os.path.dirname(videoLocation)

    while (count < 200) and (success): 
        success,image = vidcap.read()
        frame_read = os.path.join(vidDirectory,'frame%d.jpg' %count)
        cv2.imwrite(frame_read, image)     # save frame as JPEG file
        if cv2.waitKey(10) == 27:                     # exit if Escape is hit
            break
        count += 1

    cv2.destroyAllWindows()
    vidcap.release()
    return count

#Gives an array of numbers but those numbers corresponds to unidentical frames
def GiveUnidenticalFrames(numVideos,vidDirectory,FrameCount):
    RandomFrame = []
    RandomFrameData = GivemMeARandomNumber(FrameCount)
    RandomFrame.append(RandomFrameData)
    Match = False

    if numVideos == 1:
        return RandomFrame
    else:
        for i in range(0,numVideos):
            RandomFrameData = GivemMeARandomNumber(FrameCount)
            for imgNum in range(0,len(RandomFrame)):
                imgA = cv2.imread(os.path.join(vidDirectory,'frame%d.jpg' %RandomFrame[imgNum]))
                imgB = cv2.imread(os.path.join(vidDirectory,'frame%d.jpg' %RandomFrameData))
                mse = compare_image(imgA,imgB)
                if mse < 2000:
                    Match = True
                    break
            if(Match is False):
                RandomFrame.append(RandomFrameData)
            else:
                i = i-1
    return RandomFrame

def GenerateTheVideo(videoLocation, numVideos=1, t1=0, t2=0, x=0, y=0, ImageLocation=None ):
    FrameCount = GenerateFrames(videoLocation)
    vidDirectory = os.path.dirname(videoLocation)
    RandomFrame = GiveUnidenticalFrames(numVideos,vidDirectory,FrameCount)
    durationOfImage = GivemMeARandomNumber(5)

    for numVideo_i in range(0,numVideos): 
        if ImageLocation is not None :
            OverlayImage = ImageLocation #Location Of Image/Banner
            ovrImgClip = ImageClip(OverlayImage,duration=t2-t1) #Create a clip for the duration start
            

        frame_to_use = os.path.join(vidDirectory,'frame%d.jpg' %RandomFrame[numVideo_i])
        clip1 = ImageClip(frame_to_use,duration=durationOfImage)
        clip2 = VideoFileClip(videoLocation)
        if ImageLocation is not None :
            Video = CompositeVideoClip([clip1,clip2.set_start(durationOfImage).crossfadein(1), \
                    ovrImgClip.set_start(t1+durationOfImage).set_pos((x,y))]) #Overlay the video
        else :
            Video = CompositeVideoClip([clip1,clip2.set_start(durationOfImage).crossfadein(1)]) #Overlay the video            
        
        newFileLocation = os.path.join(vidDirectory,'new_video_kind%d.mp4' %RandomFrame[numVideo_i])
        Video.write_videofile(newFileLocation,fps=25)
    
    destroyAllFrames(vidDirectory,FrameCount)

if __name__ == "__main__":
    # main()
    
    print datetime.datetime.now()
    GenerateTheVideo("/home/pratika/Downloads/my_composition.mp4", 2 ) #path where the video is located
    print datetime.datetime.now()

