# -*- coding: utf-8 -*-
"""
Created on Sun Nov 11 11:40:10 2018

@author: czmy
"""

import pymysql
from sqlalchemy import create_engine
import pandas as pd
connect = create_engine('mysql+pymysql://root:cuizhen@localhost:3306/uwb?charset=utf8')
pd.io.sql.to_sql(database,'databse',connect,schema='uwb',if_exists='append')

## 打开数据库连接
#db = pymysql.connect("localhost","root","cuizhen","uwb" )
# 
## 使用 cursor() 方法创建一个游标对象 cursor
#cursor = db.cursor()
# 
## 使用 execute()  方法执行 SQL 查询 
#cursor.execute("SELECT VERSION()")
# 
## 使用 fetchone() 方法获取单条数据.
#data = cursor.fetchone()
# 
#print ("Database version : %s " % data)
# 
## 关闭数据库连接
#db.close()