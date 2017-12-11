# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 10:41:16 2017

@author: gongqi
"""
import os
import sys  

import numpy as np
from osgeo import ogr  
from osgeo import osr  
from osgeo import gdal
from scipy.spatial.distance import cdist
       
def generate_shp(filename,river_name):
    """
    Generate shapefiles of every single river section for a given river_name.
    """
    # Read shaplefiles
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataSource = driver.Open(filename,1)
    if dataSource is None:
        print 'could not open'
        sys.exit(1)
    print 'done!'
    layer = dataSource.GetLayer(0)
    layer.SetAttributeFilter("name = " + "'" + river_name + "'")
    # Save shapefiles
    i = 0
    for feature in layer:
        river_geom = ogr.Geometry(ogr.wkbLineString)       
        geom = feature.GetGeometryRef()  
        river_geom.AddGeometry(geom)   
        src_filename = 'H:\spatial entity\EXP_waterway\\lishui_EXP\\' \
                        + feature.GetField("osm_id") + '_' + str(i) + '.shp'
        ds = driver.CreateDataSource(src_filename)    
        if os.path.exists(src_filename):
            driver.DeleteDataSource(src_filename)          
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(4326)
        src_layer = ds.CreateLayer(feature.GetField("osm_id") + '_' + str(i),
                                  srs,geom_type = ogr.wkbLineString)   
        fieldDefn = ogr.FieldDefn('number', ogr.OFTString)
        fieldDefn.SetWidth(24)
        src_layer.CreateField(fieldDefn)    
        featureDefn = src_layer.GetLayerDefn()
        src_feature = ogr.Feature(featureDefn)
        src_feature.SetGeometry(geom)
        src_feature.SetField('number', i)
        src_layer.CreateFeature(src_feature)
        i = i + 1 
    src_feature = None
    
def get_river_coords(filename,river_name) :
    """
    Get the start and end points of every river sections,combine them as 
    a whole named coords and return it.
    """
 # Read shaplefiles
    driver = ogr.GetDriverByName('ESRI Shapefile')
    dataSource = driver.Open(filename,1)
    if dataSource is None:
        print 'could not open'
        sys.exit(1)
    else:
        print 'done!'
    layer = dataSource.GetLayer(0)
    layer.SetAttributeFilter("name = " + "'" + river_name + "'")
    # Get coordinates of start point & end point for every river section. 
    start_pts=[]
    end_pts=[]
    count = layer.GetFeatureCount()
    i = 0
    river_coords = []
    for feature in layer:
        geom = feature.GetGeometryRef() 
        start_pts += [[geom.GetPoint(0)[0],geom.GetPoint(0)[1],i]]
        j=geom.GetPointCount()-1
        end_pts += [[geom.GetPoint(j)[0],geom.GetPoint(j)[1],i+count]]
        i = i + 1
        river_sec_coords = []
        for k in range(0, geom.GetPointCount()):
            # GetPoint returns a tuple not a Geometry
            pt = geom.GetPoint(k)
            river_sec_coords += [[pt[0], pt[1]]]
        river_coords += [river_sec_coords]
    # Comebine the start points & end points together. 
    coords=np.array(start_pts + end_pts) 
    return river_coords,coords

def get_river_src(coords):
    """
    Calculate the elevation of every points in coords and return the index of 
    the highest point.
    """
    # Get elevation information from .tif file
    gdal.UseExceptions()
    try:
        src_ds = gdal.Open( 'H:\spatial entity\data\shpdata\\chinasrtm24000_16000.tif' )
    except RuntimeError, e:
        print 'Unable to open INPUT.tif'
        print e
        sys.exit(1)    
    try:
        srcband = src_ds.GetRasterBand(1)
    except RuntimeError, e:
        print 'Band ( %i ) not found' # band_num
        print e
        sys.exit(1)    
    elevation = srcband.ReadAsArray()
    # Transform coordinates to pixel 
    gt = src_ds.GetGeoTransform() 
    coords_elevation = [] 
    for i in range(0,len(coords)):
        px = int((coords[i][0] - gt[0]) / gt[1]) # y pixel
        py = int((coords[i][1] - gt[3]) / gt[5]) # x pixel
        coords_elevation += [elevation[py][px]]
    # Get the index of maximum elevation
    return coords_elevation.index(max(coords_elevation))
    

    
def sort_river(filename,river_name):
    """
    Sort the river sections and return the order of them as a list.
    
    Keyword arguments:
    coords -- the coordinates of start and end points of every river section
    sec_num -- the number of river sections
    restp_coords -- the coordinates of the rest points after deleting sorted 
                    points.  
    closestp_index -- the index of the closest point
    nextp_coord -- the coordinate of the next start point(other end of the 
                                                          river section)
    sorted_index -- the sorted index of river sections          
    """    
    river_coords,coords =  get_river_coords(filename,river_name) 
    if len(river_coords) == 0:
        sorted_river_coords = []
        return sorted_river_coords
    else:
        sec_num = len(coords) / 2
        closestp_index = get_river_src(coords)
        restp_coords = coords
        closest2rest_index = closestp_index 
        sorted_index = []
        for i in range(sec_num):
            if closestp_index < sec_num:
                # get the other end of the river section
                nextp_coord = np.array([[coords[closestp_index + sec_num][0],
                                         coords[closestp_index + sec_num][1]]])
                # delete the start and end points of the river section from 
                # restp_coords
                restp_coords = np.delete(restp_coords,[closest2rest_index,
                                                       closest2rest_index + 
                                                       len(restp_coords) / 2],0)
                sorted_index += [closestp_index]
            else:
                nextp_coord = np.array([[coords[closestp_index - sec_num][0],
                                         coords[closestp_index - sec_num][1]]])
                restp_coords = np.delete(restp_coords,[closest2rest_index,
                                                       closest2rest_index - 
                                                       len(restp_coords) / 2],0)
                sorted_index += [closestp_index - sec_num]
                list.reverse(river_coords[sorted_index[-1]])
            # No need to find the next point once the last section is found.
            if i == sec_num - 1:
                break                                   
            # Find the closest point
            else:
                restp_coords_cal = np.delete(restp_coords,2,1)
                dist = cdist(nextp_coord,restp_coords_cal)  
                sorted_dist = np.argsort(dist, axis=1)  
                closest2rest_index = sorted_dist[:,0][0]
                closestp_index = int(restp_coords[closest2rest_index][2])
        sorted_river_coords = []
        for i in range(len(sorted_index)):
            sorted_river_coords += river_coords[sorted_index[i]]
        return sorted_river_coords
        
    

if __name__=='__main__':
    #generate_shp('H:\spatial entity\EXP_waterway\waterways.shp','澧水')
    sorted_river_coordinates = sort_river('H:\spatial entity\EXP_waterway\waterways.shp',
                              '澧水')  