# -*-coding: utf-8 -*-
"""
Filename:  wrapper.py
Descript:
Modified:  17-12-5 下午3:24
Version:  0.1
Created:  17-12-5 下午3:24
Compiler:  python3.5
Author:  guoning
Company:  DBRG@NUDT
Contact: guoning10@nudt.edu.cn
"""


import geojson


def add_head(eFile):

    with open(eFile) as eObject:
        eList = geojson.load(eObject)
              
    newEntity = {
        "type": "FeatureCollection",
        "crs": {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "features": eList}

    with open('new_' + eFile, 'w') as output:
        geojson.dump(
            newEntity,
            output,
            ensure_ascii=False,
            indent=4,
            separators=(',', ':'))
    return


if __name__ == '__main__':

    # exlFile = sys.argv[1]
    file_title = ["first","second","third","fourth","fifth"]
    for i in range(len(file_title)):
        filename = file_title[i]+"_river_entity.geojson"
        add_head(filename)

