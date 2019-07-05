#!/usr/bin/env python
# coding=utf-8
##
# @file rosbag_view.py
# @brief simple tool base on pyqt for plot rosbag data, there is no need to import the msg package, and is more flexale than rqt_bag
# @author daibilin@yeah.net
# @version 1.0.0
# @date 2019-07-04



from pyqtgraph.Qt import QtCore, QtGui
from rosbag_widget import RosBagWidget

app = QtGui.QApplication([])

# Create main window with grid layout
win = QtGui.QMainWindow()
win.setWindowTitle('ros bag: plot')
cw = QtGui.QWidget()
win.setCentralWidget(cw)
layout = QtGui.QGridLayout()
cw.setLayout(layout)

rw = RosBagWidget()
layout.addWidget(rw, 0, 0)

win.resize(600,600)
win.show()


# Start Qt event loop unless running in interactive mode or using pyside.
##
# @brief 
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
