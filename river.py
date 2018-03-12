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

import shapely.geometry

#from osgeo import ogr  
#from osgeo import osr  
#from osgeo import gdal

import geojson
import json
from rtree import index

import time
import codecs

#import river_extract_info

    
def river_object(river_file,shpFile):
    """把shp转为原始json文件,得到river段"""
    os.system('ogr2ogr -f GeoJSON -t_srs crs:84'+' '+river_file+' '+shpFile)
    print('river_json file created')


def river_union(river_file,shpFile):
    """将原始json文件按名称合并，得到river实体"""
    #输入生成原始json文件名称
    river_object(river_file,shpFile)
    
    with codecs.open(river_file, "r",encoding='gbk', errors='ignore') as jsonObject:
        gjsonList = json.load(jsonObject)
        
    nameList = []
    rDict = {}
    i=0
    for gjson in gjsonList['features']:
        i=i+1
        name = gjson['properties']['NAME']
        #对每个河流段判断是新的
        if name is not None:
            shape = shapely.geometry.asShape(gjson['geometry'])
            if name not in nameList:
                nameList.append(name)
                
                #geometry,properties,relation, meta四大类
                geometry = shape
                
                properties = dict(NAME=name,
                            GBCODE=gjson['properties']['GBCODE'],
                            LENGTH=gjson['properties']['LENGTH'],
#                            LEVEL=gjson['properties']['LEVEL'],
#                            HYDNTG_ID=gjson['properties']['HYDNTG_ID'],
#                            CLASS=gjson['properties']['CLASS'],
#                            R_CODE=gjson['properties']['R_CODE'],
#                            BASIN1=gjson['properties']['BASIN1'],
#                            BASIN2=gjson['properties']['BASIN2'],
#                            BRANCH=gjson['properties']['BRANCH'],
#                            BRANCH2=gjson['properties']['BRANCH2'],
                            transact_time=time.strftime("%d/%m/%Y"),
                            valid_time=time.strftime("%d/%m/%Y"))
                
                relation = dict(Member='null')
                
                                
                meta = dict(note='null',
                            precision='null',
                            produce_time='null',
                            producer='null',
                            security_level='null')
                
                rDict[name] = dict(sid=gjson['properties']['GBCODE'],
                                   geometry=geometry,
                                   properties=properties,
                                   relation=relation,
                                   meta=meta)

            else:
                #河流段的长度加起来
                rDict[name]['properties']['LENGTH']+=gjson['properties']['LENGTH']
                #河流段的坐标合并
                origin = rDict[name]['geometry']
                rDict[name]['geometry'] = origin.union(shape)
     
    print('{0:d} original river entities.'.format(i))          
    print('{0:d} river entities.'.format(len(rDict)))     
    return rDict

def item_build(eDict):
    for (name, entity) in eDict.items():
        sid = entity['sid']
        geom = shapely.geometry.asShape(entity['geometry'])
        bbox = geom.bounds
        yield (sid, bbox, (name, entity))

def intersect_judge(eDict):

    sidDict = {}
    for (name, entity) in eDict.items():
        feature = geojson.Feature(geometry=entity['geometry'])
        eDict[name]['geometry'] = feature['geometry']
        sid = entity['sid']
        sidDict[sid] = eDict[name]

    idxP = index.Property()
    idxP.filename = 'river_index'
    idxP.overwrite = True
    idxP.storage = index.RT_Disk
    idxP.dimension = 2
    idx = index.Index(idxP.filename,
                      item_build(eDict),
                      properties=idxP,
                      interleaved=True,
                      overwrite=True)

    linkNum = 0
    for (currentName, currentEntity) in eDict.items():
        # if linkNum % 8192 == 0:
        #     print(linkNum)
        currentGeom = shapely.geometry.asShape(currentEntity['geometry'])
        currentQueryBox = currentGeom.bounds
        judgeIds = list(idx.intersection(currentQueryBox))
        for jid in judgeIds:
            judgeEntity = sidDict[jid]
            judgeGeom = shapely.geometry.asShape(judgeEntity['geometry'])
            if currentGeom.intersects(judgeGeom):
                jName = judgeEntity['properties']['NAME']
                if jName != currentName and jName not in eDict[currentName]['intersects']:
                    eDict[currentName]['intersects'].append(jName)
                    eDict[jName]['intersects'].append(currentName)
                    linkNum += 1

    print('{0:d} road intersection links'.format(linkNum))
    return list(eDict.values())


if __name__ == '__main__':
    start = time.time()
    
    #选择文件路径
    os.chdir('/Users/gongqi/Documents/Research/river_exp/data')
    print(os.getcwd())
    
    #选择文件
    for file_title in ['River5_polyline','River4_polyline','River1_3_polyline']:
        shpFile = file_title+'.shp'
        print(shpFile)
        river_file = file_title+'_object.json' 
        eDict=river_union(river_file,shpFile)
#        eList = intersect_judge(eDict)
#        eList = list(eDict.values())
        entityFile=file_title+'_entity.geojson'
        Entity = {
        "type": "FeatureCollection",
        "crs": {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "features": eDict}
        with open(entityFile, 'w') as output:
            geojson.dump(
                    Entity,
                    output,
                    ensure_ascii=False,
                    indent=4,
                    separators=(',', ':'))
        
    end = time.time()
    print(end-start, 'ms')
    

    
    

    




