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
import data
import copy

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
    
    time1 = time.mktime((2018, 10, 25, 0, 0, 0, 3,200,-1))   
    time2 = time.mktime((2018, 10, 26, 0, 0, 0, 3,200,-1))
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
#    database_distance = np.zeros((database_tran.shape[1],database_tran.shape[0],database_tran.shape[0]),dtype = "float")
    database_place = np.zeros((database_tran.shape[1],database_tran.shape[0],database_tran.shape[0]),dtype = "float")
#    database_vel = np.zeros((database_tran.shape[1],database_tran.shape[0],database_tran.shape[0]),dtype = "float")
    for index1 in range(userName_length-1):
        temp1 = database_tran[index1,:,1:3]
        temp1_2 = database_tran[index1,:,3]
        temp1_3 = database_tran[index1,:,4]
        for index2 in range(index1+1,userName_length):
            temp2 = database_tran[index2,:,1:3]
            temp2_2 = database_tran[index2,:,3]
            temp2_3 = database_tran[index2,:,4]
            temp_diff = np.sqrt(np.sum(np.square(temp2 - temp1),axis = 1))/13.85
            temp3 = copy.copy(temp1_2)
            temp3[(temp1_3>0.5)|(temp2_3>0.5)|(temp1_2 != temp2_2)|(temp_diff>1.1)] = 0
            database_place[:,index1,index2] = temp3
    return database_place    

def sub_tranj(guiji,index2,times2,userName,ggkj):
    ggkj = [4,9,37]
    guiji[guiji != index2] = 0
    guiji_out = {}
    j = 0
    temp = []
    user = []
    for i in range(guiji.shape[0]-1):
        if np.sum(guiji[i+1,:,:]-guiji[i,:,:]) == 0:
            qiepian = guiji[i,:,:]
            itemindex = np.argwhere(qiepian == index2)
            user_sub = userName[np.unique(itemindex)]            
            user = list(set(user).union(set(user_sub)))
            temp.append(i)
        else:
            if len(temp)>20 and (index2 in ggkj):
                guiji_out[j]={'x':(times2[temp[0]])*1000,'x2':(times2[temp[-1]])*1000,'y':ggkj.index(index2),'partialFill':'-'.join(user)}
                j +=1
            temp = []
            user = []            
    if len(temp)>20 and (index2 in ggkj):
#        print(index2)
        guiji_out[j] = {'x':(times2[temp[0]])*1000,'x2':(times2[temp[-1]])*1000,'y':ggkj.index(index2),'partialFill':'-'.join(user)}
    
    guiji_out2 = {}
    j = 0
    if len(guiji_out)>2:
        temp2 = guiji_out[0]
        for i in range(len(guiji_out)-1):
            if len(set(guiji_out[i]['partialFill']).difference(set(guiji_out[i+1]['partialFill']))) == 0 and guiji_out[i+1]['x']-guiji_out[i]['x2'] <50000:
                temp2['x2'] = guiji_out[i+1]['x2']
            else:
                guiji_out2[j] = temp2
                j += 1
                temp2 = guiji_out[i+1]
        guiji_out2[j] = temp2 
    else:
       guiji_out2 =  guiji_out                    
    return guiji_out2


def juji_detect(guiji,userName,times2,ggkj):
#    ggkj = [4,9,37]
    kongjian = np.unique(guiji)
    kongjian_guolv = kongjian[kongjian != 0]
    guiji_out_out = {}
    for index in kongjian_guolv:
        times = np.unique(np.where(guiji==index)[0])
        j = 0
        guiji_out = {}
        temp = []
        for i in range(times.shape[0]-1):
            if times[i+1]-times[i]<30:
                temp.append(times[i])
            else:
                if len(temp)>20:
                    guiji_temp = guiji[temp,:,:]
                    guiji_out[j] = sub_tranj(guiji_temp,index,times2[temp],userName,ggkj)
                    j += 1
                temp = []
        if len(temp)>20:
            guiji_temp = guiji[temp,:,:]
            guiji_out[j] = sub_tranj(guiji_temp,index,times2[temp],userName,ggkj)
        guiji_out_out[index] = guiji_out    
        guiji_out_out2 = [slide for (k,v) in guiji_out.items() for (k,slide) in v.items()]     
    return guiji_out_out2 


def time_tran(times):
    timearr = datetime.datetime.fromtimestamp(times)
    return timearr


def tranj_seg(guiji):
    guiji_out = {}
    guiji1 = guiji
    diff = guiji1[1:-1,0]-guiji1[0:-2,0]
    diff_large = np.where(diff>30)[0]
    j=0
    if diff_large.shape[0]>0:
        if diff_large.shape[0] == 1:
            guiji_out[0] = guiji1[0:diff_large[0]+1,:]
            guiji_out[1] = guiji1[diff_large[0]+1:-1,:]
            
        else:
            guiji_out[j] = guiji1[0:diff_large[0]+1,:]
            diff_large = np.append(diff_large,guiji1.shape[0])
            for index in range(diff_large.shape[0]-1):
                j += 1
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
            if (guiji[tranj].shape[0]>600):
                guiji_sub = np.empty(shape = [0,5])
                for sub_tran in range(math.floor(guiji[tranj].shape[0]/180)):
                    guiji_sub_tran = guiji[tranj][sub_tran*180:(sub_tran+1)*180,:]
                    vel = np.mean(guiji_sub_tran[:,4])
                    if vel > 0.5:
                        guiji_sub = np.append(guiji_sub,guiji_sub_tran,axis = 0)
