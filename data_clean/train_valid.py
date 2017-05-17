# -*- coding: utf-8 -*-
import sys
import os
import math
path_list = ['Z:\\v-zjiany\public\data\clean\zizhitongjian\max_length_20','Z:\\v-zjiany\public\data\clean\zizhitongjian\max_length_30',\
'Z:\\v-zjiany\public\data\clean\zizhitongjian\max_length_40','Z:\\v-zjiany\public\data\clean\zizhitongjian\max_length_50']
valid_rate = 0.01
for path in path_list:
	file_list = os.listdir(path)
	i = 0
	while i < len(file_list):
		if not file_list[i].endswith('.txt'):
			del file_list[i]
			i-=1
		i+=1
	file_list = map(lambda x:path+'\\'+x,file_list)
	for file in file_list:
		valid_set=[]
		train_set = []
		lines = open(file,'r').readlines()
		step = int(1/valid_rate)
		for i in range(len(lines)):
			if i%step ==0:
				valid_set.append(lines[i])
			else:
				train_set.append(lines[i])
		open(file[0:len(file)-4]+'_valid.txt','w').writelines(valid_set)
		open(file[0:len(file)-4]+'_train.txt','w').writelines(train_set)
