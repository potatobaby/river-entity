# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 09:18:33 2017

@author: gongqi
"""

# -*- coding: utf-8 -*-
import json
import xlrd
import pinyin
import time

import river_extract_restinfo
import river_extract_coords


def str_uni(a):
    str = a
    uni = str.decode('utf-8')
    return uni

def uni_str(a):
    if a == None:
        str = "null"
    else:
        uni = a
        str = uni.encode('utf-8')
    return str
    

def generate_river_entitylist(table):     
    """Get river entity list"""
    nrows = table.nrows
    riverlist = []
    for i in range(nrows):
        row = table.row_values(i)
        while '' in row:
            row.remove('')
        UUID = str_uni('null')
        valid_time = "21/11/2017"
        transact_time = time.strftime("%d/%m/%Y")
        tag = []
        member = river_extract_restinfo.river_extract_member(row[0])
        riverCode_dict = river_extract_restinfo.extract_riverCode()
        member_riverCode = river_extract_restinfo.extract_member_riverCode(row[0],
                                                                           riverCode_dict)
        belongs_to = uni_str(row[2])
        function = []
        rule = []
        coords=river_extract_coords.sort_river(
                              'H:\spatial entity\EXP_waterway\waterways.shp',
                              uni_str(row[0])) 
        cpoint,bbox,ghcode = river_extract_restinfo.adapt_ghash(coords)
        river_len = river_extract_restinfo.length(coords)
        meta = dict(note=str_uni('null'),
                    precision=str_uni('null'),
                    produce_time=str_uni('null'),
                    producer=str_uni('null'),
                    security_level=str_uni('null'))
        properties = dict(name=uni_str(row[0]),
                          type="river",
                          pinyin=pinyin.get(row[0], format='strip'),
                          length=repr(river_len)+"km",
                          riverCode=row[1],
                          ghashCode=ghcode)
        relation = dict(flooded_area = str_uni('null'))
        geometry = dict(Type="MultiLine",
                      coordinates=coords,
                      bbox=bbox,
                      center_point=cpoint,
                      version_time="21/11/2017",
                      SRID="EPSG 4326")
        # generate a single_river_entity
        single_river_entity = dict(UUID=UUID,
                                 valid_time=valid_time,
                                 transact_time=transact_time,
                                 tag=tag,
                                 member=member,
                                 member_riverCode=member_riverCode,
                                 belongs_to=belongs_to,
                                 function=function,
                                 rule=rule,
                                 meta=meta,
                                 propertities=properties,
                                 relation=relation,
                                 geometry=geometry)   
        riverlist.append(single_river_entity)
    print("river entity transform done.")
    return riverlist

        
if __name__ == '__main__':
    # exlFile = sys.argv[1]
    exlFile = "H:\spatial entity\River_Entity\\river_grades.xls"
    first_river_Filename = "first_river_entity.geojson"
    second_river_Filename = "second_river_entity.geojson"
    third_river_Filename = "third_river_entity.geojson"
    fourth_river_Filename = "fourth_river_entity.geojson"
    fifth_river_Filename = "fifth_river_entity.geojson"

    data = xlrd.open_workbook(exlFile)
#    first_river = data.sheet_by_name('first_grade')
#    second_river = data.sheet_by_name('second_grade')
#    third_river = data.sheet_by_name('third_grade')
#    fourth_river = data.sheet_by_name('fourth_grade')
    fifth_river = data.sheet_by_name('fifth_grade')
    
    
#    first_river_entitylist = generate_river_entitylist(first_river)
#    second_river_entitylist = generate_river_entitylist(second_river)
#    third_river_entitylist = generate_river_entitylist(third_river)
#    fourth_river_entitylist = generate_river_entitylist(fourth_river)
    fifth_river_entitylist = generate_river_entitylist(fifth_river)
  
#    with open(first_river_Filename, 'w') as file_object:
#        json.dump(first_river_entitylist, file_object, 
#                    ensure_ascii=False, indent=4, separators=(',', ':'))
#    with open(second_river_Filename, 'w') as file_object:
#        json.dump(second_river_entitylist, file_object, 
#                    ensure_ascii=False, indent=4, separators=(',', ':'))
#    with open(third_river_Filename, 'w') as file_object:
#        json.dump(third_river_entitylist, file_object, 
#                     ensure_ascii=False, indent=4, separators=(',', ':'))
#    with open(fourth_river_Filename, 'w') as file_object:
#        json.dump(fourth_river_entitylist, file_object, 
#                     ensure_ascii=False, indent=4, separators=(',', ':'))
    with open(fifth_river_Filename, 'w') as file_object:
        json.dump(fifth_river_entitylist, file_object, 
                     ensure_ascii=False, indent=4, separators=(',', ':'))
