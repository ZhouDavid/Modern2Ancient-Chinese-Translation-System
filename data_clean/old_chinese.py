# -*- coding: utf-8 -*-
import os
import numpy as np
import sys
import re
import chardet

reload(sys)
sys.setdefaultencoding('utf8')
'''
处理要点：
1. 要把原文中的空行全部去掉
2. 原文中的-----，开头是资治通鉴第xx、资治通览第xx的行都要去掉
3. 译文中每句话中间有可能有>,直接replace 就好
'''
chinesePattern = re.compile(u'[\u4e00-\u9fa5]+')

f = open('D:\data\\raw\zizhi\out6.txt','r')
#ff = open('D:\data\\raw\zizhi\out6.txt','w')
# fout = open('out5.txt','w')
# for line in f.readlines():
# 	line = unicode(line)
# 	if line=='　\n':
# 		continue
# 	fout.write(line)
def is_bad_line(line):
	count=0
	pos = -1
	for i,c in enumerate(line):
		if c == '[':
			count+=1
			pos = i
	if count>1:
		return pos

	return -1

# def 
fout1 = open('D:\data\\raw\zizhi\\origin.txt','w')
fout2 = open('D:\data\\raw\zizhi\\trans.txt','w')
line_num = 1
count = 0

lines = []
for i,line in enumerate(f.readlines()):
	pos = is_bad_line(line)
	if not pos == -1:
		new_line = line[pos:len(line)]
		old_line = line[0:pos-1]+'\n'
		lines.append(old_line)
		lines.append(new_line)
	else:
		lines.append(line)

for line in lines:
	#ff.write(line)
	line = line.replace('>','')
	if line_num%2:
		fout1.write(line.strip()+'\n')
	else:
		fout2.write(line.strip()+'\n')
	line_num+=1

		
fout1.close()
fout2.close()

