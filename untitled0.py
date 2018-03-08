#encoding=-utf-8
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 16:54:07 2018

@author: gongqi
"""
import os
import sys

import numpy as np
from osgeo import ogr  
from osgeo import osr  
from osgeo import gdal

import geojson

import time
import codecs

    
def river_object(river_file,shpFile):
    """把shp转为原始json文件,得到river段"""
    os.system('ogr2ogr -f GeoJSON -t_srs crs:84'+' '+river_file+' '+shpFile)
    print('river_json file created')


def river_union(shpFile):
    """将原始json文件按名称合并，得到river实体"""
    #输入生成原始json文件名称
    river_file = 'river.json' 
    river_object(river_file,shpFile)
    
    with codecs.open(river_file, "r",encoding='utf-8', errors='ignore') as jsonObject:
        gjsonList = geojson.load(jsonObject)
        
    nameList = []
    rDict = {}
    for gjson in gjsonList['features']:
        name = gjson['properties']['NAME']
        #对每个河流段判断是否
        if name is not None:
            if name not in nameList:
                nameList.append(name)
                #properties和geometry两大类
                properties = dict(NAME=name,
                            LENGTH=gjson['properties']['LENGTH'],
                            HYDNTG_ID=gjson['properties']['HYDNTG_ID'],
                            GBCODE=gjson['properties']['GBCODE'],
                            CLASS=gjson['properties']['CLASS'],
                            R_CODE=gjson['properties']['R_CODE'],
                            BASIN1=gjson['properties']['BASIN1'],
                            BASIN2=gjson['properties']['BASIN2'],
                            BRANCH=gjson['properties']['BRANCH'],
                            BRANCH2=gjson['properties']['BRANCH2'],
                              LEVEL=gjson['properties']['LEVEL'])
                geometry=dict(coordinates=gjson['geometry']['coordinates'],
                              type=gjson['geometry']['type'])
                rDict[name] = dict(properties=properties,
                                   geometry=geometry)
            else:
                #河流段的长度加起来
                rDict[name]['properties']['LENGTH']+=gjson['properties']['LENGTH']
                #河流段的坐标合并
                rDict[name]['geometry']['coordinates'].append(
                        gjson['geometry']['coordinates'])
                #河流段的几何类型改变
                rDict[name]['geometry']['type']='MultiLineString'
                
    print('{0:d} river entities.'.format(len(rDict)))        
    return rDict



if __name__ == '__main__':
    start = time.time()
    
    #选择文件路径
    os.chdir('/Users/gongqi/Documents/Research/river_exp/data')
    print(os.getcwd())
    #选择文件
    shpFile = 'River5_polyline.shp'
    print(shpFile)
    rDict=river_union(shpFile)
    
    entityFile='five.json'
    with open(entityFile, 'w') as output:
        json.dump(
            rDict,
            output,
            ensure_ascii=False,
            indent=4,
            separators=(',', ':'))
        
    end = time.time()
    print(end-start, 'ms')
    







#driver = ogr.GetDriverByName('ESRI Shapefile')
#shpFile = r"./data/River5_polyline.shp"
#ds = driver.Open(shpFile) 
#   
#layer = ds.GetLayer()
#
##查看属性类型
##layerDefinition = layer.GetLayerDefn()
##for i in range(layerDefinition.GetFieldCount()):
##    print(layerDefinition.GetFieldDefn(i).GetName())
#
##得到所有河流名称    
#for feature in layer:
##    geom = feature.GetGeometryRef()
##    print (geom.Centroid().ExportToWkt())
##    a = feature.GetField("NAME").encode('latin-1').decode('unicode_escape')   
##    a = feature.GetField("NAME").encode('').decode('unicode_escape')
#    a = feature.GetField("NAME")
#    print(a)
##    if a.startswith( '\\u'):
##        a = a.encode('latin-1').decode('unicode_escape') 
##    else:
##        print('hello')   
##   str = feature.GetField("NAME")
##   str = codecs.decode(str,'unicode_escape')
##   print(str)
    




