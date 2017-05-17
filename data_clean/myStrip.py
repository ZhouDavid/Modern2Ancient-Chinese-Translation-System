# -*- coding: utf-8 -*-
inPath = 'D:\data\clean\zizhitongjian\split_trans2.txt'
def myStrip(line):
	if line.startwith('['):
		start = line.find(']')+1
		end = line.find('*')
		line
fin = open(inPath)