#                        guiji_sub.append(guiji_sub_tran)
                if guiji_sub.shape[0]!=0:
                    wander_tranj.update({tranj : guiji_sub})
            else:
                if (vel > 0.5) & (timelast > 180.0):
                    wander_tranj.update({tranj : guiji[tranj]})
    
    return wander_tranj

def wander_place(guiji,userName):
   
    ggkj = [4,9,37]
    guiji_out = {}
    j = 0
    for user in userName:
        data_slice = guiji[j,:,:]
        j += 1
        guiji_out_temp ={}
        for place in ggkj:
            guiji_place = data_slice[data_slice[:,3] == place]
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
        data_slice = guiji[j,:,:]
        j +=1
        guiji_out_temp = {}
        for place in kj:
            guiji_place = data_slice[data_slice[:,3] == place]
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
                        qujian[user].append({'x':(guiji_temp[place][tranj][0][0]+28800)*1000,
                                       'x2':(guiji_temp[place][tranj][-1][0]+28800)*1000,
                                       'y':kj.index(place),
                                       'partialFill':datatimeToString(guiji_temp[place][tranj][0][0],
                                                                      guiji_temp[place][tranj][-1][0])})
        
    jsonData [chartname] = qujian
    return jsonData        
       

def hypervel(guiji,userName,kjlb):
    j =0
    jsonData = {}
    for user in userName:
        jsonData[user]=[]   
#        for i in range(guiji.shape[1]):
        for i in range(guiji.shape[1]-1):
            if guiji[j,i,4]!=0 or guiji[j,i+1,4]!=0:
                jsonData[user].append({'x':(guiji[j,i,0]+28800)*1000,'y':guiji[j,i,4],'vel':kjlb[int(guiji[j,i,3])]})
#            jsonData[user].append({'x':guiji[j,i,0]*1000,'y':guiji[j,i,4],'vel':kjlb[int(guiji[j,i,3])]})
        j += 1
    return jsonData


    
    

kjlb = pd.Series(['八层','室外走廊','多功能活动室','卫生间','出口','室内走廊','陈',
                  '鲁','崔','卫','浴','韩','李','巩','江','海','起居室','走廊危险区'],
                    index = [1,4,9,23,24,25,27,28,29,30,31,32,33,34,35,36,37,39])

#database = database.database
ggkj = [4,9,37]
qbkj = [4,9,23,24,25,37,39]
database_quzao = quzao(database)
database_tran = database_cube(database_quzao)
database_distance = distance(database_tran)
userName = pd.unique(database_quzao['userName']) 
jsonData_juji = juji_detect(database_distance,userName,times,ggkj)
wander = wander_place(database_tran,userName)
#hyper = hypervelocity(database_tran,userName)
jsonData_wander = wander_chart(wander,ggkj,'wander')
jsonData_wander['kongjian'] = ['室外走廊', '多功能活动室', '起居室']
jsonData_hyper = hypervel(database_tran,userName,kjlb)
#jsonData_hyper = wander_chart(hyper,qbkj,'hyper')
#jsonData_hyper['kongjian'] = ['室外走廊', '多功能活动室', '卫生间','出口','室内走廊','起居室','走廊危险区']
#
app ={}
app['yvalue']={'wander':jsonData_wander,'hyper':jsonData_hyper,'juji':jsonData_juji} 





times = database_tran[1,:,0]
#otherStyleTime = list(map(time_tran,times))
#
#fig, ax = plt.subplots(figsize=(15, 7.5))
#ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
##plt.figure("map2",figsize=(15, 7.5))
#plt.plot_date(otherStyleTime,list(database_tran[1,:,2]),'-')
#plt.show()
##
##img=Image.open('H:/20181019/map2.png')
#
##lugong_data = database_tran[1,:,:]
#
#
#fileObject = open('E:/20181101/flask_test/jsonFile3.json', 'w',encoding='utf-8')  
#jsObj = json.dump(app,fileObject,ensure_ascii=False)   
#fileObject.close()  
##
##lugong_hyper = hypervelocity(lugong_data)
#
#
##lugong_37 = lugong_data[lugong_data[:,3] == 37]
##lugong_37_seg = tranj_seg(lugong_37)
##lugong_wander = wander_detect(lugong_37_seg)
##lugong_37_vel = np.mean(lugong_37[:,4])
#
###lugong_out = quzao(lugong)
###guiji_out,guiji_out2=resample(lugong_out)
###guiji_37 = gonggong(lugong_out,37)
###velocity1 = velocity(guiji_37)
#
#plt.figure("map2",figsize=(15, 7))
##plt.imshow(img)
##plt.plot(guiji_out2[:,1],guiji_out2[:,2],'.',linewidth=0.001)
#plt.plot(otherStyleTime,signal.medfilt(lugong_data[:,4],3),'.')
#plt.show()




#line = Line("速度") 
#line.add("速度", list(lugong_data[:,0].T), list(lugong_data[:,4].T),line_width=2,is_datazoom_show=True) 
#line.render()


