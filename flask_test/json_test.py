# -*- coding: utf-8 -*-
"""
Created on Sun Oct 28 12:43:02 2018

@author: czmy
"""
import json
import time
jsonData = [{
                    'x': time.mktime((2014, 10, 2,0,0,0,2,317,0))*1000,
                    'x2': time.mktime((2014, 11, 2,0,0,0,2,317,0))*1000,
                    'y': 0
                }, {
                    'x': time.mktime((2014, 11, 2,0,0,0,2,317,0))*1000,
                    'x2': time.mktime((2014, 11, 5,0,0,0,2,317,0))*1000,
                    'y': 1
                }, {
                    'x': time.mktime((2014, 11, 8,0,0,0,2,317,0))*1000,
                    'x2': time.mktime((2014, 11, 9,0,0,0,2,317,0))*1000,
                    'y': 2
                }, {
                    'x': time.mktime((2014, 11, 9,0,0,0,2,317,0))*1000,
                    'x2': time.mktime((2014, 11, 19,0,0,0,2,317,0))*1000,
                    'y': 1
                }, {
                    'x': time.mktime((2014, 11, 10,0,0,0,2,317,0))*1000,
                    'x2': time.mktime((2014, 11, 23,0,0,0,2,317,0))*1000,
                    'y': 2
                }]
print(jsonData)
# json.dumps()用于将dict类型的数据转成str，因为如果直接将dict类型的数据写入json会发生报错，因此将数据写入时需要用到该函数。
j = json.dumps(jsonData)
print(j)