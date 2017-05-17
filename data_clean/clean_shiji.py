#-*- coding:utf-8 -*-
import chardet
import pdb
from sentence_sim import similarity
#in_origin_path = 'E:\MSRA\dataset\\twenty_four_history\\total_origin\shiji.txt'
in_origin_path = 'D:\MSRA\dataset\\raw\\twenty_four_history-v2\origin\shiji.txt'
in_trans_path = 'D:\MSRA\dataset\\raw\\twenty_four_history-v2\\trans\shiji.txt'
out_origin_path = 'D:\MSRA\dataset\\raw\\twenty_four_history\shiji\shiji_origin.txt'
out_trans_path = 'D:\MSRA\dataset\\raw\\twenty_four_history\shiji\shiji_trans.txt'

sim_threshold = 0.1

def find_title(line,titles):
	for i,title in enumerate(titles):
		if not line.find(title)==-1:
			return i
	return -1

def deal_with_shiji_origin(in_origin_path,out_origin_path,in_trans_path,out_trans_path):
	'''
	处理原文
	'''
	file = open(in_origin_path,'r')
	lines = file.readlines()
	lines =map(lambda x:x.decode('utf-8'),lines)
	file.close()
	titles = []
	context = lines[0:len(lines)]  #正文
	articles = []
	article = ''
	para = ''
	for i,line in enumerate(context):
		index = line.find(u'●')
		if not index ==-1:
			if len(article)>0:
				articles.append(article+para+'</para>\n</article>\n')
				para = ''
			cur_title = line[index+3:len(line)]
			titles.append(cur_title)
			start = cur_title.find(u'·')+2
			end = cur_title.find(u'第')
			cur_title= cur_title[start:end]
			article = '<article>\n  <title>'+cur_title.strip()+'</title>\n'

		else:
			if line.startswith(u'　　'):
				if len(para)>0:
					article+=para+'</para>\n'
				para = '  <para>'+line.strip()
			else:
				line = line.strip()
				line = line.replace(u'-',u'')
				if len(line)>0:
					para += line

	articles.append(article+para+'</para>\n</article>')
	file = open(out_origin_path,'w')

	articles = map(lambda x:x.encode('utf-8'),articles)
	file.writelines(articles)
	file.close()

	# '''
	# 处理译文
	# '''
	# got_titles=[]
	# def is_title(line):
	# 	for title in titles:
	# 		start = title.find('·')+2
	# 		end = title.find('第')
	# 		title= title[start:end]
	# 		if line.startswith(title):
	# 			got_titles.append(title+'\n')
	# 			return end-start
	# 	return -1

	# file=open(in_trans_path,'r')
	# lines = file.readlines()
	# file.close()
	# para =''
	# paras=[]
	# title_num = 0
	# for line in lines:
	# 	name_length = is_title(line)
	# 	if name_length>0:
	# 		title_num+=1
	# 		if len(para)>0:
	# 			paras.append(para+'</article>\n')
	# 		para ='<article>\n  <title>'+line[0:name_length].strip()+'</title>\n'+line[name_length:len(line)].strip()
	# 	else:
	# 		para+=line.strip()
	# print title_num
	# paras.append(para)
	# file=open(out_trans_path,'w')
	# file.writelines(paras)
	# file.close()

	# leak = []
	# clean_titles=[]
	# for title in titles:
	# 	start = title.find('·')+2
	# 	end = title.find('第')
	# 	title= title[start:end]
	# 	clean_titles.append(title+'\n')

	'''
	筛选出在译文中的篇目
	'''
	# for i in clean_titles:
	# 	if not i in got_titles:
	# 		leak.append(i)
	# file = open('tmp.txt','w')
	# file.writelines(leak)
	# file.close()
def abstract_title(line):
	start = line.find('<title>')
	end = line.find('</title>')
	start += 7
	title = line[start:end]
	return title

def abstract_content(line):
	start = line.find('</title>')+8
	end = line.find('</p>')
	return line[start:end]

