import pandas as pd
import argparse
from tabulate import tabulate
import json
import ipdb


ndef log_info(df):
    # log out the information
    print('Current status:')
    print(f'Total remained: {len(df)}')
    print(f"# Male: {len(df[df['性别'] == '男生'])}, # Female: {len(df[df['性别'] == '女生'])}")
    return None


def print_short_info(index, df):
    print(tabulate(df.iloc[index, [0, 3, 4, 5, 6, 7, 8, 9, 10, 12]], headers='keys', tablefmt='psql'))
    return None


def make_cand_list(df, scores):
    # make a candidate list, list of list, element is list of index
    cand_list = []
    for i in range(len(df)):
        index1 = df['序号'][i]
        gender = df['性别'][i]
        cand_index = []
        if df['我想匹配'][i] == '不限':
            df_cand = df[df['序号'] != index1]
            if gender == '男生':
                df_cand = df_cand[df_cand['我想匹配'] != '小姐姐']
            elif gender == '女生':
                df_cand = df_cand[df_cand['我想匹配'] != '小哥哥']
            else:
                raise ValueError('!')
        elif df['我想匹配'][i] == '小哥哥':
            df_cand = df[df['序号'] != index1]
            df_cand = df_cand[df_cand['性别'] == '男生']
            if gender == '男生':
                df_cand = df_cand[df_cand['我想匹配'] != '小姐姐']
            elif gender == '女生':
                df_cand = df_cand[df_cand['我想匹配'] != '小哥哥']
            else:
                raise ValueError('!')
        elif df['我想匹配'][i] == '小姐姐':
            df_cand = df[df['序号'] != index1]
            df_cand = df_cand[df_cand['性别'] == '女生']
            if gender == '男生':
                df_cand = df_cand[df_cand['我想匹配'] != '小姐姐']
            elif gender == '女生':
                df_cand = df_cand[df_cand['我想匹配'] != '小哥哥']
            else:
                raise ValueError('!')
        else:
            raise ValueError('!')
        for index2 in list(df_cand['序号']):
            cand_index.append((index2, scores[index1][index2]))
        cand_index.sort(key=lambda x: x[1], reverse=True)
        cand_list.append(cand_index)
    return cand_list


def print_first(df, scores):
    # calcaulate the possible pairs and reccomend 
    # the ones refered
    # the ones with less candidates first
    cand_list = make_cand_list(df, scores)
    cand_num_list = [(i, len(cand_list[i])) for i in range(len(cand_list))]
    cand_num_list.sort(key=lambda x: x[1])
    index = []
    for i in range(5):
        index.append(cand_num_list[i][0])
    print_short_info(index, df)
    return cand_list


def rec_candidate(df, cand_list, times):
    # Give 5 condidate information for the query
    try:
        index = list(range(times*5, times*5+5))
        index = [cand_list[i][0] for i in index]
    except:
        index = list(range(times*5, len(cand_list)))
        index = [cand_list[i][0] for i in index]
    print_short_info(index, df)
    return None


def cross_out(index, df_clean):
    # Cross out the paried candidates
    df_clean = df_clean[df_clean['序号'] != index]
    df_clean.reset_index(drop=True, inplace=True)
    return df_clean


# def log_personal_information(index, df, output_file):
#     # log out the personal information
#     df_temp = df.iloc[list(index), :].T
#     print(tabulate(df_temp, headers='keys', tablefmt='psql'), file=output_file)
#     return None

def log_personal_information(i, index, df, output_file):
    # log out the personal information
    df_temp = df.iloc[list(index), :]
    df_temp.reset_index(inplace=True, drop=True)
    print(f"{i:>5} {df_temp['姓名'][0]:>20}: {df_temp['本人微信号'][0]:>20} {df_temp['姓名'][1]:>20}: {df_temp['本人微信号'][1]:>20}", 
            file=output_file)
    return None


if __name__ == "__main__":
    
    # Parser arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-io', '--input_original', help='The original excel file containing the data')
    parser.add_argument('-ic', '--input_clean', help='The clean excel file')
    parser.add_argument('-s', '--score_matrix', default='./score_matrix.json',
            help='The score matrix file')
    parser.add_argument('-o', '--output', default='./output.txt', 
            help='The name of the output file, default is output.txt')
    args = parser.parse_args()

    # Process the data
    df = pd.read_excel(args.input_clean)
    df_orig = pd.read_excel(args.input_original)
    with open(args.score_matrix) as f:
        scores = json.load(f)
    log_info(df)  # Log

    # list inviters and programmer
    inviter = list(df['邀请人'])
    priority = []
    priority.append(44)
    for name in set(inviter):
        if name in list(df['姓名']):
            df_temp = df[df['姓名'] == name]
            priority.append(df_temp['序号'].values[0])
    
    # Start to pair
    pairs = []
    while True:
        # Give candidates
        cand_list = print_first(df, scores)
        if len(priority) != 0:
            print('The inviters or programmers are still remained single! Their index/indices:')
            print(priority)

        while True:
            try:
                index1 = int(input('Please input the index of query candidate:'))
            except:
                if index2 == 'save':
                    df.to_excel('./temp.xlsx')
                    with open(args.output, 'wt') as f:
                        for i in range(len(pairs)):
                            log_personal_information(i, pairs[i], df_orig, f)
                    print('Have saved the current state. To exit, press ctrl+c')
                    break

            if index1 in list(df['序号']):
                break
            else:
                print('This candidate has been crossed out or does not exit, please select another one.')

        # Give recommendations
        i = 0
        while True:
            print_short_info([index1], df_orig)
            df_temp = df[df['序号'] == index1]
            index_temp = df_temp.index[0]
            rec_candidate(df_orig, cand_list[index_temp], i)
            index2 = input('Please select the pair for the candidate, press ENTER to view next, press q to go back, and type "save" to save temperary file:')
            try:
                index2 = int(index2)
                if index2 in list(df['序号']):
                    break
                else:
                    print('This candidate has been crossed out or does not exit, please select another one.')
            except:
                if index2 == '':

                    if i < int(len(cand_list[index1]) / 5):
                        i += 1
                    else:
                        print('This is the last page')
                elif index2 == 'q':
                    i -= 1
                elif index2 == 'save':
                    df.to_excel('./temp.xlsx')
                    with open(args.output, 'wt') as f:
                        for i in range(len(pairs)):
                            log_personal_information(i, pairs[i], df_orig, f)
                    print('Have saved the current state. To exit, press ctrl+c')
                else:
                    print('Sorry, cannot recognize this input.')

        # Cross out and update  # Log
        df = cross_out(index2, df)
        df = cross_out(index1, df)
        if index1 in priority:
            priority.remove(index1)
        if index2 in priority:
            priority.remove(index2)
        log_info(df)  # Log
        pairs.append((index1, index2))

        # Finish?
        if (len(df[df['性别'] == '男生']) == 0) or (len(df[df['性别'] == '女生']) == 0):
            break
        
    # Write the result
    with open(args.output, 'wt') as f:
        for i in range(len(pairs)):
            log_personal_information(i, pairs[i], df_orig, f)

