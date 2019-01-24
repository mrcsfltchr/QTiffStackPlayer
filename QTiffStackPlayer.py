from qtpy import QtCore, QtWidgets,QtGui

import qimage2ndarray as qnd
import tifffile as tf


from qtpy.QtWidgets import QWidget,QApplication,QSlider,QMainWindow,QLabel,QGridLayout,QLineEdit,QDoubleSpinBox,QVBoxLayout,QHBoxLayout,QPushButton,QSizePolicy, QAction, QFileDialog,QSpinBox, QFrame
from qtpy.QtCore import QTimer, Qt, QDir
import numpy as np
import sys
import os


class QTiffStackPlayer(QMainWindow):
    
    #Main Window is also going to act as the controller. 
    
    
    def __init__(self,parent = None):
        super(QTiffStackPlayer,self).__init__(parent)
        
        self.setWindowTitle('Tiff Stack Player')
        
        self.videoviewer = QTiffStackView()
        #self.videoviewer.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
        
        #backend model (conforming to MVC design pattern)
        
        
        self.model = QTiffStackModel()
        
        #as controller this class contains the video index
        self.index = 0
        self.counterconnected = False
        #Create new action
        
        openAction = QAction('&Open',self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open movie')
        openAction.triggered.connect(self.openFile)
        
        #Create exit action
        
        exitAction = QAction('&Exit',self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.exitCall)
        
        #Create menu bar and add action
        #QMainWindow has a default Menu Bar attribute accessible by calling self.menuBar()
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)
        
        
        #add an error label
        
        errorLabel = QLabel()
        #This function call below sets the policy determining how the error label may be shrunk and expanded by the parent window. Syntax is 'QWidget.setSizePolicy (self, QSizePolicy.Policy hor, QSizePolicy.Policy ver)'
        errorLabel.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Maximum)
        
        layout = QVBoxLayout()
        self.setCentralWidget(self.videoviewer)
        
        #connect the signals from the viewer to the slots on the controller.
        
        self.videoviewer.frametimer.timeout.connect(self.getFrame)
        self.videoviewer.frametimer.timeout.connect(self.updateCounter)
        
        self.videoviewer.slideBar.valueChanged.connect(self.sliderChanged)
        self.videoviewer.slideBar.valueChanged.connect(self.updateCounter)
        self.videoviewer.play.clicked.connect(self.whenButtonPressed)
        
        self.videoviewer.counter.valueChanged.connect(self.counterChanged)
        self.counterconnected = True       

        self.show()
    def openFile(self):
        
        #called when user clicks on Open or presses ctrl+o
        #opens filedialog and finds file
        #if filename is not None try and openwith tifffile library and store in videoviewer property 'frames'
        #currently only .ome.tif image stacks are supported.
        
        fileName, _ = QFileDialog.getOpenFileName(self,"Choose Video or Image Stack",QDir.homePath())
        

   
        if self.model is None:
            self.model = QTiffStackModel()
            
        
        self.model.addFrames(fileName)
                  
        if self.model.frames is not None:
            self.videoviewer.updateRanges(self.model.videolength-1)
            
            
            
    def exitCall(self):
        sys.exit(app.exec_())
        

     
    def getFrame(self):
        
        #each time this is called the frame is incremented. 
        self.index +=1
        
        if self.model.frames is None:
            msgbox = QtWidgets.QMessageBox()
            msgbox.setText('No frames have been added!')
            msgbox.exec_()
         
        elif self.index < self.model.videolength:
            
            self.videoviewer.frame_view.activeframe = self.model.frames.asarray(self.index)
            self.videoviewer.frame_view.update()
        else:
            self.videoviewer.frametimer.stop()
            self.index -=1
            
         
    def sliderChanged(self):
        if self.videoviewer.frametimer.isActive():
            self.videoviewer.frametimer.stop()
            self.videoviewer.counter.valueChanged.connect(self.counterChanged)
            self.counterconnected = True
        #have written get_frame() such that every time it is called the video index is incremented before continuing. Can't be bothered to change this. So before calling it, in order to make the slidebar value and frame number of frame displayed the same we -1.
        self.index = self.videoviewer.slideBar.value() -1
        self.getFrame()
    
    def whenButtonPressed(self):
        
        if not self.videoviewer.frametimer.isActive():
            
            if self.counterconnected:
                self.videoviewer.counter.valueChanged.disconnect(self.counterChanged)
                self.counterconnected = False
            self.videoviewer.frametimer.start()
        else:
            self.videoviewer.frametimer.stop()
            if not self.counterconnected:
                self.videoviewer.counter.valueChanged.connect(self.counterChanged)
                self.counterconnected = True   
    def updateCounter(self):
        
        self.videoviewer.counter.setValue(self.index)
        
        
    def counterChanged(self):
        self.videoviewer.slideBar.setValue(self.videoviewer.counter.value())
        
