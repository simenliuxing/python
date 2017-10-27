#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:liuxing

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
s = pd.Series([1,3,5,np.nan,6,8])
# print(s)

dates = pd.date_range('20130101',periods=6)
# print(dates)

df = pd.DataFrame(np.random.randn(6,4),index = dates,columns = ['a','b','c','d'])
# 查看数据
# print(df.head(2))
# print(df.tail(2))
# print(df.index)
# print(df.columns)
# print(df.values)
# print(df.describe())
# print(df.T)
# print(df.sort_index(axis=1, ascending=False))

# 选择
#       获取
# print(df['a'])
# print(df[0:3])
# print(df['20130102':'20130104'])
# print(df)
# print('')
#       通过标签选择
# print(df.loc[dates[0]])
# print(df.loc[:,['a', 'b']])
# print(df.loc['20130102':'20130104',['a', 'b']])
# print(df.loc['20130102',['a', 'b']])
# print(df.loc[dates[0],'a'])
# print(df.at[dates[0],'a'])

#       通过位置选择
# print(df.iloc[3])
# print(df.iloc[3:5,0:2])
# print(df.iloc[[1,2,4],[0,2]])
# print(df.iloc[1:3,:])
# print(df.iloc[:,1:3])
# print(df.iloc[1,1])
# print(df.iat[1,1])


#   布尔索引
# print(df[df.a>0])
# print(df[df>0])
df2 = df.copy()
df2['e'] = ['one', 'one', 'two', 'three', 'four', 'three']
# print(df2)
# print(df2[df2['e'].isin(['two', 'four'])])


#   设置
s1 = pd.Series([1,2,3,4,5,6],index=pd.date_range('20130102', periods=6))
# print(s1)
df['f'] = s1
df.at[dates[0],'a'] = 0
df.iat[0,1] = 0
df.loc[:,'d'] = np.array([5]*len(df))
df2 = df.copy()
# print(df2)
print()
df2[df2 > 0] = -df2
# print(df2)


#   缺失值处理
df1 = df.reindex(index=dates[0:4],columns=list(df.columns)+['e'])
df1.loc[dates[0]:dates[1],'e'] = 1
# df1 = df1.dropna(how='any')
# print(df1)
# df1 = df1.fillna(value=4)
df1 = pd.isnull(df1)
# print(df1)


#   相关操作
# print(df.mean())
# print(df.mean(1))
# print(df.apply(np.cumsum))
# print(df)
# print(df.apply(lambda  x :x.max() - x.min()))
s = pd.Series(np.random.randint(0,7,size=10))
# print(s)
# print(s.value_counts())
# print(s.value_counts())



#   合并
df = pd.DataFrame(np.random.randn(10,4))
print(df)
pieces = [df[:3],df[3:7],df[7:3]]
print(pd.concat(pieces))


















