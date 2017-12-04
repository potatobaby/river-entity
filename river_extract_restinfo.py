# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 17:32:00 2017

@author: gongqi
"""


import os

from shapely.geometry import LineString
from shapely.geometry import Point
import geohash_hilbert as ghh
import math
from math import log
import xlrd

#import river_extract_coords

os.chdir('H:\spatial entity\River_Entity')

def str_uni(a):
    str = a
    uni = str.decode('gbk')
    return uni

def uni_str(a):
    uni = a
    str = uni.encode('utf-8')
    return str

def river_extract_member(river_name):
    """Traverse the excel and return members of the given river """
    filename='dongtinghu.xlsx'
    data = xlrd.open_workbook(filename)
    table = data.sheet_by_name(u'Sheet1')
    flag = 0 #to see if the river exists
    # Find the row of specific river and its members 
    for row_num in range(table.nrows):
        row_value = table.row_values(row_num)
        if row_value[0] == river_name:
            while '' in row_value:
                row_value.remove('')
            del row_value[0]
            members = []
            for river in row_value:
                river = uni_str(river)
                members += [river] 
            return members
            flag = 1
    if flag == 0:
         return "null"
     
def adapt_ghash(coords):

    if len(coords) == 0:
        center_p = []
        bbox = []
        ghcode = "null"
    else:
        line = LineString(coords)
        cpoint = line.centroid
        bbox = line.bounds
        edgeLen = max(bbox[2] - bbox[0], bbox[3] - bbox[1])
        level = int(math.ceil(log(360 / edgeLen)/log(2)*2/5))
        ghcode = ghh.encode(cpoint.x, cpoint.y, level)
        center_p=[cpoint.x,cpoint.y]
    return center_p,bbox,ghcode


    
 