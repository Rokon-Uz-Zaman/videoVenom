#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore
import banner_ui
from size_handler import SizeHandler
import preview


class BannerandTextClass(QtGui.QWidget) :

    SCALE_FACTOR = 1  #how original video is scaled compared to frame in this widget window
    closeApp = QtCore.pyqtSignal() #signal , slot to be with caller

    def __init__(self, ui, sizeHandler = None):
        super(BannerandTextClass, self).__init__()
        self.ui = ui
        self.sizeHandler = sizeHandler
        self.show_banner = False
        self.file = None
        self.color = None
        self.font = None
        self.preview = None


    def initUI(self):      
        self.ui.bannerText.connect(self.ui.bannerText, QtCore.SIGNAL("textChanged(QString)"),
                    self.labelUpdate)
        self.ui.fontBtn.clicked.connect(self.font_choice)
        self.ui.colorBtn.clicked.connect(self.color_choice)
        self.ui.bannerBtn.clicked.connect( self.bannerToogle )
        self.ui.previewBtn.clicked.connect( self.preview_banner )
        self.ui.nextBtn.clicked.connect( self.closeWidget )

        self.bounds = QtCore.QRect(self.ui.frame.geometry().x() + 10, self.ui.frame.geometry().y() + 10, 250, 50)
        self.setMouseTracking(True)  #mouse move will always be called, unlike earlier when it meant drag
        self.ui.frame.setMouseTracking(True)
        self.ui.bannerLabel.setMouseTracking(True)

    def setScaleFactor( self, original_width, original_height ) :
        #adjusting the workspace
        self.SCALE_FACTOR = (1.0 * original_height) / self.ui.frame.height()
        self.ui.frame.setFixedWidth( original_width / self.SCALE_FACTOR )            



    def labelUpdate(self):
        self.ui.bannerLabel.setText(self.ui.bannerText.text())

    def font_choice(self):
        self.font, valid = QtGui.QFontDialog.getFont()
        
        if valid:
            self.ui.bannerLabel.setFont(self.font)

    def color_choice(self):
        self.color = QtGui.QColorDialog.getColor()
        self.ui.bannerLabel.setStyleSheet("QLabel { color: %s}" % self.color.name())

    def file_open(self):
        self.file = QtGui.QFileDialog.getOpenFileName(self, 'Open File')
        if self.file.isEmpty() :
            self.file = None
        return self.file

    def file_close(self):
        self.file = None

    def preview_banner(self) :
            self.preview = preview.showPreview( self )
            self.preview.closeApp.connect( self.destroying_preview ) #connecting destructor to signal
            self.preview.moveStuff( self.SCALE_FACTOR, self.ui.frame.geometry(), self.bounds, self.ui.bannerLabel.geometry(), self.ui.bannerLabel.text(), self.font, self.color, self.file )

    def destroying_preview(self) :
        self.preview = None
            
    def bannerToogle(self) :
        if self.show_banner is False :
            if self.file_open() is not None :
                self.show_banner = True
                self.ui.bannerBtn.setText("Remove banner")
        elif self.show_banner is True :
            self.file_close()
            self.show_banner = False
            self.ui.bannerBtn.setText("Add banner")
        self.repaint()

    def paintEvent(self, event):
        if self.sizeHandler is not None and self.sizeHandler.object == "rectangle" :
            self.bounds = self.sizeHandler.bounds

        if self.show_banner is True :
            qp = QtGui.QPainter()
            qp.begin(self)
            color = QtGui.QColor(0, 0, 0)
            color.setNamedColor('#d4d4d4')
            qp.setPen(color)
            qp.setBrush(QtGui.QColor("Red"))
            qp.drawRect(  self.bounds )
            qp.end()

        if self.sizeHandler is not None :
            self.sizeHandler.paintEvent( event)

    def mousePressEvent(self, event):

        if self.ui.bannerLabel.geometry().contains( event.pos() ) : #label
            if self.sizeHandler is None or self.sizeHandler.bounds != self.ui.bannerLabel.geometry() :
                self.sizeHandler = SizeHandler(self, self.ui.bannerLabel)
                # self.sizeHandler.enable_Hresize = self.sizeHandler.enable_Vresize = False  #disabling handlers
            self.sizeHandler.mousePressEvent(event)

        elif self.show_banner is True and self.bounds.contains( event.pos()) :
            if self.sizeHandler is None or self.sizeHandler.bounds != self.bounds : #selection
                self.sizeHandler = SizeHandler(self, "rectangle", self.bounds)
            self.sizeHandler.mousePressEvent(event)

        self.repaint()
   
    def mouseReleaseEvent(self, event):
        if self.sizeHandler is not None :
            self.sizeHandler.mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self.sizeHandler is not None :
            self.sizeHandler.mouseMoveEvent(event)
            if self.sizeHandler.can_Hresize is True or \
                self.sizeHandler.can_Vresize is True or \
                self.sizeHandler.can_move is True:

                self.repaint()

    def closeEvent(self, event) :
        if self.preview is not None :
            self.preview.closeEvent(event)
        self.closeWidget()


    def closeWidget(self) :
        self.closeApp.emit()
        self.close()

      

def showBannerandText( caller  ) :
    ui = banner_ui.Ui_Form()
    widget = BannerandTextClass(ui)
    ui.setupUi(widget)
    widget.initUI()
    widget.caller = caller #setting main window as caller here for accessing variables
    if caller is not None :
        widget.caller.hide()
        widget.setGeometry( caller.geometry() )
    widget.show()
    widget.show()
    return widget





def main():
    
    app = QtGui.QApplication(sys.argv)
    app.file = None
    widget = showBannerandText( None )    
    widget.setScaleFactor(1024, 768)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
