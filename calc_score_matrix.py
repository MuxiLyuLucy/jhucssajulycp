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

    if df1['意向CP性别'] != df2['性别'] and df1['意向CP性别'] != '不限':
        return -2

    if df1['希望CP和自己同城吗？'] == "同城":
        if df1['所在城市'] == df2['所在城市']:
            score += 10
    else:
        score += undecided_score
        
    entertainment_1 = df1['娱乐偏好'].split('，')
    entertainment_2 = df2['娱乐偏好'].split('，')

    same_entertainment = list(set(entertainment_1).intersection(entertainment_2))
    score += len(same_entertainment) * undecided_score

    music_1 = df1['音乐偏好'].split('，')
    music_2 = df2['音乐偏好'].split('，')

    same_music = list(set(music_1).intersection(music_2))
    score += len(same_music) * undecided_score

    cat_dog_1 = df1['猫or狗']
    cat_dog_2 = df2['猫or狗']

    if cat_dog_1 == cat_dog_2:
        score += undecided_score
    else:
        if cat_dog_1 == "都好可爱" or (cat_dog_2 == "都好可爱"):
            score += undecided_score

    personality_1 = df1['你的性格'].split('，')
    personality_2 = df1['希望CP的性格是？'].split('，')
    same_personality = list(set(personality_1).intersection(personality_2))
    score += len(same_personality) * undecided_score

    def handle_time(time):
        if time[:1] == '3':
            return 0
        elif time[:1] == '0':
            return 1
        elif time[:1] == '1':
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

    if df1['希望CP与自己同校吗'] == "同校":
        if df1['学校'] == df2['学校']:
            score += 10
        else:
            return -2
    elif df1['希望CP与自己同校吗'] == "不同校":
        if df1['学校'] != df2['学校']:
            score += 10
        else:
            return -2
    else:
        score += undecided_score

    age = int(df2['年龄'])
    age_choice = df1['理想CP年龄'].split('，')

    matched = False
    for choice in age_choice:
        if choice[:2] == '17':
            if 17 <= age <= 20:
                matched = True
                break
        elif choice[:2] == '21':   
            if 21 <= age <= 23:
                matched = True
                break
        elif choice[:2] == '24':
            if 24 <= age <= 26: 
                matched = True
                break
        elif choice[:2] == '26':   
            if 26 <= age <= 28:
                matched = True
                break
        elif choice[:2] == '28':   
            if age >= 28:
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
parser.add_argument('-i', '--input_clean',default='./data.xlsx', help='The clean excel file')
parser.add_argument('-o', '--output', default='./score_matrix.json', 
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
