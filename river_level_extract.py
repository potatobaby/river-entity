#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 23:13:19 2017

@author: gongqi
"""

from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import json

def get_url_collections(page_website,flag):
    html = urlopen(page_website)
    siteSoup = BeautifulSoup(html, "html.parser")
    
    selectkey = siteSoup.find_all("li",attrs={"class":"hui3"})
    basic_url ='http://www.cjmsa.gov.cn'
    url_collections = []
    
    for blink in selectkey:  
        new_url = blink.find_all("a")[0]['href']
        url = basic_url + new_url
        if flag == 1:
            url_collections += [url]
            flag = 0
        else:
            flag = 1
    return url_collections

def get_data(url_collections,river_levels,time_strings):
    for i in range(len(url_collections)):
        website = url_collections[i]    
        html = urlopen(website)
        siteSoup = BeautifulSoup(html, "html.parser")
        
        selectkey1 = siteSoup.find_all("div",attrs={"class":"nr1"}) 
        selectkey2 = siteSoup.find_all("div",attrs={"class":"ly1"})        
         #time
        for blink in selectkey2:
            time_string = re.sub('文章来源：信息台　更新时间：','',blink.find(text=True)).strip()
            time_strings += [time_string]
            print(time_string)            
        #湘江+湘江水位 
        for blink in selectkey1:  
            xiangjiang = (blink.find_all("tbody")[0].find_all("p")[51].find(text=True)).strip()
            print(xiangjiang)
            river_level = (blink.find_all("tbody")[0].find_all("p")[52].find(text=True)).strip()
            river_levels += [river_level]
            print(river_level)
    return river_levels,time_strings

if __name__ == '__main__':     
    flag = 1  
    root_website = "http://www.cjmsa.gov.cn/vcms/classArticleListByPage.do?type=active&channelId=5&classIds=312&templateId=206&page=" 
    river_levels = []
    time_strings = []
    
    for i in range(1,2):                      #需要更改的地方
        page_website = root_website + str(i)
        url_collections = get_url_collections(page_website,flag)
        river_levels,time_strings = get_data(url_collections,river_levels,time_strings)
    #    flag = abs(flag-1)
    #将river_levels和time_strings写入json文件中
    newEntity = [time_strings]+[river_levels]
    with open('river_level.json', 'w') as output:
        json.dump(
            newEntity,
            output,
            ensure_ascii=False,
            indent=4,
            separators=(',', ':'))
    