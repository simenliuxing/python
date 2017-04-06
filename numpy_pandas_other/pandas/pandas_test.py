#!/usr/bin/env python
# -*- coding:utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# numpy.random随机数
# print np.random.random(3)
# print np.random.rand(3,4)
# print np.random.randn(3,4)

# 创建
s = pd.Series([1,2,6,np.nan,44,4])
dates = pd.date_range('20170406',periods = 6)
df = pd.DataFrame(np.random.randn(6,4),index = dates,columns = ['a','b','c','d'])
df = pd.DataFrame(np.arange(12).reshape(3,4))
df2 = pd.DataFrame({ 'A' : 1.,  
					 'B' : pd.Timestamp('20130102'),
					 'C' : pd.Series(1,index=list(range(4)),dtype='float32'),
					 'D' : np.array([3] * 4,dtype='int32'),
					 'E' : pd.Categorical(["test","train","test","train"]),
				 	 'F' : 'foo' })
# 属性
# print df2.dtypes
# print df2.index
# print df2.columns
# print df2.values
# print df2.describe()
# print df2.T
# axis=1 横向排序，axis=0 纵向排序,都是以index/columns排序
# print df2.sort_index(axis=1,ascending = False)
# print df2.sort_index(axis=0,ascending = False)
# print df2.sort_values(by='E',ascending = False)


# 选择数据
dates = pd.date_range('20170406',periods = 6)
df = pd.DataFrame(np.arange(24).reshape(6,4),index = dates,columns = ['a','b','c','d'])

# 选择列
# print df.a
# print df['a']

# 选择行
# print df[0:3]
# print df['2017-04-06':'2017-04-08']

# 标签选择 select by label
# print df.loc['20170406']
# print df.loc[:,['a','b']]
# print df.loc['20170406',['a','b']]
# print df.loc['2017-04-06',['a','b']]

# 位置选项 select by position
# print df.iloc[5,3]
# print df.iloc[3:5,1:3]
# print df.iloc[[1,3,5],1:3]

# 标签选择和位置选择混合,mixed selection:ix
# print df.ix[:3,['a','c']]

# booean indexing
# print df[df.a>8]


# 设置值
dates = pd.date_range('20170406',periods = 6)
df = pd.DataFrame(np.arange(24).reshape(6,4),index = dates,columns = ['a','b','c','d'])
df.iloc[2,2] = 1111
df.loc['20170406','b'] = 222222
# a列>4的所有行列
df[df.a>4] = 0
# a列>4的所有行,a列
df.b[df.a>4] = 0
df['f'] = np.nan
df['f'] = pd.Series([1,2,3,4,5,6],index=pd.date_range('20170406',periods = 6))
# print df


# 处理丢失数据
dates = pd.date_range('20170406',periods = 6)
df = pd.DataFrame(np.arange(24).reshape(6,4),index = dates,columns = ['a','b','c','d'])
df.iloc[0,1] = np.nan
df.iloc[1,2] = np.nan
# 丢掉行axis=0，how={'any','all'},any有一个nan则丢弃，all全部则丢弃
df = df.dropna(axis=0,how='any')
# 数据填充
df = df.fillna(value = 0)
# 判断是否是nan
# print df.isnull()
# 是否包含nan的值
# print np.any(df.isnull())==True
# print df


# pandas 导入导出
data = pd.read_csv('Student.csv')
# data.to_pickle('Student.pickle')
# print type(data)
data = pd.read_pickle('Student.pickle')
# print data


