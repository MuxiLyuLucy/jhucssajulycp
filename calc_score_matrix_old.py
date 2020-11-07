import pandas as pd
import argparse
import json
from tqdm import tqdm


def score(index1, index2, df):
    df1 = df[df['序号'] == index1]
    df2 = df[df['序号'] == index2]
    score = 0

    if df1['目前所在城市'].values[0] == df2['目前所在城市'].values[0]:
        score += 10

    if df1['我更倾向'].values[0] == '年龄比我大':
        if df1['年龄'].values[0] <= df2['年龄'].values[0]:
            score += 3
    elif df1['我更倾向'].values[0] == '年龄比我小':
        if df1['年龄'].values[0] >= df2['年龄'].values[0]:
            score += 3
    elif df1['我更倾向'].values[0] == '和我差不多':
        if abs(df1['年龄'].values[0] - df2['年龄'].values[0]) < 2:
            score += 3
        elif abs(df1['年龄'].values[0] - df2['年龄'].values[0]) < 3:
            score += 2
        elif abs(df1['年龄'].values[0] - df2['年龄'].values[0]) < 4:
            score += 1
    elif df1['我更倾向'].values[0] == '不限':
        score += 3
    else:
        raise ValueError('!')

    if df2['我更倾向'].values[0] == '年龄比我大':
        if df2['年龄'].values[0] <= df1['年龄'].values[0]:
            score += 3
    elif df2['我更倾向'].values[0] == '年龄比我小':
        if df2['年龄'].values[0] >= df1['年龄'].values[0]:
            score += 3
    elif df2['我更倾向'].values[0] == '和我差不多':
        if abs(df1['年龄'].values[0] - df2['年龄'].values[0]) < 2:
            score += 3
        elif abs(df1['年龄'].values[0] - df2['年龄'].values[0]) < 3:
            score += 2
        elif abs(df1['年龄'].values[0] - df2['年龄'].values[0]) < 4:
            score += 1
    elif df2['我更倾向'].values[0] == '不限':
        score += 3
    else:
        raise ValueError('!')

    if df1['学院'].values[0] == df2['学院'].values[0]:
        score -= 5

    hobby1 = df1['兴趣爱好'].values[0].split()
    hobby2 = df2['兴趣爱好'].values[0].split()

    score += (len(hobby1 + hobby2) - len(set(hobby1 + hobby2))) * 2

    return score


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_clean', help='The clean excel file')
    parser.add_argument('-o', '--output', default='./score_matrix.json', 
            help='The name of the output file, default is score_matrix.json')
    args = parser.parse_args()

    # Process the data
    df = pd.read_excel(args.input_clean)

    scores = []
    for i in tqdm(range(len(df))):
        scores.append([score(i, j, df) for j in range(len(df))])

    with open(args.output, 'w') as f:
        json.dump(scores, f)

