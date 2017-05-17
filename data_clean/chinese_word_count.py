# -*- coding: utf-8 -*-
import sys
import chardet

reload(sys)
sys.setdefaultencoding('utf8')

inPath = 'D:\data\shiji.txt'
fin = open(inPath)
word_num = 0
symbol = ['，','。',' ','！','：','“','”','《','》','（','）','、','*']
i = 0
for line in fin.readlines():
	line = unicode(line)
	for s in symbol:
		line = line.replace(s,'')
	word_num+=len(line)
	i+=1
print word_num
fin.close()

