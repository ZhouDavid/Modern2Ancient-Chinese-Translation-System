# -*- coding: utf-8 -*-
import os
import sys

reload(sys)
sys.setdefaultencoding('utf8')

input_path1 = 'D:\data\\raw\zizhi\\origin.txt'
input_path2 = 'D:\data\\raw\zizhi\\trans.txt'
output_path1 = 'D:\data\\raw\zizhi\\origin2.txt'
output_path2 = 'D:\data\\raw\zizhi\\trans2.txt'

fin1 = open(input_path1,'r')  
fin2 = open(input_path2,'r')
fout1 = open(output_path1,'w')
fout2 = open(output_path2,'w')

line_index = 0
line_index_list = []
count=0
for line in fin1.readlines():
	line = unicode(line)
	if len(line)<3: #碰到一个空行，直接跳过
		continue
	if line[0]=='　':
		line_index_list.append(line_index)
		line=line[2:len(line)]
		if line.startswith('['):
			start = line.find(']')
			line = line[start+1:len(line)]

		fout1.write(line)
		count+=1
	line_index+=1
	
fout1.close()

print count
print len(line_index_list)

lines = fin2.readlines()


for i in line_index_list:
	line = unicode(lines[i])
	if line.startswith('　'):
		line=line[2:len(line)]
	if line.startswith('['):
		start = line.find(']')
		line = line[start+1:len(line)]
	fout2.write(line)

fout2.close()

