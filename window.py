import sys
import os
# os.putenv("IMAGEIO_FFMPEG_EXE", os.getcwd() + 'ffmpeg.win32.exe')
# os.environ['IMAGEIO_FFMPEG_EXE'] = os.getcwd() + '/moviepy/ffmpeg.win32.exe'


import basic_ui
from timeline import AnotherTimeline, Communicate
from PyQt4 import QtGui, QtCore
from PyQt4.phonon import Phonon
import time
import textEditor
import videoProcessing
import upload



DELAY = 100 * 1 #  5 seconds in milli-seconds

class Window(QtGui.QMainWindow):


    def __init__(self):
        super(Window, self).__init__()
        self.c = Communicate() 
        self.timeline = AnotherTimeline( self, 80, {"w" : 450, "h" : 50, "x" : 280, "y" : 450} )
        self.bannerAndText = False
        self.hasBanner = False
        self.bannerWidget = None
        self.publishWidget = None
        self.tagsWidget = None
        self.file = None
        self.startTimeInSec = self.endTimeInSec = 0
    
    def setup_connections( self, ui ) :
        self.ui = ui
        ui.playButton.clicked.connect(self.start_playback)
        ui.pauseButton.clicked.connect(self.pause_playback)
        ui.stopButton.clicked.connect(self.stop_playback)
        ui.seekSlider.setMediaObject(ui.videoPlayer.mediaObject())
        ui.volumeSlider.setAudioOutput(ui.videoPlayer.audioOutput())
        ui.nextBtn.clicked.connect(self.nextButtonToogle)
        ui.startTimeWidget.timeChanged.connect( self.moveBannerInTimeline )
        ui.endTimeWidget.timeChanged.connect( self.moveBannerInTimeline )
        #ticker
        ui.videoPlayer.mediaObject().tick.connect(self.tick)
        self.c.updateBW[int].connect(self.timeline.setValue)
        self.ui.nextBtn.setEnabled(False)
        #disabling stuff at init
        self.ui.bannerBox.hide()
        self.ui.bannerPic.hide()


    def paintEvent(self, e):
        self.timeline.paintEvent(e )


   
    def tick(self, time):
        self.timeline.my_range = self.ui.videoPlayer.mediaObject().totalTime() / 1000  #converting millisecond to second
        if self.errorConditionsBannerTime() is True : #check for errors
            return

        # video width and height
        self.videoWidth = self.ui.videoPlayer.videoWidget().sizeHint().width()
        self.videoHeight = self.ui.videoPlayer.videoWidget().sizeHint().height()

        displayTime = time / 1000  #seconds
        self.c.updateBW.emit(displayTime)        
        self.repaint()

    def open_file( self) :
        file = QtGui.QFileDialog.getOpenFileName(self, 'Open movie file')
        self.file = os.path.normpath(unicode(file)) 
        mediaSource = Phonon.MediaSource( self.file )
        self.ui.videoPlayer.load( mediaSource )
        print self.file
        self.ui.videoPlayer.play() #start playback auto so that video data gets populated.
        self.ui.videoPlayer.mediaObject().stateChanged.connect(self.playbackSupported)

    def playbackSupported(self, state):
        if state == Phonon.ErrorState :
            print "Error. Video format not supported. Install proper codecs"
            QtGui.QMessageBox.critical(self, "Error in playback", "Video format not supported. Install proper codecs.")
        else:
            self.ui.videoPlayer.mediaObject().stateChanged.disconnect(self.playbackSupported)
            self.ui.nextBtn.setEnabled(True)





    def start_playback( self) :
        if self.ui.videoPlayer.mediaObject().hasVideo() is False and self.bannerAndText is False:
            self.open_file()
        else :
            self.ui.videoPlayer.play()

    def pause_playback( self) :
        
        self.ui.videoPlayer.pause()

    def stop_playback( self) :
        self.ui.videoPlayer.stop()
        self.ui.videoPlayer.mediaObject().clear() #remove media from video player
        self.ui.nextBtn.setEnabled(False)

    def moveBannerInTimeline(self) : 
        if self.errorConditionsBannerTime( takeAction = False ) is False : 
            self.startTimeInSec = self.ui.startTimeWidget.time().hour() * 3600 + self.ui.startTimeWidget.time().minute() * 60 + self.ui.startTimeWidget.time().second()
            self.endTimeInSec = self.ui.endTimeWidget.time().hour() * 3600 + self.ui.endTimeWidget.time().minute() * 60 + self.ui.endTimeWidget.time().second()
            self.timeline.setBannerDuration( self.startTimeInSec, self.endTimeInSec )
            self.repaint()


    def nextButtonToogle(self) :
        self.pause_playback()
        if self.bannerAndText is False :
                self.bannerWidget = textEditor.showBannerandText( self)
                self.bannerWidget.setScaleFactor( self.videoWidth, self.videoHeight )
                #banner and text
                self.bannerWidget.closeApp.connect( self.destroying_bannerWidget ) #connecting destructor to signal
                self.bannerAndText = True

        elif self.bannerAndText is True :
                self.ui.bannerBox.show()
                self.ui.bannerPic.show()
                self.ui.startTimeWidget.setTime(QtCore.QTime(0,0,0,0))
                self.ui.endTimeWidget.setTime(QtCore.QTime(0,0,0,0))
                self.ui.progressBox.setTitle("Step 3/5")
                self.ui.nextLabel.setText("Next")
                self.ui.nextBtn.setText("Get tags")
                self.ui.nextBtn.clicked.connect( self.showTagsWindow )
                self.ui.stopButton.setEnabled(False)


        self.repaint()

    def destroying_bannerWidget(self) :
        if self.bannerWidget is not None :
            self.setGeometry( self.bannerWidget.geometry() )
            self.show()
            self.bannerWidget = None
            self.nextButtonToogle()


    def showTagsWindow(self) :
        if self.errorConditionsBannerTime() is False :
            self.tagsWidget = upload.showUpload(self)
            self.tagsWidget.closeApp.connect( self.destroytagsWidget ) #connecting destructor to signal
        


    def showPublishWidget(self) :
        num_videos = 1
        if self.string_of_tags :
            num_videos = len(self.string_of_tags.split(","))
        
        if self.hasBanner is True :
            imgLoc = os.getcwd() + "/output.png"
        else :
            imgLoc = None
        self.publishWidget = videoProcessing.showProcessing( self, videoLocation = self.file, numVideos=num_videos, \
                                        tags = self.string_of_tags, t1=self.startTimeInSec, t2=self.endTimeInSec, \
                                        x=0, y=0, ImageLocation=imgLoc)
        self.publishWidget.closeApp.connect( self.destroyPublishWidget ) #connecting destructor to signal

    def destroyPublishWidget(self):
        self.publishWidget = None
    
    def destroytagsWidget(self):
        self.tagsWidget = None
        
    

    def errorConditionsBannerTime(self, takeAction = True) :
        if any( [ self.ui.startTimeWidget.time() > QtCore.QTime(0,0,0,0).addMSecs(self.timeline.my_range * 1000), self.ui.endTimeWidget.time() > QtCore.QTime(0,0,0,0).addMSecs(self.timeline.my_range * 1000 )] ) :
               if takeAction is True :
                   self.stop_playback()
                   print "Error. Start or End time for banner is more than video's length."
                   QtGui.QMessageBox.critical(self, "Error in playback", "Start or End time for banner is more than video's length.")
               return True
        
        if any( [ self.ui.startTimeWidget.time() > self.ui.endTimeWidget.time()] ) :
               if takeAction is True :
                   self.stop_playback()
                   print "Error. Start time cannot be more than the  End time."
                   QtGui.QMessageBox.critical(self, "Error in playback", " Start time cannot be more than the  End time.")
               return True

        return False

    def closeEvent(self, event) :
        if self.bannerWidget is not None :
            self.bannerWidget.closeEvent(event)
        if self.publishWidget is not None :
            self.publishWidget.closeEvent(event)
        if self.tagsWidget is not None :
                self.tagsWidget.closeEvent(event)


def run():
    app = QtGui.QApplication(sys.argv)
    MainWindow = Window()
    ui = basic_ui.Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    MainWindow.setup_connections(ui)
    #QtGui.QApplication.setStyle("cleanlooks")
    sys.exit(app.exec_())


run()