def sentence_split(in_origin_path,in_trans_path,out_origin_path,out_trans_path):
	fin1 = open(in_origin_path,'r')
	fin2 = open(in_trans_path,'r')
	origin_lines = fin1.readlines()
	trans_lines = fin2.readlines()
	fin1.close()
	fin2.close()
	i = 0

	fout1 = open(out_origin_path,'w')
	fout2 = open(out_trans_path,'w')

	for j,trans_line in enumerate(trans_lines):
		trans_title = abstract_title(trans_line)
		cur_origin_title = abstract_title(origin_lines[i])

		while not trans_title == cur_origin_title:
			i+=1
			try:
				cur_origin_title = abstract_title(origin_lines[i])
			except:
				print i,j
				input()

		trans_content = abstract_content(trans_line)
		origin_content = abstract_content(origin_lines[i])
		trans_sentences = trans_content.split('。')
		origin_sentences = origin_content.split('。')
		origin_sentences = map(lambda s:s+'。\n',origin_sentences)
		trans_sentences=map(lambda s:s+'。\n',trans_sentences)
		fout1.writelines(origin_sentences)
		fout2.writelines(trans_sentences)
		i+=1

	fout1.close()
	fout2.close()

def sentence_alignment(in_origin_path,in_trans_path):
	origin_sentences = open(in_origin_path,'r').readlines()
	trans_sentences = open(in_trans_path,'r').readlines()
	pair = []
	if len(origin_sentences)<len(trans_sentences):
		for i,s in enumerate(origin_sentences):
			print similarity(s,trans_sentences[i])
	else:
		i = 0 #trans 指针
		j = 0 #origin 指针
		for trans in trans_sentences:
			try:
				origin_sim,_ = similarity(origin_sentences[j],trans)
				print _
				input()
				if origin_sim < sim_threshold:
					#origin不动，向前添加trans
					print (i,origin_sim)
					new_trans = trans.strip()+trans_sentences[i+1].strip()
					cur_sim = similarity(origin_sentences[j],new_trans)
					print (i,cur_sim)
					input()
					if origin_sim<cur_sim and cur_sim>=sim_threshold:
						pair.append((origin_sentences[i],new_trans))
						i+=1
					else:
						#trans不动,向前添加origin
						new_origin = origin_sentences[j].strip()+origin_sentences[j+1].strip()
						cur_sim = similarity(new_origin,trans)
						if origin_sim < cur_sim and cur_sim >=sim_threshold:
							pair.append((new_origin,trans))
							j+=1
				else:
					pair.append((origin_sentences[i],trans))
			except Exception,e:
				print e
				input()
			i+=1
			j+=1
	
def abstract_trans(input_path):
	'''
	从说明、原文、注解中抽取译文中
	'''
	trans = open(input_path,'r').readlines()
	#trans = map(lambda x:x.decode('utf-8'),trans)
	title_list = open('D:\MSRA\dataset\category\shiji_category.txt','r').readlines()
	title_list = map(lambda x:x.decode('utf-8'),title_list)
	articles = []
	out = open('D:\MSRA\dataset\\raw\\twenty_four_history\shiji\shiji_trans.txt','w')
	is_in_content = False
	article=''
	for i,line in enumerate(trans):
		if not line.find('【原文】')==-1:
			article+='</article>\n'
			articles.append(article)
			is_in_content = False	
		if is_in_content:
			line = line.strip()
			if len(line)>0:
				article+='  <para>'+line+'</para>\n'
		else:				
			if not line.find('《史记》译注')==-1:
				article = '<article>\n  <title>'+trans[i+1].strip()+'</title>\n'

			if not line.find('【译文】')==-1:
				is_in_content = True

	out.writelines(articles)
	out.close()


if __name__ == '__main__':
	deal_with_shiji_origin('D:\hanshu.txt','./hanshu_split.txt','','')
	# generate_trans_pair('E:\MSRA\dataset\\raw\\twenty_four_history\shiji\shiji_origin.txt',\
	# 	'E:\MSRA\dataset\\raw\\twenty_four_history\shiji\shiji_trans.txt',\
	# 	'E:\MSRA\dataset\\raw\\twenty_four_history\shiji\shiji_origin_split.txt',\
	# 	'E:\MSRA\dataset\\raw\\twenty_four_history\shiji\shiji_trans_split.txt')
	#sentence_alignment('E:\MSRA\dataset\\raw\\twenty_four_history\shiji\shiji_origin_split.txt','E:\MSRA\dataset\\raw\\twenty_four_history\shiji\shiji_trans_split.txt')
	#abstract_trans('D:\MSRA\dataset\\raw\\twenty_four_history-v2\\trans\shiji2.txt')
	
	