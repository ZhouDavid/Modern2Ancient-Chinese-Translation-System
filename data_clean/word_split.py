# -*- coding: utf-8 -*-
import os
import sys
import jieba

reload(sys)
sys.setdefaultencoding('utf8')

def naive_split(line):
	'''无脑按照空格分所有词'''
	line = unicode(line)
	ans=[]
	for i in range(len(line)):
		ans.append(line[i])
	return ans

def write_split_line(sline,fout):
	line=''
	for ch in sline:
		line = line+ch+' '
	line = line.strip()
	fout.write(line+'\n')

input_path = ['D:\MSRA\\tot_trs']
output_path = ['D:\MSRA\\tot_trs_space_split']


for i,path in enumerate(input_path):
	fin = open(path,'r')
	fout = open(output_path[i],'w')
	for line in fin.readlines():
		# if i==0:
		# 	line = line.strip()
		# 	sline = jieba.cut(line)
		# 	sline = ' '.join(sline)
		# 	sline+='\n'
		# 	fout.write(sline)
		# else:
		# 	sline = naive_split(line)
		# 	write_split_line(sline,fout)
		sline = naive_split(line)
		write_split_line(sline,fout)






