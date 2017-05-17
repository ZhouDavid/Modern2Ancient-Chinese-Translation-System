# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')


path = 'D:\data\clean\zizhitongjian\split_origin2.txt'
symbolDict = {}
fin = open(path)
for line in fin.readlines():
	line = unicode(line)
	line = line.strip()
	s = line[len(line)-1]
	if not s in symbolDict:
		symbolDict[s]=1
	else:
		c = symbolDict[s]
		c+=1
		symbolDict[s] = c

ftup = sorted(symbolDict.items(),lambda x,y:cmp(x[1],y[1]),reverse = True)

out = open('symbolDict.txt','w')
for item in ftup:
	line = str(item[0])+" "+str(item[1])+'\n'
	out.write(line)
out.close()
fin.close()