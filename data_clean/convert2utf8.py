# -*- coding: utf-8 -*-
import chardet
import sys
import os

# root_path = ['E:\MSRA\dataset\《二十四史》（原版%252B白话文全集%252B原版清史稿 ）TXT\二十四史全文白话全集+清史稿 TXT\《二十四史+清史稿》作者：司马迁',\
# 'E:\MSRA\dataset\《二十四史》（原版%252B白话文全集%252B原版清史稿 ）TXT\二十四史全文白话全集+清史稿 TXT\二十四史白话文',\
# 'E:\MSRA\dataset\24history\24-origin','E:\MSRA\dataset\24history\24-trans']
root_path = 'E:\MSRA\dataset'
def convert(contents):
	ans=[]
	for line in contents:
		code = chardet.detect(line)['encoding']
		if not code==None:
			try:
				line = line.decode(code)
			except:
				pass
	return ans
def combine(path,name_list):
	new_name_list = []
	for name in name_list:
		new_name_list.append(path+'\\'+name)
	return new_name_list

for path in os.walk(root_path):
	name_list = path[2]
	root = path[0]
	name_list = combine(root,name_list)
	for name in name_list:
		file = open(name,'r')
		print name
		new_contents = convert(file.readlines())
		file.close()
		fout = open(name,'w')
		fout.writelines(new_contents)
		fout.close()



