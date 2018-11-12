# -*- coding: utf-8 -*-
"""
Created on Sat Oct 27 14:23:23 2018

@author: czmy
"""

from flask import Flask,render_template,url_for
import json
import time

# 生成Flask实例
app = Flask(__name__)



#def get_chartdata():
    

@app.route('/')
def hello():
    return render_template('my_template4.html')

# /test路由 接收前端的ajax请求
@app.route('/test',methods=['POST'])
def my_echart():

    file = open('E:/20181101/flask_test/jsonFile3.json','r',encoding='utf-8')
    jsonData  = json.load(file)
    
#    print(jsonData)
    # json.dumps()用于将dict类型的数据转成str，因为如果直接将dict类型的数据写入json会发生报错，因此将数据写入时需要用到该函数。
    j = json.dumps(jsonData)
#    print(j)


    # 在浏览器上渲染my_template.html模板（为了查看输出的数据）
    return(j)


if __name__ == '__main__':
    # 运行项目
    app.run(threaded=True)
#    app.run(host='0.0.0.0')