class QTiffStackModel():
    
    def __init__(self,frames = None):
        
        self.frames = frames
        
    def addFrames(self,fileName):
        
        if fileName != '' and fileName[-4:] == '.tif':
            
                
        
            self.frames = tf.TiffFile(fileName) 
    
        #upon loading frames also store "meta data" i.e video length as this will be useful later
        
            self.videolength = self.frames.imagej_metadata['frames']
        
    
    
class QTiffStackView(QWidget):
    #the view which the user of the videoviewer sees.
    #This class contains relevant 'client side' attributes e.g. buttons to get a frame, a slide bar and a timer. These attributes submit requests to the QTiffStackController to give the next frame etc. The controller returns either the requested frame or an error message
    
    
    def __init__(self):
        super(QTiffStackView,self).__init__()
        #add the image display. This is a subclass of QLabel, where paintEvent is overriden.
        self.frame_view = FrameView()
        
        #self.frame_view.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        
        #add the slide bar which allows the user to manual flick through 
        
       
        self.slideBar = QSlider(Qt.Horizontal)
        self.slideBar.setTickPosition(QSlider.TicksAbove)
        self.slideBar.setTracking(True)
        self.slideBar.setTickInterval(100)
        
        #add a counter which displays the frame which is currently displayed
        self.counter = QSpinBox()
        self.counter.setSingleStep(1)
        self.counter.setRange(self.slideBar.minimum(),self.slideBar.maximum())
        
        #self explanatory
        self.play = QPushButton('Play')
        
        #when play button is pressed the timer takes control of the displaying of frames
        self.frametimer = QTimer()
        
        frame_rate = 30
        self.frametimer.setInterval(frame_rate)
        
        #Add a sublayout to align the slidebar and frame counter next to eachother
        slidelyt = QHBoxLayout()
        slidelyt.addWidget(self.slideBar)
        slidelyt.addWidget(self.counter)
        
        
        #Add the main layout for the widget
        lyt = QVBoxLayout()
        
        lyt.addWidget(self.frame_view)
        lyt.addLayout(slidelyt)
        lyt.addWidget(self.play)
        
        self.setLayout(lyt)
        
      
    def updateRanges(self,maximum):
        
        assert type(maximum) == int
        
        self.slideBar.setMaximum(maximum)
        self.counter.setRange(self.slideBar.minimum(),self.slideBar.maximum())
        
        
        
class FrameView(QLabel):
    
    #subclass of QLabel. the paintEvent function, which updates the display when the eventloop registers an update, has been overriden. 
    #Using a third party library we can convert the numpy array image data into a QPixmap which may be 'painted' on to the Label.
    
    def __init__(self, parent = None):
        super(FrameView,self).__init__()
        
        self.activeframe = None
        
        #self.setFrameStyle(QFrame.Panel|QFrame.Sunken)
        
        
        
    def paintEvent(self, e):
        
        super().paintEvent(e)
        
        
        
        if self.activeframe is not None:
            maxintens = np.max(self.activeframe)
            img = qnd.gray2qimage(self.activeframe,normalize = (0,maxintens))
        
            pix = QtGui.QPixmap.fromImage(img)
            
            pix = pix.scaled(self.size(),Qt.KeepAspectRatio)
            self.setPixmap(pix)
        else:
            self.setText('No video displayed')
            
        
        
        
if __name__ == '__main__':
    
    
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
        
    else:
        app = QtWidgets.QApplication.instance()
        
        
    player = QTiffStackPlayer()
    
    app.exec_()
    

       
  