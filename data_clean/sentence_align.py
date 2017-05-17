# -*-coding:utf-8 -*-

charset = u'，。,：?、”“—.！!》《\n'
import sentence_sim
import pdb


# origin_sentence
def find_match_index(origin_sentence, origin_id):
    start = -1
    end = -1

    for j, oc in enumerate(origin_sentence):
        for i in range(len(trans_set)):
            if not new_trans_set[i].find(oc) == -1:
                count_box[i]+=1
    index = find_max_index(origin_id)
    return index



def find_max_index(line_id):
    start_index =max(line_id-1000,0)
    end_index = min(line_id+10,len(trans_set))
    max_index =-1
    max_length = 0

    for i in range(start_index,end_index):
        if max_length<count_box[i]:
            max_length = count_box[i]
            max_index = i
    return max_index
def find_max_range(count_box, line_id):
    max_score = 0
    start = max(3 * line_id - 3, 0)
    end = 5 * line_id + 3
    i = start
    actual_start = -1
    actual_end = -1

    def find_range(count_box, raw_start):
        start_index = raw_start
        while len(count_box[start_index]) == 0:
            start_index += 1

        consecutive_empty_num = 0
        max_char_index = 0
        count = 0
        num = 0
        end_index = start_index + 1
        end_type = -1
        inverse_num = 0
        i = start_index
        while len(count_box[i]) > 0 or consecutive_empty_num < 2:
            if len(count_box[i]) == 0:
                if len(count_box[i - 1]) == 0:
                    consecutive_empty_num += 1
                else:
                    consecutive_empty_num = 1
                if consecutive_empty_num > 1:
                    end_type = 1
                    break
            elif max_char_index > min(count_box[i]):
                inverse_num += 1
                if inverse_num > 1:
                    end_type = 0
                    break
            else:
                max_char_index = max(count_box[i])

            num += len(count_box[i])

            i += 1
            if i == len(count_box):
                break

        if end_type == 1:
            end_index = i - 1
        else:
            if len(count_box[i - 1]) == 0:
                i -= 1
            end_index = i

        return start_index, end_index, num * (end_index - start_index)

    while i < end:
        start_index, end_index, score = find_range(count_box, i)
        if max_score < score:
            max_score = score
            actual_start = start_index
            actual_end = end_index
        i = end_index

    # if line_id == 4:
    # 	print end_index,score
    # 	pdb.set_trace()

    return actual_start, actual_end, max_score


origin_set = open('E:\MSRA\dataset\\raw\\twenty_four_history\shiji\shiji_origin_split.txt', 'r').readlines()
trans_set = open('E:\MSRA\dataset\\raw\\twenty_four_history\shiji\shiji_trans_split.txt', 'r').readlines()
origin_set = map(lambda x: x.decode('utf-8').strip(), origin_set)
trans_set = map(lambda x:x.decode('utf-8').strip() , trans_set)

new_origin_set = map(lambda x:sentence_sim.multiple_replace(x,charset),origin_set)
new_trans_set = map(lambda x:sentence_sim.multiple_replace(x,charset),trans_set)
candidate_dict = []
last_end = 0
end = 0


for i in range(len(trans_set)):
    candidate_dict.append([])
for jj, ors in enumerate(new_origin_set):
    # print jj
    if jj%1000 ==0:
        print jj
    count_box = [0] * len(trans_set)
    index= find_match_index(ors, jj)
    if not index==-1:
        candidate_dict[index].append(jj)

last_index = -2
result = []

new_origin_set = []
new_trans_set = []

for i in range(len(candidate_dict)):
    tmp = ''
    for j in candidate_dict[i]:
        tmp+=origin_set[j].encode('utf-8')
    tmp+='\n'
    if len(tmp)>1:
        new_trans_set.append(trans_set[i].encode('utf-8')+'\n')
        new_origin_set.append(tmp)


fi= open('E:\MSRA\dataset\\raw\\twenty_four_history\shiji\shiji_new_origin_split.txt','w')
fo = open('E:\MSRA\dataset\\raw\\twenty_four_history\shiji\shiji_new_trans_split.txt','w')
fi.writelines(new_origin_set)
fo.writelines(new_trans_set)

