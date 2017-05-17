# -*-coding:utf-8 -*-
import sys

import para_alignment
import sentence_sim
import sentence_split
import generate_limited_len

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('<usage>:<origin file path> <translation file path> <output path>.')
        exit(0)
    max_length = 20
    org_file = sys.argv[1]
    trs_file = sys.argv[2]
    out_path = sys.argv[3]
    out_org_file = out_path + '\\' + 'origin'+'_'+str(max_length)
    out_trs_file = out_path + '\\' + 'trans'+'_'+str(max_length)

    aligned_ors_paras, aligned_trs_paras = para_alignment.para_align(org_file,trs_file,out_path)
    aligned_ors_sentences,aligned_trs_sentences = sentence_split.sentence_align(aligned_ors_paras,aligned_trs_paras)

    ors_tmp = map(lambda x: x.encode('utf-8') + '\n', aligned_ors_paras)
    trs_tmp= map(lambda x: x.encode('utf-8') + '\n', aligned_trs_paras)
    open('ors_tmp','w').writelines(ors_tmp)
    open('trs_tmp','w').writelines(trs_tmp)



    aligned_ors_max_length_20,aligned_trs_max_length_20 = generate_limited_len.max_length_filter(aligned_ors_sentences,aligned_trs_sentences,max_length)

    aligned_ors_max_length_20 = map(lambda x:x.encode('utf-8')+'\n',aligned_ors_max_length_20)
    aligned_trs_max_length_20 = map(lambda x:x.encode('utf-8')+'\n',aligned_trs_max_length_20)

    open(out_org_file,'w').writelines(aligned_ors_max_length_20)
    open(out_trs_file,'w').writelines(aligned_trs_max_length_20)
