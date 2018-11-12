# -*- coding: utf-8 -*-
"""
Created on Thu Oct 18 13:25:15 2018

@author: ceedi
"""

from PIL import Image
import matplotlib.pyplot as plt
import pandas as pd
import time
import numpy as np
import math
from scipy import interpolate
import scipy.signal as signal
from matplotlib.dates import DateFormatter, drange
import datetime
#from pyecharts import Line
import json


class process:
    
    def quzao(guiji):
        guiji_out = guiji[guiji['zoneId']>0]    
        return guiji_out
    
    def gonggong(guiji,quyu):
        guiji_out = guiji[guiji['zoneId']==quyu]
        return guiji_out
    
    def velocity(guiji):
        guiji_out = guiji    
        addtime = guiji_out['addTime']
        localX = guiji_out['localX']
        localY = guiji_out['localY']
        aa = addtime.shape
        addtime_diff = np.array(addtime[3:aa[0]])-np.array(addtime[0:aa[0]-3])
        locaX_diff = np.array(localX[3:aa[0]])-np.array(localX[0:aa[0]-3])
        locaY_diff = np.array(localY[3:aa[0]])-np.array(localY[0:aa[0]-3])
        local_diff = np.sqrt(np.square(locaX_diff)+np.square(locaY_diff))
    #    print(locaX_diff,locaY_diff)
        velocity = local_diff/addtime_diff/13.85*1000
        velocity = np.append(velocity,np.array([0,0,0]))
        guiji_out['velocity'] = velocity    
        return guiji_out
    
    #def med_fil(addtime,local):
    #    a1 = int(np.min(addtime)/1000.0)
    #    a2 = int(np.max(addtime)/1000.0)
    #    for index in range(a1,)
    
    def resample(guiji):
        #中值滤波+规则采样        
        addtime = np.floor(np.array(guiji['addTime'].astype('float'))/1000)
        addtime_unique = np.unique(addtime)
        guiji_out = np.zeros((addtime_unique.shape[0],4))
        
        localX = np.array(guiji['localX'].astype('float'))
        localY = np.array(guiji['localY'].astype('float'))
        zoneId = np.array(guiji['zoneId'].astype('int'))
        j = 0
        for index in addtime_unique:
            guiji_out[j,0] = index
            temp = np.where((addtime==index))
            guiji_out[j,1] = np.median(localX[temp])
            guiji_out[j,2] = np.median(localY[temp])
            guiji_out[j,3] = np.argmax(np.bincount(zoneId[temp]))
    #        guiji_out[j,3] = np.median(zoneId[temp])
    #        temp1 = localY[addtime == index]
            j = j+1
        
        time1 = time.mktime(time.strptime(local_date, "%Y-%m-%d"))    
        time2 = time1+86400
        times1 = np.linspace(time1,time2,int(time2-time1)+1)
    #    guiji_out2 = np.zeros((addtime_unique.shape[0],4))
        guiji_out2 = guiji_out
    #    print(type(guiji_out2[0]))
        guiji_out3 = np.append([guiji_out2[0]],guiji_out2,axis = 0)
        guiji_out4 = np.append(guiji_out3,[guiji_out2[-1]],axis = 0)
        guiji_out4[0,0]= time1
        guiji_out4[-1,0]= time2    
    #    guiji_out2.append(guiji_out[-1])
    #    times2 = np.linspace(min(addtime_unique),max(addtime_unique),int(max(addtime_unique)-min(addtime_unique))+1)
        f=interpolate.interp1d(list(guiji_out4[:,0].T),list(guiji_out4[:,1:].T),kind='nearest')
    #    print(guiji_out[:,0])
        ynew=f(list(times1.T))
        guiji_out5 = np.append([times1.T],ynew,axis = 0).T
        locaX_diff = guiji_out5[1:,1]-guiji_out5[0:-1,1]
        locaY_diff = guiji_out5[1:,2]-guiji_out5[0:-1,2]
        vel = np.sqrt(np.square(locaX_diff)+np.square(locaY_diff))/13.85
    #    print(vel.shape)
        vel_index = np.where(vel>4)
        vel[vel_index]=(vel[(vel_index[0]+1,)]+vel[(vel_index[0]-1,)])/2
        vel1 = np.append(vel[0],vel).reshape(times1.shape[0],1)    
        guiji_out6 = np.append(guiji_out5,vel1,axis = 1)
        return guiji_out,guiji_out6
    
        
    
    
    def database_cube(database):
        userName = pd.unique(database['userName'])    
        userName_length = userName.shape[0]
        database_tran = np.zeros((userName_length,86401,5)) 
        j = 0   
        print(userName)
        for userN in userName:
            user_data = database[database['userName'] == userN]
            guiji_out,guiji_out2 = resample(user_data)
            database_tran[j,:,:] = guiji_out2
            j = j+1
        return database_tran
    
    
    def distance(database_tran):   
        userName_length = database_tran.shape[0]
        database_distance = np.zeros((database_tran.shape[1],database_tran.shape[0],database_tran.shape[0]),dtype = "float")
        for index1 in range(userName_length-1):
            temp1 = database_tran[index1,:,1:3]
            for index2 in range(index1+1,userName_length):
                temp2 = database_tran[index2,:,1:3]
                temp_diff = np.sqrt(np.sum(np.square(temp2 - temp1),axis = 1))
                database_distance[:,index1,index2] = temp_diff
    #            database_distance[:,index2,index1] = temp_diff
        return database_distance    
    
    def time_tran(times):
        timearr = datetime.datetime.fromtimestamp(times)
    #    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timearr)
        return timearr
    
    
    def tranj_seg(guiji):
        guiji_out = {}
        guiji1 = guiji
    #    zz =np.zeros((guiji2.shape[0],1))
    #    guiji1 = np.append(guiji2,zz,axis = 1)
        diff = guiji1[1:-1,0]-guiji1[0:-2,0]
        diff_large = np.where(diff>30)[0]
        j=0
    #    print(diff_large.shape[0])
        if diff_large.shape[0]>0:
            if diff_large.shape[0] == 1:
    #            j += 1
                guiji_out[0] = guiji1[0:diff_large[0]+1,:]
                guiji_out[1] = guiji1[diff_large[0]+1:-1,:]
                
            else:
                guiji_out[j] = guiji1[0:diff_large[0]+1,:]
                diff_large = np.append(diff_large,guiji1.shape[0])
                for index in range(diff_large.shape[0]-1):
                    j += 1
    #                print(diff_large[index],diff_large[index+1])
    #                guiji1[diff_large[index]:diff_large[index+1],-1] = j
                    temp = guiji1[diff_large[index]+1:diff_large[index+1]+1,:]
                    if(temp.shape[0]>5):
                        guiji_out[j] = guiji1[diff_large[index]+1:diff_large[index+1]+1,:]
        else:
            guiji_out[j] = guiji1
        return guiji_out      
                
    def wander_detect(guiji):
        wander_tranj = {}
        for tranj in guiji:
    #        print(tranj)
            if (guiji[tranj].shape[0]>0):
                vel = np.mean(guiji[tranj][:,4])
                timelast = guiji[tranj][-1,0]-guiji[tranj][0,0]
    #            print(vel,timelast)
                if (vel > 0.5) & (timelast > 180.0):
                    wander_tranj.update({tranj : guiji[tranj]})
        
        return wander_tranj
    
    def wander_place(guiji,userName):
       
        ggkj = [4,9,37]
        guiji_out = {}
        j = 0
        for user in userName:
            data = guiji[j,:,:]
            j += 1
            guiji_out_temp ={}
            for place in ggkj:
                guiji_place = data[data[:,3] == place]
    #            print(guiji_place.shape)
                guiji_place_seg = tranj_seg(guiji_place)
                guiji_wander = wander_detect(guiji_place_seg)
                if (len(guiji_wander)>0):
                    guiji_out_temp.update({place:guiji_wander})
            guiji_out.update({user:guiji_out_temp})        
        return guiji_out    
    
    
    
    
    def hypervelocity(guiji,userName):
        kj = [4,9,23,24,25,37,39]
        guiji_out ={}
        j = 0
        for user in userName:
            data = guiji[j,:,:]
            j +=1
            guiji_out_temp = {}
            for place in kj:
                guiji_place = data[data[:,3] == place]
                guiji_hyper = guiji_place[signal.medfilt(guiji_place[:,4],5) > 0.8]
                if (guiji_hyper.shape[0]>2):
                    guiji_place_seg = tranj_seg(guiji_hyper)
                    guiji_out_temp.update({place:guiji_place_seg})
            guiji_out.update({user:guiji_out_temp})
        return guiji_out
    
    def datatimeToString(timestamp1,timestamp2):
        str1 = datetime.datetime.fromtimestamp(timestamp1).strftime("%H:%M:%S")
        str2 = datetime.datetime.fromtimestamp(timestamp2).strftime("%H:%M:%S")
        str3 = str1+'-'+str2
    #    print(str3)
        return str3
    
    def wander_chart(guiji,kj,chartname):
        
        jsonData = {}
        qujian = {}
        user_list = ['鲁工','李所','韩工','李工','崔工','巩所']
        if(chartname == 'wander'):        
            for user in user_list:
                qujian.update({user:[]})
                if(user in guiji):
                    guiji_temp = guiji[user] 
                    for place in guiji_temp:
                        for tranj in guiji_temp[place]:
        #                    print(guiji_temp[place][tranj].shape)
                            qujian[user].append({'x':(guiji_temp[place][tranj][0][0]+28800)*1000,
                                           'x2':(guiji_temp[place][tranj][-1][0]+28800)*1000,
                                           'y':kj.index(place),
                                           'partialFill':datatimeToString(guiji_temp[place][tranj][0][0],
                                                                          guiji_temp[place][tranj][-1][0])})
        
        if(chartname == 'hyper'):
            for user in user_list:
                qujian.update({user:[]})
                if(user in guiji):
                    guiji_temp = guiji[user] 
                    for place in guiji_temp:
                        for tranj in guiji_temp[place]:
        #                    print(guiji_temp[place][tranj].shape)
                            qujian[user].append({'x':guiji_temp[place][tranj][0][0]*1000,
                                           'x2':guiji_temp[place][tranj][-1][0]*1000,
                                           'y':kj.index(place),
                                           'partialFill':np.mean(guiji_temp[place][tranj][:,4])})
            
        
        jsonData [chartname] = qujian
        return jsonData        
           
    
    def hypervel(guiji,userName,kjlb):
        j =0
        jsonData = {}
        for user in userName:
            jsonData[user]=[]   
    #        for i in range(guiji.shape[1]):
            for i in range(guiji.shape[1]):
                jsonData[user].append({'x':(guiji[j,i,0]+28800)*1000,'y':guiji[j,i,4],'vel':kjlb[int(guiji[j,i,3])]})
            j += 1
        return jsonData
        
    

    
    def __init__(self):        
        ggkj = [4,9,37]
        kjlb = pd.Series(['八层','室外走廊','多功能活动室','卫生间','出口','室内走廊','陈',
                      '鲁','崔','卫','浴','韩','李','巩','江','海','起居室','走廊危险区'],
                        index = [1,4,9,23,24,25,27,28,29,30,31,32,33,34,35,36,37,39])
        database_quzao = quzao(database)
        database_tran = database_cube(database_quzao)
        database_distance = distance(database_tran)
        userName = pd.unique(database_quzao['userName']) 
        wander = wander_place(database_tran,userName)
        #hyper = hypervelocity(database_tran,userName)
        jsonData_wander = wander_chart(wander,ggkj,'wander')
        jsonData_wander['kongjian'] = ['室外走廊', '多功能活动室', '起居室']
        jsonData_hyper = hypervel(database_tran,userName,kjlb)
        app ={}
        app['yvalue']={'wander':jsonData_wander,'hyper':jsonData_hyper} 










