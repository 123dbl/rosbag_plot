##
# @file rosbag_widget.py
# @brief 
# @author daibilin@yeah.net
# @version 1.0.0
# @date 2019-07-04


from pyqtgraph.Qt import QtCore, QtGui
from FileDialog import *
import rosbag
import pyqtgraph as pg
import os
import re
import matplotlib.pyplot as plt
from DataTreeWidget import DataTreeWidget
from pyqtgraph.parametertree import Parameter, ParameterTree, ParameterItem, registerParameterType
import time


class RosBagWidget(QtGui.QWidget):

    ##
    # @brief 
    #
    # @return 

    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.file_name = ''
        self.bag = None
        self.data = {}
        self.plot_data = {}
        self.gridLayout = None
        self.label1 = None
        self.loadBtn = None
        self.tree = None
        self.addBtn = None
        self.editBtn = None
        self.removeBtn = None
        self.plotBtn = None
        self.plotTree = None
        self.plotData = None
        self.plotwin = None
        self.plot_num = 1
        self.params = [{'type': 'group', 'name': u'plot params',
                        'children': [{'type': 'str', 'name': 'x axis name',
                                      'value': u'time(s)'},
                                     {'type': 'str', 'name': 'y axis name',
                                      'value': u'position(m)'},
                                     {'type': 'str', 'name': 'plot name',
                                      'value': u'plot name'}]}]
        self.line_mark_list = ['+-', '*-', 'o-', '^-', 's-', 'x-', '.-', 'p-', 'h-', 'd-']
        self.msg_types = []
        self.topics = {}
        self.topics_data = {}
        self.msg_types_blacklist = ['sensor_msgs/PointCloud', 'sensor_msgs/Image']
        self.setup_ui(self)

    ##
    # @brief 
    #
    # @param Form
    #
    # @return 
    def setup_ui(self, Form):
        self.setObjectName("Form")
        self.resize(217, 499)
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setVerticalSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.label1 = QtGui.QLabel("")
        self.label1.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        self.label1.setStyleSheet("border:1px solid black;")
        self.gridLayout.addWidget(self.label1, 0, 0)
        self.loadBtn = QtGui.QPushButton("...")
        self.loadBtn.setFixedWidth(20)
        self.gridLayout.addWidget(self.loadBtn, 0, 1)
        self.loadBtn.clicked.connect(self.load_file)
        self.tree = DataTreeWidget(data=self.data)
        self.gridLayout.addWidget(self.tree, 1, 0, 1, 2)
        self.addBtn = QtGui.QPushButton("")
        add_icon = QtGui.QIcon()
        add_icon.addPixmap(QtGui.QPixmap("resources/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.addBtn.setIcon(add_icon)
        self.addBtn.clicked.connect(self.add_plot)
        self.gridLayout.addWidget(self.addBtn, 0, 2)
        self.editBtn = QtGui.QPushButton("")
        edit_icon = QtGui.QIcon()
        edit_icon.addPixmap(QtGui.QPixmap("resources/edit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.editBtn.setIcon(edit_icon)
        self.editBtn.clicked.connect(self.edit_plot)
        self.gridLayout.addWidget(self.editBtn, 0, 3)
        self.removeBtn = QtGui.QPushButton("")
        remove_icon = QtGui.QIcon()
        remove_icon.addPixmap(QtGui.QPixmap("resources/remove.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.removeBtn.setIcon(remove_icon)
        self.removeBtn.clicked.connect(self.remove_plot)
        self.gridLayout.addWidget(self.removeBtn, 0, 4)
        self.plotBtn = QtGui.QPushButton("plot")
        # plot_icon = QtGui.QIcon()
        # plot_icon.addPixmap(QtGui.QPixmap("resources/plot.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        # self.plotBtn.setIcon(plot_icon)
        self.plotBtn.clicked.connect(self.plot)
        self.gridLayout.addWidget(self.plotBtn, 0, 5)
        self.plotTree = ParameterTree()
        self.plotData = Parameter.create(name='params', type='group', children=self.params)
        self.plotTree.setParameters(self.plotData, showTop=False)
        self.gridLayout.addWidget(self.plotTree, 1, 2, 1, 4)
        # self.tree2.setSizePolicity(self.tree1.width()/2, 499)
        # self.tree1.resize(setWidth(150)
        # self.tree2.setWidth(50)
        self.plotData.sigTreeStateChanged.connect(self.change)

    ##
    # @brief 
    #
    # @param param
    # @param changes
    #
    # @return 
    def change(self, param, changes):  # todo change plot params
        print("tree changes:(to do)")
        for param, change, data in changes:
            path = self.plotData.childPath(param)
            print(path)
            if path is not None:
                childName = '.'.join(path)
            else:
                childName = param.name()
            print('  parameter: %s' % childName)
            print('  change:    %s' % change)
            print('  data:      %s' % str(data))
            print('  ----------')

    ##
    # @brief 
    #
    # @param file_name
    # @param start_dir
    #
    # @return 
    def load_file(self, file_name=None, start_dir=None):
        """Load a rosbag (*.bag) file.
        """
        start = time.clock()
        if not file_name:
            if not start_dir:
                start_dir = '.'
            self.file_dialog = FileDialog(None, "Load rosbag ..", start_dir, "rosbag (*.bag)")
            # file_dialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)
            self.file_dialog.show()
            self.file_dialog.fileSelected.connect(self.load_file)
            return
        file_name = unicode(file_name)
        self.file_name = file_name
        self.label1.setText(str(file_name))
        self.file_info(file_name)
        end = time.clock()
        print("load file cost %s s" % (end - start))

    ##
    # @brief 
    #
    # @param file_name
    #
    # @return 
    def file_info(self, file_name=None):
        if not file_name:
            self.data = {}
        else:
            self.bag = rosbag.Bag(file_name)
            self.tree.setData(self.bag.get_type_and_topic_info()[1])
            # print(self.bag.get_type_and_topic_info()[1])
            bag_length = self.get_bag_length(self.bag.get_type_and_topic_info()[1])*10
            if len(file_name)*8 > bag_length:
                bag_length = len(file_name) * 8
            self.label1.setFixedWidth(bag_length)
            # clear data
            self.msg_types = []
            self.topics = {}
            self.topics_data = {}
            # print(self.get_bag_length(self.bag.get_type_and_topic_info()[1]))
            for m in self.bag.get_type_and_topic_info()[0]:
                self.msg_types.append(m)
            for t in self.bag.get_type_and_topic_info()[1]:
                if self.bag.get_type_and_topic_info()[1][t][0] not in self.msg_types_blacklist:
                    get_topic_params_cmd = "rostopic echo -b " + file_name + " -n 1 -p " + t
                    topic_parms = os.popen(get_topic_params_cmd).read()
                    topic_parms_list = self.topic_str2list(topic_parms)
                    self.topics[t] = topic_parms_list
                    get_topic_data_cmd = "rostopic echo -b " + self.file_name + " -p " + t
                    topic_data = os.popen(get_topic_data_cmd).read()
                    topic_data_list = self.topic_data_str2list(topic_data[:-1])
                    self.topics_data[t] = topic_data_list
                else:
                    print(t+"is not proper for plot")
                # print("topic_data_list", topic_data_list)
                # break

    @staticmethod
    ##
    # @brief 
    #
    # @param data
    #
    # @return 
    def get_bag_length(data):
        max_topic_len = 0
        max_topic_type_len = 0
        for topic in data:
            if len(topic) > max_topic_len:
                max_topic_len = len(topic)
            if len(data[topic][0])>max_topic_type_len:
                max_topic_type_len = len(data[topic][0])
        # print(max_topic_len, max_topic_type_len)
        return max_topic_len + max_topic_type_len


    @staticmethod
    ##
    # @brief 
    #
    # @param topic_str
    #
    # @return 
    def topic_str2list(topic_str):
        # print(len(topic_str))
        # print(topic_str)
        topic_list = []
        if len(topic_str) > 0:
            # print(topic_str[0])
            out1 = re.split('\n', topic_str)
            params = re.split(',', out1[0])
            values = re.split(',', out1[1])
            # print(len(params), len(values))
            for i in range(len(params)):
                if values[i].strip('-').replace(".", '').isdigit():
                    topic_list.append(params[i])
            # print(topic_list)
            return topic_list

    @staticmethod
    ##
    # @brief 
    #
    # @param topic_data_str
    #
    # @return 
    def topic_data_str2list(topic_data_str):
        topic_data_list = []
        if len(topic_data_str) > 0:
            out1 = re.split('\n', topic_data_str)
            for o in out1:
                data_list = re.split(',', o)
                topic_data_list.append(data_list)
            return topic_data_list

    ##
    # @brief 
    #
    # @return 
    def add_plot(self):
        if len(self.file_name):
            #print("add plot")
            self.plotwin = PlotWin(self.topics, self.plot_num)
            self.plotwin.setWindowModality(QtCore.Qt.ApplicationModal)
            self.plotwin.setGeometry(500, 500, 600, 150)
            if self.plotwin.exec_():  # accepted
                #print("ok")
                self.plot_num = self.plot_num + 1
                if len(self.plotwin.plot_name.text()) > 0:
                    self.plotwin.param['name'] = unicode(self.plotwin.plot_name.text()) + " " + unicode(self.plotwin.topic_name.currentText())
                    self.plotwin.param['type'] = 'group'
                    x = {'name': 'x', 'type': 'str', 'value': unicode(self.plotwin.field1.currentText())}
                    y = {'name': 'y', 'type': 'str', 'value': unicode(self.plotwin.field2.currentText())}
                    color = self.plotwin.colorBtn.color(mode='byte')
                    color_str = ''
                    for i in color[:-1]:
                        c = str(hex(i)).replace("0x", '')
                        if len(c) < 2:
                            c = '0' + c
                        color_str = color_str + c
                    # print(color, color_str)
                    line_color = {'name': 'line_color', 'type': 'color', 'value': color_str,
                                  'tip': "This is a color button"}
                    line_mark = {'name': 'line_mark', 'type': 'list',
                                 'values': self.line_mark_list,
                                 'value': unicode(self.plotwin.line_mark.currentText())}
                    self.plotwin.param['children'] = [x, y, line_color, line_mark]
                    self.params.append(self.plotwin.param)
                    self.plotData = Parameter.create(name='params', type='group', children=[self.plotwin.param])
                    self.plotTree.addParameters(self.plotData, showTop=False)
                else:
                    print("Please input the plot name first.")

            else:
                print("cancel")
        else:
            print("Please add bag file first!")

    ##
    # @brief 
    #
    # @return 
    def edit_plot(self):
        # print("edit plot", self.plotTree.selectedItems(), self.plotTree.currentItem())
        if hasattr(self.plotTree.currentItem(), "param"):
            print("edit plot " +
                  re.split('\'', str(getattr(self.plotTree.currentItem(), "param")))[1] + "(to do)")
            # if hasattr(getattr(self.plotTree.currentItem(), "param"), "name"):
                # print(getattr(getattr(self.plotTree.currentItem(), "param"), "name"))
        # print("%x" % id(self.params[0]))

    ##
    # @brief 
    #
    # @return 
    def remove_plot(self):
        if hasattr(self.plotTree.currentItem(), "param"):
            print("remove plot " +
                  re.split('\'', str(getattr(self.plotTree.currentItem(), "param")))[1] + "(to do)")

    ##
    # @brief 
    #
    # @return 
    def plot(self):
        print("plot")
        plots = []
        for p in self.params[1:]:
            topic_name = re.split(' ', p['name'])
            # print(topic_name[1])
            x_name = None
            y_name = None
            line_color = None
            line_mark = None
            for c in p['children']:
                if c['name'] == 'x':
                    x_name = c['value']
                elif c['name'] == 'y':
                    y_name = c['value']
                elif c['name'] == 'line_color':
                    line_color = c['value']
                elif c['name'] == 'line_mark':
                    line_mark = c['value']
            plots.append([topic_name[0], topic_name[1], x_name, y_name, line_color, line_mark])
        # print(plots)

        # plt.figure(figsize=(12, 10))
        for p in plots:
            x, y = self.get_bag_data(p)
            plt.plot(x, y, p[5], color=("#" + p[4]), label=p[0])
        plt.xlabel(self.params[0]['children'][0]['value'])
        plt.ylabel(self.params[0]['children'][1]['value'])
        plt.title(self.params[0]['children'][2]['value'])
        # plt.ylim(-1.2, 1.2)
        plt.legend(loc='upper right')
        plt.grid(True)
        # plt.savefig(gflags.FLAGS.title + '.svg', format= 'svg')
        plt.show()

    ##
    # @brief 
    #
    # @param plot_info
    #
    # @return 
    def get_bag_data(self, plot_info):
        x = []
        y = []
        plot_data = self.topics_data[plot_info[1]]
        x_index = plot_data[0].index(plot_info[2])
        y_index = plot_data[0].index(plot_info[3])
        # print(plot_data, x_index, y_index)
        for pd in plot_data[1:]:
            # print('len(pd)', len(pd))
            # print('x_index', x_index)
            # print('y_index', y_index)
            x.append(pd[x_index])
            y.append(pd[y_index])
            # break
        return x, y


class PlotWin(QtGui.QDialog):
    ##
    # @brief 
    #
    # @param topics
    # @param plot_num
    #
    # @return 
    def __init__(self, topics, plot_num):
        QtGui.QWidget.__init__(self)
        self.gridLayout = None
        self.label = None
        self.label_c = None
        self.colorBtn = None
        self.plot_name = 'plot' + str(plot_num)
        self.label11 = None
        self.label1 = None
        self.label2 = None
        self.label3 = None
        self.field1 = None
        self.field2 = None
        self.line_mark = None
        self.topic_name = None
        self.buttonBox = None
        self.axisLayout = QtGui.QGridLayout()
        self.btnhbLayout = QtGui.QHBoxLayout()

        self.plot_colors = []
        self.topics = topics
        self.topics_list = list(topics)
        self.param = {}

        self.setup_ui(self)

        if len(topics) == 0:
            print("Please import bag first!")

    ##
    # @brief 
    #
    # @param Form
    #
    # @return 
    def setup_ui(self, Form):
        self.setObjectName("Form")
        # self.resize(217, 499)
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setVerticalSpacing(0)
        self.gridLayout.setObjectName("gridLayout")

        self.label = QtGui.QLabel("Title: ")
        self.gridLayout.addWidget(self.label, 0, 0)
        self.label.setFixedWidth(40)
        self.plot_name = QtGui.QLineEdit(self.plot_name)
        self.gridLayout.addWidget(self.plot_name, 0, 1)
        self.label11 = QtGui.QLabel("Topic: ")
        self.gridLayout.addWidget(self.label11, 0, 2)
        self.label11.setFixedWidth(40)
        self.topic_name = QtGui.QComboBox()
        self.topic_name.addItems(self.topics_list)
        self.gridLayout.addWidget(self.topic_name, 0, 3)
        self.topic_name.currentIndexChanged.connect(self.combox_change)
        self.label_c = QtGui.QLabel("color:")
        self.gridLayout.addWidget(self.label_c, 0, 4)
        self.colorBtn = pg.ColorButton(color=(255, 0, 0))
        self.colorBtn.sigColorChanged.connect(self.change_color)
        self.colorBtn.setFixedWidth(30)
        self.gridLayout.addWidget(self.colorBtn, 0, 5)

        # self.label1 = QtGui.QLabel("Axes")
        # self.axisLayout.addWidget(self.label1, 0, 0)
        self.label1 = QtGui.QLabel("X-Axis: ")
        self.label1.setFixedWidth(50)
        self.axisLayout.addWidget(self.label1, 0, 0)
        self.field1 = QtGui.QComboBox()
        self.field1.addItems(self.topics[self.topics_list[0]])
        self.axisLayout.addWidget(self.field1, 0, 1)
        self.label2 = QtGui.QLabel("Y-Axis: ")
        self.label2.setFixedWidth(50)
        self.axisLayout.addWidget(self.label2, 0, 2)
        self.field2 = QtGui.QComboBox()
        self.field2.addItems(self.topics[self.topics_list[0]])
        self.axisLayout.addWidget(self.field2, 0, 3)
        self.label3 = QtGui.QLabel("line_mark: ")
        self.label3.setFixedWidth(70)
        self.axisLayout.addWidget(self.label3, 0, 4)
        self.line_mark = QtGui.QComboBox()
        self.line_mark.addItems(['+-', '*-', 'o-', '^-', 's-', 'x-', '.-', 'p-', 'h-', 'd-'])
        self.axisLayout.addWidget(self.line_mark, 0, 5)
        self.gridLayout.addLayout(self.axisLayout, 1, 0, 1, 6)

        self.buttonBox = QtGui.QDialogButtonBox()
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        # self.gridLayout.addWidget(self.buttonBox, 4, 1)
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setDefault(True)
        self.btnhbLayout.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.btnhbLayout, 2, 0, 1, 6)
        self.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self, QtCore.SLOT("accept()"))
        self.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self, QtCore.SLOT("reject()"))

    ##
    # @brief 
    #
    # @return 
    def change_color(self):
        self.plot_colors.append(self.colorBtn.color(mode='byte'))
        # print(self.plot_colors)

    ##
    # @brief 
    #
    # @return 
    def combox_change(self):
        self.field1.clear()
        self.field1.addItems(self.topics[unicode(self.topic_name.currentText())])
        self.field2.addItems(self.topics[unicode(self.topic_name.currentText())])
