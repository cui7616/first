# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 16:44:37 2018

@author: ceedi
"""

import http
import json
import pandas as pd
import time

class download:    
    def url_download(day):
        headers = {"Content-type": "application/json; charset=utf-8"}
        httpClient = http.client.HTTPConnection("192.168.12.73", 8080)
        database = pd.DataFrame(columns=['addTime','userName', 'localX', 'localY', 'zoneId'])
        startNum = 0
        scaleNum = 1000
        isNextPage = 'true'
        while isNextPage == 'true':            
            print(startNum)
            data = {"action":"get.position.logs",
                "startNum":str(startNum),
                "scaleNum":str(scaleNum),
                "day":day}
            params = '?'
            for key in data:
                params = params +key+'='+data[key]+'&'
            params="/service/position.json/"+params
            httpClient.request("GET",params, None, headers)
            response = httpClient.getresponse()
            position_json = response.read()
            position_obj = json.loads(position_json)
            
            temp = pd.DataFrame(position_obj['positions'])
            temp_ = temp[['addTime','userName', 'localX', 'localY', 'zoneId']]
            database = database.append(temp_,ignore_index=True)
            
            isNextPage = position_obj['paging']['isNextPage']
            startNum = startNum + scaleNum    
        return database
        
    def time_tran(times):
        times /=1000.0
        timearr = time.localtime(times)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timearr)
        return otherStyleTime 

class data:
    
    def __init__(self,day):
        self.database = download.url_download(day)
        addTime_com = self.database['addTime']
        timeStamp = addTime_com
        time_transfer = pd.Series(map(download.time_tran,timeStamp))
        self.database['Time']=time_transfer
    

if __name__ == '__main__': 
    database = data('2018-10-26')