# 合并 concatenating
df1 = pd.DataFrame(np.ones((3,4))*0,columns=['a','b','c','d'])
df2 = pd.DataFrame(np.ones((3,4))*1,columns=['a','b','c','d'])
df3 = pd.DataFrame(np.ones((3,4))*2,columns=['a','b','c','d'])
# 上下合并axis=0纵向合并，axis=1横向合并,ignore_index = True重新索引
res = pd.concat([df1,df2,df3],axis=0,ignore_index = True)
# join,['inner','outer']
df1 = pd.DataFrame(np.ones((3,4))*0,columns=['a','b','c','d'],index=[1,2,3])
df2 = pd.DataFrame(np.ones((3,4))*1,columns=['b','c','d','e'],index=[2,3,4])
res = pd.concat([df1,df2],join='inner',ignore_index=True)
# 左右合并，join_axes,用df1的索引,缺省用nan,多余丢弃
res = pd.concat([df1,df2],axis=1,join_axes=[df1.index])
# 缺省用nan
res = pd.concat([df1,df2],axis=1)
# print res
# append
df1 = pd.DataFrame(np.ones((3,4))*0,columns=['a','b','c','d'])
df2 = pd.DataFrame(np.ones((3,4))*1,columns=['b','c','d','e'],index=[2,3,4])
df2 = pd.DataFrame(np.ones((3,4))*1,columns=['a','b','c','d'])
df3 = pd.DataFrame(np.ones((3,4))*1,columns=['a','b','c','d'])
# 往下追加
res = df1.append([df2,df3],ignore_index=True)
# 添加一行
s1 = pd.Series([1,2,3,4],index=['a','b','c','d'])
res = df1.append(s1,ignore_index=True)
# print res


# merge合并
left = pd.DataFrame({'key':['K0','K1','K2','K3'],
					'A':['A0','A1','A2','A3'],
					'B':['B0','B1','B2','B3']})
right = pd.DataFrame({'key':['K0','K1','K2','K3'],
					'C':['C0','C1','C2','C3'],
					'D':['D0','D1','D2','D3']})
# 基于key这个列的合并
res = pd.merge(left,right,on='key')
left = pd.DataFrame({'key1':['K0','K0','K1','K2'],
				     'key2':['K0','K1','K0','K1'],
					'A':['A0','A1','A2','A3'],
					'B':['B0','B1','B2','B3']})
right = pd.DataFrame({'key1':['K0','K1','K1','K2'],
					  'key2':['K0','K0','K0','K0'],
					'C':['C0','C1','C2','C3'],
					'D':['D0','D1','D2','D3']})
# 两个列的合并 how=[left,right,outer,inner],sql中两个表的链接
res = pd.merge(left,right,on=['key1','key2'],how='right')

# indicator显示merge是如何合并的
df1 = pd.DataFrame({'col1':[0,1], 'col_left':['a','b']})
df2 = pd.DataFrame({'col1':[1,2,2],'col_right':[2,2,2]})
# res = pd.merge(df1,df2,on='col1',how='outer',indicator=True)
res = pd.merge(df1,df2,on='col1',how='outer',indicator='indicator_colunm')



# merged by index
left = pd.DataFrame({'A': ['A0', 'A1', 'A2'],
                     'B': ['B0', 'B1', 'B2']},
                      index=['K0', 'K1', 'K2'])
right = pd.DataFrame({'C': ['C0', 'C2', 'C3'],
                      'D': ['D0', 'D2', 'D3']},
                       index=['K0', 'K2', 'K3'])
res = pd.merge(left,right,left_index=True,right_index=True,how='outer')
res = pd.merge(left,right,left_index=True,right_index=True,how='inner')



# handle 给列重命名
boys = pd.DataFrame({'k': ['K0', 'K1', 'K2'], 'age': [1, 2, 3]})
girls = pd.DataFrame({'k': ['K0', 'K0', 'K3'], 'age': [4, 5, 6]})
res = pd.merge(boys,girls,on='k',suffixes=['_boy','_girl'],how='outer')
# print girls
# print res


#  数据可视化 plot data
# Series
data = pd.Series(np.random.randn(1000),index=np.arange(1000))
data = data.cumsum()
# data.plot()
# plt.show()

# DataFrame
data = pd.DataFrame(np.random.randn(1000,4),
					index=np.arange(1000),
					columns=list('ABCD'))
data = data.cumsum()
# print data.head()
# plot的方法 bar hist box kde area scatter hexbin pie
# data.plot()
ax = data.plot.scatter(x='A', y='B', color='DarkBlue', label="Class 1")
data.plot.scatter(x='A', y='C', color='LightGreen', label='Class 2', ax=ax)
plt.show()