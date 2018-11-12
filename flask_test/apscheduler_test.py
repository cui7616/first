# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 18:08:10 2018

@author: ceedi
"""

from flask import Flask,render_template
from flask_apscheduler import APScheduler
from flask_apscheduler.auth import HTTPBasicAuth
import json
import datetime
import data


class Config(object):
    JOBS = [
        {
            'id': 'job1',
            'func': '__main__:job1',
            'args': (),
            'trigger': 'cron',
            'minute': '*/10'
        }
    ]

    SCHEDULER_API_ENABLED = True
    SCHEDULER_AUTH = HTTPBasicAuth()


def job1():
    nowTime=datetime.datetime.now().strftime('%Y-%m-%d')
    pastTime = (datetime.datetime.now()-datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    database_o = data.data(pastTime)
    database = database_o.database
    fileName = 'D:/newpro/flask_test/json'+pastTime+'.json' 
    fileObject = open(fileName, 'w',encoding='utf-8')  
    jsObj = json.dump(database,fileObject,ensure_ascii=False)   
    fileObject.close() 
    print(nowTime,pastTime)


if __name__ == '__main__':
    app = Flask(__name__)
    app.config.from_object(Config())

    scheduler = APScheduler()
    # it is also possible to set the authentication directly
    # scheduler.auth = HTTPBasicAuth()
    scheduler.init_app(app)
    scheduler.start()

    @scheduler.authenticate
    def authenticate(auth):
        return auth['username'] == 'guest' and auth['password'] == 'guest'
    @app.route('/')
    def hello():
        return render_template('my_template4.html')
    
    # /test路由 接收前端的ajax请求
    @app.route('/test',methods=['POST'])
    def my_echart():
    
        file = open('D:/newpro/flask_test/jsonFile3.json','r',encoding='utf-8')
        jsonData  = json.load(file)
    #    print(jsonData)
        # json.dumps()用于将dict类型的数据转成str，因为如果直接将dict类型的数据写入json会发生报错，因此将数据写入时需要用到该函数。
        j = json.dumps(jsonData)
        print(j)
    
    
        # 在浏览器上渲染my_template.html模板（为了查看输出的数据）
        return(j)

    app.run()