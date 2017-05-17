# -*- coding: utf-8 -*-
import os
import sys
import re
import sentence_sim

reload(sys)
sys.setdefaultencoding('utf8')
charset = u'，。,：?、”“—.！!》《\n'

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

def write_sentences(sentences,fout):
	ss = []
	sentences = map(lambda x:x.encode('utf-8')+u'。\n',sentences)
	for s in sentences:
		if len(s)>2:
			ss.append(s)
	fout.writelines(ss)


def split_sentence(sentence):
	sentence = unicode(sentence).strip()
	sentences = []
	sentences = sentence.split(u'。')
	return sentences


def find_match_sentence(origin_sentence,trans_sentences):
	count_box = [0]*len(trans_sentences)
	origin_sentence = sentence_sim.multiple_replace(origin_sentence,charset)
	for j, oc in enumerate(origin_sentence):
		for i in range(len(trans_sentences)):
			tmp_trans = sentence_sim.multiple_replace(trans_sentences[i],charset)
			if not tmp_trans.find(oc)==-1:
				count_box[i]+=1

	max_length = -1
	for i in range(len(trans_sentences)):
		if max_length < count_box[i]:
			max_length = count_box[i]
			index = i

	return trans_sentences[index],max_length

if __name__ == '__main__':
	input_path_list = ['E:\MSRA\dataset\\raw\zizhitongjian\origin8.txt','E:\MSRA\dataset\\raw\zizhitongjian\\trans8.txt']
	output_path_list=['E:\MSRA\dataset\\raw\zizhitongjian\\split_origin8.txt','E:\MSRA\dataset\\raw\zizhitongjian\\split_trans8.txt']
	# for i,path in enumerate(input_path_list):
	# 	file = open(path,'r')
	# 	fout = open(output_path_list[i],'w')
	# 	for line in file.readlines():
	# 		line = unicode(line)
	# 		sentences = split_sentence(line)
	# 		write_sentences(sentences,fout)
	# 		#write_split_line(sline,fout)
	# 	file.close()
	# 	fout.close()
	fin1 = open(input_path_list[0],'r')
	fin2 = open(input_path_list[1],'r')
	fout1 = open(output_path_list[0],'w')
	fout2 = open(output_path_list[1],'w')

	origin_sentences = fin1.readlines()
	trans_sentences = fin2.readlines()

	origin_sentences = map(lambda x:x.decode('utf-8').strip(),origin_sentences)
	trans_sentences = map(lambda x:x.decode('utf-8').strip(),trans_sentences)
	count = 0
	if len(origin_sentences)==len(trans_sentences): #理论上应该是相等的，因为句子数量是一样的
		length = len(origin_sentences)   
		for i in range(length):
			origin_split_sentences = split_sentence(origin_sentences[i])
			trans_split_sentences = split_sentence(trans_sentences[i])
			if len(origin_split_sentences) == len(trans_split_sentences):#split出来的数量相等才保留
				write_sentences(origin_split_sentences,fout1)
				write_sentences(trans_split_sentences,fout2)
			else:
				if len(origin_sentences[i])>50:
					for origin_sentence in origin_split_sentences:
						if len(origin_sentence)>0:
							trans_sentence,score = find_match_sentence(origin_sentence,trans_split_sentences)
							if score > 3:
								fout1.write(origin_sentence+u'。\n')
								fout2.write(trans_sentence+u'。\n')
								# print unicode(origin_sentence),'->',unicode(trans_sentence)
								# print score
								# input()
								count+=1
				elif len(origin_sentences[i])>1:
					fout1.write(origin_sentences[i]+u'。\n')
					fout2.write(trans_sentences[i]+u'。\n')
					

print count