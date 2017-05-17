# -*-coding:utf-8 -*-
import sys
import sentence_sim


def para_search(org_para,trs_para_set):
    org_sentences = org_para.split(u'。')
    org_first_sentence = org_sentences[0]
    #org_last_sentence = org_sentences[len(org_sentences)-1]
    max_index = -1
    max_score = 0
    for index,trs_para in enumerate(trs_para_set):
        trs_sentences = trs_para.split(u'。')
        trs_first_sentence = trs_sentences[0]
        #trs_last_sentence = trs_sentences[len(trs_sentences)-1]
        score = sentence_sim.similarity(org_first_sentence, trs_first_sentence)
        if max_score<score:
            max_score = score
            max_index = index
    if max_score<0.1:
        return -1
    if len(org_para)>len(trs_para_set[max_index]):
        return -1
    return max_index


def para_align(my_org_file,my_trs_file,out_path):
    charset = u'，。,：?、”“—.！!》《'
    org_file = ''
    trs_file = ''
    origin_paras = []
    trans_paras = []

    org_lines = open(my_org_file,'r').readlines()
    trs_lines = open(my_trs_file,'r').readlines()
    origin_paras = map(lambda x:x.decode('utf-8').strip(),org_lines)
    trans_paras = map(lambda x:x.decode('utf-8').strip(),trs_lines)

    new_origin_paras = []
    new_trans_paras=[]

    #去掉空白段落
    i = 0
    while i<len(origin_paras):
        if len(origin_paras[i])==0:
            del origin_paras[i]
            i-=1
        i+=1

    i = 0

    while i<len(trans_paras):
        if len(trans_paras[i])==0:
            del trans_paras[i]
            i-=1
        i+=1

    for i,org_para in enumerate(origin_paras):
        start_index = max(0,i-1000)
        end_index = min(len(trans_paras),i+2000)
        if len(org_para)>0:
            trs_para_set = trans_paras[start_index:end_index]
            index = para_search(org_para,trs_para_set)
            if not index==-1:
                new_origin_paras.append(org_para)
                new_trans_paras.append(trs_para_set[index])

    return new_origin_paras,new_trans_paras

