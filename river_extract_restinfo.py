# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 17:32:00 2017

@author: gongqi
"""


import os

from shapely.geometry import LineString
from geopy import distance
import geohash_hilbert as ghh
import math
from math import log
#from math import radians, cos, sin, asin, sqrt
import xlrd

#import river_extract_coords

def str_uni(a):
    str = a
    uni = str.decode('utf-8')
    return uni

def uni_str(a):
    uni = a
    str = uni.encode('utf-8')
    return str

def river_extract_member(river_name):
    """Traverse the excel and return members's name of the given river """
    filename = 'dongtinghu.xlsx'
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


# Calculates distance between 2 GPS coordinates
#def haversine(lat1, lon1, lat2, lon2):
#    """
#    Calculate the great circle distance between two points 
#    on the earth (specified in decimal degrees)
#    """
#    # convert decimal degrees to radians 
#    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
#    # haversine formula 
#    dlon = lon2 - lon1 
#    dlat = lat2 - lat1 
#    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
#    c = 2 * asin(sqrt(a)) 
#    r = 6378.137 # Radius of earth in kilometers. Use 3956 for miles
#    return c * r

def dist(point1,point2):
    distance.VincentyDistance.ELLIPSOID = 'WGS-84'
    d = distance.distance
    dist2points = d(point1, point2)
    return dist2points.meters
    

def length(coords):
    """Calculate the length of the river"""
    if len(coords) == 0:
        river_len2 = 0
    else:
        lines = LineString(coords)
        river_len2 = 0
        for i in range(len(coords)-1):
            point1 = lines.coords[i]
            point2 = lines.coords[i + 1]
            river_len2 += dist(point1,point2) 
        river_len2 = round(river_len2/1000,2)
    return river_len2
   
def extract_riverCode():
    """
    Traverse the excel and return the members' riverCode of the given river 
    """
    riverCode_dict = {}
    filename='river_grades.xls'
    data = xlrd.open_workbook(filename)
    sheets = data.sheet_names()
    for i in range(len(sheets)): 
        table = data.sheet_by_name(sheets[i])
        for row_num in range(table.nrows):
            row_value = table.row_values(row_num)
            a = row_value[0]
            riverCode_dict[a] = row_value[1]
    return riverCode_dict

def extract_member_riverCode(river_name,riverCode_dict):
    """Return all riverCode of the river's members"""
    members = river_extract_member(river_name)
    if members == "null":
        return "null"
    else:
        members_riverCode = []
        for i in range(len(members)):
            river_name = str_uni(members[i])
            member_code =  riverCode_dict[river_name]
            members_riverCode += [member_code]
        return members_riverCode
        
riverCode_dict = extract_riverCode() 
b = river_extract_member(u'麻林河')      
a = extract_member_riverCode(u'麻林河',riverCode_dict)   

            
        
            
    
 