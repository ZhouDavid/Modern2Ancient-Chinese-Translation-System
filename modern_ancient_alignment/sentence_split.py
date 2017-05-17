# -*- coding: utf-8 -*-
import sys
import sentence_sim

reload(sys)
sys.setdefaultencoding('utf8')
charset = u'，。,：?、”“—.！!》《\n'


def naive_split(line):
    '''无脑按照空格分所有词'''
    line = unicode(line)
    ans = []
    for i in range(len(line)):
        ans.append(line[i])
    return ans


def write_split_line(sline, fout):
    line = ''
    for ch in sline:
        line = line + ch + ' '
    line = line.strip()
    fout.write(line + '\n')


def write_sentences(sentences, fout):
    sentences = map(lambda x: x.encode('utf-8') + u'。\n', sentences)
    fout.writelines(sentences)


def split_sentence(sentence):
    sentence = unicode(sentence).strip()
    sentences = []
    sentence = sentence.replace(u'；',u'。')
    sentences = sentence.split(u'。')
    return sentences


def find_match_sentence(origin_sentence, trans_sentences):
    count_box = [0] * len(trans_sentences)
    origin_sentence = sentence_sim.multiple_replace(origin_sentence, charset)
    for j, oc in enumerate(origin_sentence):
        for i in range(len(trans_sentences)):
            tmp_trans = sentence_sim.multiple_replace(trans_sentences[i], charset)
            if not tmp_trans.find(oc) == -1:
                count_box[i] += 1

    max_length = -1
    for i in range(len(trans_sentences)):
        if max_length < count_box[i]:
            max_length = count_box[i]
            index = i

    return index, max_length

def sentence_align(ors_aligned_paras,trs_aligned_paras):
    ors_aligned_sentences = []
    trs_aligned_sentences = []
    if len(ors_aligned_paras) == len(trs_aligned_paras):  # 理论上应该是相等的，因为句子数量是一样的
        length = len(ors_aligned_paras)
        for i in range(length):
            ors_sentences = split_sentence(ors_aligned_paras[i])
            trs_sentences = split_sentence(trs_aligned_paras[i])

            if len(ors_sentences) == len(trs_sentences):  # split出来的数量相等才保留
                j=0
                while j< len(ors_sentences):
                    if len(ors_sentences[j]) == 0:
                        del ors_sentences[j]
                        del trs_sentences[j]
                        j-=1
                    j+=1
                ors_aligned_sentences.extend(ors_sentences)
                trs_aligned_sentences.extend(trs_sentences)
            else:
                if len(ors_aligned_paras[i]) > 50:
                    last_ors = ''
                    last_index = 0
                    for origin_sentence in ors_sentences:
                        if len(origin_sentence) > 3:
                            index, score = find_match_sentence(origin_sentence, trs_sentences)
                            if not last_index == index:
                                if score > 3:
                                    ors_aligned_sentences.append(last_ors)
                                    trs_aligned_sentences.append(trs_sentences[last_index])
                                    last_index = index
                                    last_ors = origin_sentence
                            else:
                                last_ors += origin_sentence+u'。'
                    if len(last_ors) > 3:
                        ors_aligned_sentences.append(last_ors)
                        trs_aligned_sentences.append(trs_sentences[last_index])

                elif len(ors_aligned_paras[i]) > 1:
                    ors_aligned_sentences.append(ors_aligned_paras[i])
                    trs_aligned_sentences.append(trs_aligned_paras[i])

    for i in range(len(ors_aligned_sentences)):
        if not ors_aligned_sentences[i].endswith(u'。') and not ors_aligned_sentences[i].endswith(u'?'):
            ors_aligned_sentences[i]+=u'。'
        if not trs_aligned_sentences[i].endswith(u'。') and not trs_aligned_sentences[i].endswith(u'?'):
            trs_aligned_sentences[i] += u'。'

    return ors_aligned_sentences,trs_aligned_sentences