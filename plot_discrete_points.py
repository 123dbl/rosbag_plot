#! /usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
import csv
import re
import gflags
import sys

gflags.DEFINE_string('title', 'plot', 'name of figure')
gflags.DEFINE_string('x_label', 'x(m)', 'name of x axis')
gflags.DEFINE_string('y_label', 'y(m)', 'name of y axis')
gflags.DEFINE_string('label1', 'data1', 'name of plot1')
gflags.DEFINE_string('label2', 'data2', 'name of plot2')
gflags.DEFINE_string('file_name1', 'can1.csv', 'name of data file 1')
gflags.DEFINE_integer('column_x1', 15, 'column of x data in file 1')
gflags.DEFINE_integer('column_y1', 18, 'column of y data in file 1')
gflags.DEFINE_string('separator1', ',', 'separator used to split_data1, support multi-separators')
gflags.DEFINE_string('file_name2', 'gps_1.csv', 'name of data file 2')
gflags.DEFINE_integer('column_x2', 6, 'column of x data in file 2')
gflags.DEFINE_integer('column_y2', 5, 'column of y data in file 2')
gflags.DEFINE_string('file_name', 'result', 'name of data pic')
gflags.DEFINE_string('separator2', ',', 'separator used to split_data2, support multi-separators')
gflags.DEFINE_string('log_name', '', 'name of log file')

def split_data(line_txt, option, p):

    data = []
    if option == 0:
        data = re.split(p, line_txt)
    elif option == 1:
        data = re.split(p, line_txt)
    return data


def load_txt_data(file_name, c1, c2, p):

    data1 = []
    data2 = []
    with open(file_name) as txtData:
        lines = txtData.readlines()
        for line in lines:
            data = split_data(line, 0, p)
            data1.append(data[c1])
            data2.append(data[c2])
    return data1, data2


def load_csv_data(file_name, c1, c2):

    data1 = []
    data2 = []
    with open(file_name) as csvData:
        lines = csv.reader(csvData)
        for line in lines:
            data1.append(line[c1])
            data2.append(line[c2])
    return data1, data2

if __name__ == '__main__':
    gflags.FLAGS(sys.argv)
    file_name1 = gflags.FLAGS.file_name1
    column_x1 = gflags.FLAGS.column_x1
    column_y1 = gflags.FLAGS.column_y1
    p1=gflags.FLAGS.separator1
    if file_name1[-3:] == 'csv':
        x1, y1 = load_csv_data(file_name1, column_x1, column_y1)
    elif file_name1[-3:] == 'txt':
        x1, y1 = load_txt_data(file_name1, column_x1, column_y1, p1)
    file_name2 = gflags.FLAGS.file_name2
    column_x2 = gflags.FLAGS.column_x2
    column_y2 = gflags.FLAGS.column_y2
    p2=gflags.FLAGS.separator2
    if file_name1[-3:] == 'csv':
        x2, y2 = load_csv_data(file_name2, column_x2, column_y2)
    elif file_name1[-3:] == 'txt':
        x2, y2 = load_txt_data(file_name2, column_x2, column_y2, p2)
    plt.figure(figsize=(16, 12))
    #plt.plot(list(range(0,len(y1)-1,1)), y1[1:], "r-*", label='data1')
    plt.plot(x1[1:], y1[1:], "r-*", label=gflags.FLAGS.label1)
    #plt.plot(list(range(0,len(y1)-1,1)), y2[1:], "b-+", label='data2')
    plt.plot(x2[1:], y2[1:], "b-+", label=gflags.FLAGS.label2)
    plt.xlabel(gflags.FLAGS.x_label)
    plt.ylabel(gflags.FLAGS.y_label)
    plt.title(gflags.FLAGS.title)
    #plt.ylim(-1.2, 1.2)
    plt.legend(loc='upper right')
    plt.grid(True)
    #plt.savefig(gflags.FLAGS.title + '.svg', format= 'svg')
    plt.show()
