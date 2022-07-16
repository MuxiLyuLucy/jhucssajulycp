import pandas as pd
import argparse
import json
from tqdm import tqdm
from tabulate import tabulate

def score(index1, index2, df):
    df1 = df.iloc[index1]
    df2 = df.iloc[index2]
    score = 0
    undecided_score = 1

    if df1['意向CP性别'] != df2['性别'] and df1['意向CP性别'] != '男┋女':
        return -2

    # if df1['希望CP和自己同城吗？'] == "同城":
    #     if df1['所在城市'] == df2['所在城市']:
    #         score += 10
    # else:
    #     score += undecided_score

    if df1['您参加本活动的主要目的？'] != df2['您参加本活动的主要目的？']:
        return -2

    if df1['希望CP与自己同校吗'] == "同校":
        if df1['学校'] == df2['学校']:
            score += 10
        else:
            return -2
    elif df1['希望CP与自己同校吗'] == "异校":
        if df1['学校'] != df2['学校']:
            score += 10
        else:
            return -2
    else:
        score += undecided_score

        
    entertainment_1 = df1['娱乐偏好'].split('┋')
    entertainment_2 = df2['娱乐偏好'].split('┋')

    same_entertainment = list(set(entertainment_1).intersection(entertainment_2))
    score += len(same_entertainment) * undecided_score

    music_1 = df1['音乐偏好'].split('┋')
    music_2 = df2['音乐偏好'].split('┋')

    same_music = list(set(music_1).intersection(music_2))
    score += len(same_music) * undecided_score

    cat_dog_1 = df1['猫or狗']
    cat_dog_2 = df2['猫or狗']

    if cat_dog_1 == cat_dog_2:
        score += undecided_score
    else:
        if cat_dog_1 == "都喜欢" or (cat_dog_2 == "都喜欢"):
            score += undecided_score

    personality_1 = df1['你的性格'].split('┋')
    personality_2 = df1['希望CP的性格是？'].split('┋')
    same_personality = list(set(personality_1).intersection(personality_2))
    score += len(same_personality) * undecided_score

    rational_1 = df1['您认为自己是感性还是理性的？'].split('┋')
    rational_2 = df1['您希望TA是感性还是理性的？'].split('┋')
    same_rational = list(set(rational_1).intersection(rational_2))
    score += len(same_rational) * undecided_score

    def handle_time(time):
        if time == "半小时左右":
            return 0
        elif time == "半小时至一小时":
            return 1
        elif time == "一小时至两小时":
            return 2
        else:
            return 3

    time1 = handle_time(df1['计划每天投入多少时间在与CP互动上？'])
    time2 = handle_time(df2['计划每天投入多少时间在与CP互动上？'])

    score += (3 - abs(time1 - time2)) * undecided_score
    score += undecided_score

    if df1['希望CP和自己专业相似吗？'] == "希望":
        if df1['专业方向'] == df2['专业方向']:
            score += 10
        else:
            score -= undecided_score
    elif df1['希望CP和自己专业相似吗？'] == "不希望":
        if df1['专业方向'] != df2['专业方向']:
            score += 10
        else:
            score -= undecided_score
    else:
        score += undecided_score

    if df1['你希望对方的Myers-Briggs性格类型与自己相同吗？'] == "希望":
        if df1['你的Myers-Briggs性格类型'] != "(空)" and df2['你的Myers-Briggs性格类型'] != "(空)":
            if df1['你的Myers-Briggs性格类型'] == df2['你的Myers-Briggs性格类型']:
                score += 10
            else:
                score -= undecided_score
    elif df1['你希望对方的Myers-Briggs性格类型与自己相同吗？'] == "不希望":
        if df1['你的Myers-Briggs性格类型'] != "(空)" and df2['你的Myers-Briggs性格类型'] != "(空)":
            if df1['你的Myers-Briggs性格类型'] != df2['你的Myers-Briggs性格类型'] and df1['你的Myers-Briggs性格类型'] != "(空)" and df2['你的Myers-Briggs性格类型'] != "(空)":
                score += 10
            else:
                score -= undecided_score

    age = int(df2['年龄'][:2])
    age_choice = df1['理想CP年龄'].split('┋')

    matched = False
    for choice in age_choice:
        if choice[:2] == '18':
            if 18 <= age <= 19:
                matched = True
                break
        elif choice[:2] == '20':
            if 20 <= age <= 22:
                matched = True
                break
        elif choice[:2] == '23':
            if 23 <= age <= 25:
                matched = True
                break
        elif choice[:2] == '26':   
            if 26 <= age <= 28:
                matched = True
                break
        elif choice[:2] == '29':
            if 29 <= age <= 31:
                matched = True
                break
        elif choice[:2] == '32':
            if age >= 32:
                matched = True
                break
        else:
            matched = True
            break
    if matched:
        score += undecided_score
    else:
        return -2
    return score

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input_clean',default='../data/CP.xlsx', help='The clean excel file')
parser.add_argument('-o', '--output', default='../data/score_matrix.json', 
        help='The name of the output file, default is score_matrix.json')
args = parser.parse_args()
df = pd.read_excel(args.input_clean)
scores = []
for i in tqdm(range(len(df))):
    score_ind = []
    for j in range(len(df)):
        score1 = score(i, j, df)
        score2 = score(j, i, df)
        diff_penalty = 0.1
        final_score = score1 + score2 - abs(score1 - score2) * diff_penalty
        if score1 == -2 or score2 == -2:
            final_score = -2
        score_ind.append(final_score)
    scores.append(score_ind)

with open(args.output, 'w') as f:
    json.dump(scores, f)
