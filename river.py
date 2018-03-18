#encoding=-utf-8
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 16:54:07 2018

@author: gongqi
"""
import os
import sys
import sys
sys.getdefaultencoding() 

import shapely.geometry

from osgeo import ogr  
from osgeo import osr  
from osgeo import gdal

import geohash_hilbert as ghh
import math
import geojson
import json
from rtree import index

import time
import codecs

#import river_extract_info

    
def river_object(river_file,shpFile):
    """把shp转为原始json文件,得到river段"""
    os.system('ogr2ogr -f GeoJSON -t_srs crs:84'+' '+river_file+' '+shpFile)
    print('Step1: river_json file created')


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
                            UUID='null',
                            GBCODE=gjson['properties']['GBCODE'],
                            LENGTH=gjson['properties']['LENGTH'],
                            LEVEL=gjson['properties']['LEVEL'],
                            HYDNTG_ID=gjson['properties']['HYDNTG_ID'],
                            CLASS=gjson['properties']['CLASS'],
                            R_CODE=gjson['properties']['R_CODE'],
                            BASIN1=gjson['properties']['BASIN1'],
                            BASIN2=gjson['properties']['BASIN2'],
                            BRANCH=gjson['properties']['BRANCH'],
                            BRANCH2=gjson['properties']['BRANCH2'],
                            transact_time=time.strftime("%d/%m/%Y"),
                            valid_time=time.strftime("%d/%m/%Y"),
                            Tributary_NAME=[],
                            Tributary=[])
                
                relation = dict(Tributary=[])
                
                                
                meta = dict(note='null',
                            precision='null',
                            produce_time='null',
                            producer='null',
                            security_level='null')
                
                rDict[name] = dict(type="Feature",
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
     
#    print('{0:d} original river entities.'.format(i))          
#    print('{0:d} river entities.'.format(len(rDict))) 
    print('Step2: union finished')
    eList = list(rDict.values())    
    return eList

def river_union2(river_file,shpFile):
    """将原始json文件按名称合并，得到river1_3级实体"""
    #输入生成原始json文件名称
    river_object(river_file,shpFile)
    
    with codecs.open(river_file, "r",encoding='utf-8', errors='ignore') as jsonObject:
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
                            UUID='null',
                            GBCODE=gjson['properties']['GBCODE'],
                            LENGTH=gjson['properties']['LENGTH'],
                            LEVEL=gjson['properties']['LEVEL_RIVE'],
                            transact_time=time.strftime("%d/%m/%Y"),
                            valid_time=time.strftime("%d/%m/%Y"),
                            Tributary_NAME=[],
                            Tributary=[])
                
                relation = dict(Tributary=[])
                
                                
                meta = dict(note='null',
                            precision='null',
                            produce_time='null',
                            producer='null',
                            security_level='null')
                
                rDict[name] = dict(type="Feature",
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
     
#    print('{0:d} original river entities.'.format(i))          
#    print('{0:d} river entities.'.format(len(rDict)))   
    print('Step2: union finished')
    eList = list(rDict.values())    
    return eList

def encode(eList):
    """计算出将每条河流的唯一标示UUID"""
    classCode = 160201
    for i in range(len(eList)):
         geom = shapely.geometry.asShape(eList[i]['geometry'])
         cpoint = geom.centroid
         bbox = geom.bounds  
         edgeLen = max(bbox[2] - bbox[0], bbox[3] - bbox[1])
         level = int(math.ceil(math.log2(360 / edgeLen) * 2 / 5))
         if level <= 0:
             level = 1
         #计算geohashcode
         ghcode = ghh.encode(cpoint.x, cpoint.y, level)
         #唯一标识 UUID=类别码+位置码+顺序码
         UUID = str(classCode) + ghcode + "00" 
         eList[i]['properties']['UUID']=UUID
    print('Step3: encoding finished')
    return eList
    
def item_build(eList):
    i = 0
    for entity in eList:
        sid = i
        geom = shapely.geometry.asShape(entity['geometry'])
        bbox = geom.bounds
        i = i+1
        yield (sid, bbox, entity)    


def extract_tributary(eList1,eList2):  
    """将上一级每条河流和下一级每条河流求交，求出支流信息"""
    #建立索引
    idxP = index.Property()
    idxP.filename = 'road_index'
    idxP.overwrite = True
    idxP.storage = index.RT_Disk
    idxP.dimension = 2
    idx = index.Index(idxP.filename,
                      item_build(eList2),
                      properties=idxP,
                      interleaved=True,
                      overwrite=True)

#    linkNum = 0
    for currentEntity in eList1:
        currentGeom = shapely.geometry.asShape(currentEntity['geometry'])
        currentQueryBox = currentGeom.bounds   #对上一级河流求bbox
        currentID = currentEntity['properties']['UUID']
        currentLevel = currentEntity['properties']['LEVEL']
        currentBuffer = currentGeom.buffer(0.2)
        judgeIds = list(idx.intersection(currentQueryBox))#求出相交的下一级河流
        for jid in judgeIds:
            judgeEntity = eList2[jid]
            judgeGeom = shapely.geometry.asShape(judgeEntity['geometry'])
            if currentBuffer.intersects(judgeGeom):
                jID = judgeEntity['properties']['UUID']
                jLevel= judgeEntity['properties']['LEVEL']
                jNAME = judgeEntity['properties']['NAME']
                if jID != currentID and jID not in currentEntity['relation']['Tributary'] and jLevel>currentLevel:
                    currentEntity['relation']['Tributary'].append(jID)
                    currentEntity['properties']['Tributary'].append(jID)
                    currentEntity['properties']['Tributary_NAME'].append(jNAME)                   
#                    linkNum += 1
  
    
    print('Step4: extracting relations finished')
    return eList1
                


if __name__ == '__main__':
    start = time.time()
    
    #选择文件路径
    os.chdir('/Users/gongqi/Documents/Research/river_exp/data')
    print(os.getcwd())
    
    #选择文件5级河流
    print('')
    file_title = 'River5_polyline'
    shpFile = file_title+'.shp'
    print(shpFile)
    river_file = file_title+'_object.json' 
    eList5 = river_union(river_file,shpFile)
    eList5 = encode(eList5)
               
   #选择4级河流
    print('')
    file_title = 'River4_polyline'
    shpFile = file_title+'.shp'
    print(shpFile)
    river_file = file_title+'_object.json' 
    eList4 = river_union(river_file,shpFile)
    eList4 = encode(eList4)
    eList4 = extract_tributary(eList4,eList5)      
            
    #选择3级河流
    print('')
    file_title = 'River1_3_polyline'
    shpFile = file_title+'.shp'
    print(shpFile)
    river_file = file_title+'_object.json' 
    eList1=river_union2(river_file,shpFile)
    eList1 = encode(eList1)
    eList1 = extract_tributary(eList1,eList1)
    eList1 = extract_tributary(eList1,eList4) 
    eList1 = extract_tributary(eList1,eList5) 
    
    
    
    file_titles = ['River1_3_polyline','River4_polyline','River5_polyline']
    eLists = [eList1,eList4,eList5]  
    for i in range(len(eLists)):
        entityFile='../output/'+file_titles[i]+'_entity.geojson'
        Entity = {
        "type": "FeatureCollection",
        "crs": {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "features": eLists[i]}
        with open(entityFile, 'w') as output:
            geojson.dump(
                    Entity,
                    output,
                    ensure_ascii=False,
                    indent=4,
                    separators=(',', ':'))
    
    print('All river entity files created')
            
    end = time.time()
    print(end-start, 'ms')
    

    
    

    




