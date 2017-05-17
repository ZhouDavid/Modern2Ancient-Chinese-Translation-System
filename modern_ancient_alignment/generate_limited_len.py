# -*-coding:utf-8 -*-
import sentence_sim
charset = u'，。,：?、”“—.！!》《'
def word_len(s):
	s = sentence_sim.multiple_replace(s,charset)
	return len(s)

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



def max_length_filter(aligned_ors_sentences,aligned_trs_sentences,max_length = 50):
	new_or = []
	new_tr = []
	for i in range(len(aligned_ors_sentences)):
		if i%10000 ==0:
			print i
		if word_len(aligned_ors_sentences[i])<=max_length and word_len(aligned_trs_sentences[i])<=max_length:
			new_or.append(aligned_ors_sentences[i])
			new_tr.append(aligned_trs_sentences[i])
		else:
			tmp_ors = aligned_ors_sentences[i].split(u'，')
			tmp_trs = aligned_trs_sentences[i].split(u'，')
			for j,o in enumerate(tmp_ors):
				if word_len(o)<max_length and word_len(o)>3:
					index,score = find_match_sentence(o,tmp_trs)
					if score>3 and word_len(tmp_trs[index])<max_length:
						if j<len(tmp_ors)-1:
							new_or.append(o+u'，')
							new_tr.append(tmp_trs[index]+u'，')
						else:
							new_or.append(o)
							new_tr.append(tmp_trs[index])
	return new_or,new_tr

