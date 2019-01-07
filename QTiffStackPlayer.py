from qtpy import QtCore, QtWidgets,QtGui

import qimage2ndarray as qnd
import tifffile
from qtpy.QtCore import 

from qtpy.QtWidgets import QWidget,QApplication,QSlider,QMainWindow,QLabel,QGridLayout,QLineEdit,QDoubleSpinBox,QVBoxLayout,QPushButton,QSizePolicy, QAction, QFileDialog
from qtpy.QtCore import QTimer, Qt, QDir
import numpy as np
import sys
import os


class QTiffStackPlayer(QMainWindow):
    
    def __init__(self,parent = None):
        super(QTiffStackPlayer,self).__init__(parent)
        
        self.setWindowTitle('Tiff Stack Player')
        
        self.videoviewer = QTiffStackView('&Open',self)
        self.videoviewer.setSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding)
        
        #backend controller and model (conforming to MVC design pattern)
        
        self.videocontroller = None
        self.model = None
        
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
        layout.addWidget(self.videoviewer)
        layout.addWidget(errorLabel)
        
        
    def openFile(self):
        
        #called when user clicks on Open or presses ctrl+o
        #opens filedialog and finds file
        #if filename is not None try and openwith tifffile library and store in videoviewer property 'frames'
        #currently only .ome.tif image stacks are supported.
        
        fileName, _ = QFileDialog.getOpenFileName(self,"Choose Video or Image Stack",QDir.homePath())
        
        if fileName != '' and fileName[-4:] == '.tif':
            with tf.TiffFile(fileName) as tif:
                frames = tif.asarray()
                
        
        if self.model is None:
            self.model = QTiffStackModel(frames)
            
        else:
            self.model.addFrames(frames)
                               
            
            
    def exitCall(self):
        sys.exit(app.exec_())
        
        
    
class QTiffStackModel():
    
    def __init__(self,frames = None):
        
        self.frames = frames
        
    def addFrames(frames = None)
    
        self.frames = frames 
    
    
class QTiffStackView(QWidget):
    #the view which the user of the videoviewer sees.
    #This class contains relevant 'client side' attributes e.g. buttons to get a frame, a slide bar and a timer. These attributes submit requests to the QTiffStackController to give the next frame etc. The controller returns either the requested frame or an error message
    
    
    def __init__(self):
        
        #add the image display. This is a subclass of QLabel, where paintEvent is overriden.
        frame_view = FrameView()
        
        frame_view.setSizePolicy(QSizePolicy.Expanding)
        
        #add the slide bar which allows the user to manual flick through frames
        self.slideBar = QSlider(Qt.Horizontal)
        self.slideBar.setTickPosition(QSlider.TicksAbove)
        self.slideBar.setTracking(True)
        self.slideBar.setTickInterval(100)
        
        #add a counter which displays the frame which is currently displayed
        self.counter = QSpinBox()
        self.counter.setSingleStep(1)
        self.counter.setRange(self.slideBar.minimum(),self.slideBar.maximum())
        
        #self explanatory
        play = QPushButton('Play')
        
        #when play button is pressed the timer takes control of the displaying of frames
        frametimer = QTimer()
        
        frame_rate = 30
        frametimer.setInterval(frame_rate)
        
        #Add a sublayout to align the slidebar and frame counter next to eachother
        slidelyt = QHBoxLayout()
        slidelyt.addWidget(self.slideBar)
        slidelyt.addWidget(self.counter)
        
        
        #Add the main layout for the widget
        lyt = QVBoxLayout()
        
        lyt.addWidget(frame_view)
        lyt.addLayout(slidelyt)
        lyt.addWidget(play)
        
        self.setLayout(lyt)
        
        
        
        
        
class FrameView(QLabel):
    
    #subclass of QLabel. the paintEvent function, which updates the display when the eventloop registers an update, has been overriden. 
    #Using a third party library we can convert the numpy array image data into a QPixmap which may be 'painted' on to the Label.
    
    def __init__(self, parent = None):
        super().__init__(self)
        
        self.activeframe = None
        
    def paintEvent(self, e):
        super().paintEvent(e)
        
        qp = QtGui.QPainter(self)
        
        maxintens = np.max(self.activeframe)
        img = qnd.gray2qimage(self.activeframe,normalize = (0,maxintens))
        
        pix = QtGui.QPixmap.fromImage(img)
    
        
        
       
  