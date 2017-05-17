#-*- coding:utf-8 -*-
import chardet
import re


charset = u'，。,：?、”“—.！!》《'

def multiple_replace(text, cdict):  
   	for i in cdict:
   		text = text.replace(i,'')
   	return text

def similarity(origin_sentence,trans_sentence):
	num = 0
	step = 3
	origin_sentence = origin_sentence.decode('utf-8')
	trans_sentence = trans_sentence.decode('utf-8')
	origin_sentence  = multiple_replace(origin_sentence,charset)
	trans_sentence = multiple_replace(trans_sentence,charset)

	for char in origin_sentence:
		if char in trans_sentence:
			num+=1

	return float(num)/(len(origin_sentence)+len(trans_sentence)),(num,len(origin_sentence),len(trans_sentence))
	
if __name__ == '__main__':
	# line1 = u'天下有不顺者，黄帝从而征之，平者去之，披山通道，未尝宁居。'
	# line2 = u'天下有不顺从的,黄帝便去征讨,平服了的地方,黄帝便带兵离开。披荆斩棘,开山通道,从没安逸地过日子。'
	lines = open('tmp.txt').readlines()
	line1 = lines[0]
	line2 = lines[1]
	print similarity(line1,line2)	
