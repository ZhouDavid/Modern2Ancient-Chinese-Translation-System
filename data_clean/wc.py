import sys
import pandas as pd
import numpy as np
import re
#D:\data\\raw\europarl-v7-training\europarl-v7.fr-en.fr
file = open('D:\data\\raw\en-fr\\train.en','r')
file2 = open('D:\data\\raw\en-fr\\test.en','r')
freq = {}
for line in file.readlines():
	words = line.split()
	for w in words:
		if w in freq:
			f = freq[w]
			f+=1
			freq[w]=f
		else:
			freq[w]=1

# for line in file2.readlines():
# 	words = line.split()
# 	for w in words:
# 		if w in freq:
# 			f = freq[w]
# 			f+=1
# 			freq[w]=f
# 		else:
# 			freq[w]=1

ftup = sorted(freq.items(),lambda x,y:cmp(x[1],y[1]),reverse = True)

outfile = open('old_en_freq.txt','w')
for item in ftup:
	line = str(item[0])+" "+str(item[1])+'\n'
	outfile.write(line)
	