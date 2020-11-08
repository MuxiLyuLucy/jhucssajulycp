from tabulate import tabulate
from gs import Gale_Shapley
import argparse, json 
import pandas as pd 
import numpy as np

name = '姓名/昵称'
gdr = '性别'
g_pref = '意向CP性别'
short_info_headers = [0,1,2,3,4,5,6,7,8,9]

def print_short_info(idxes, df):
    print(tabulate(df.iloc[idxes, short_info_headers], headers='keys', tablefmt='psql'))

def priority_pairing(df, scores):
    normal_cand_idxes = list(df[df['是否优先'] == 0].index)
    print('共{}个需要优先匹配的对象'.format(len(normal_cand_idxes)))
    # Only subjects with priority can propose in the GS algorithm
    p_scores = np.array(scores)
    p_scores[normal_cand_idxes] = -2 * np.ones(p_scores[normal_cand_idxes].shape)
    p_pairs = Gale_Shapley(p_scores)
    # Cross out already paired subjects
    paired_idxes = np.array(p_pairs).flatten()
    scores[paired_idxes, :] = -2
    scores[:, paired_idxes] = -2
    return p_pairs

def normal_pairing(scores):
    n_pairs = Gale_Shapley(scores)
    # Cross out already paired subjects
    paired_idxes = np.array(n_pairs).flatten()
    scores[paired_idxes, :] = -2
    scores[:, paired_idxes] = -2
    return n_pairs

def manual_pairing(args, df, scores, unpaired_idxes, pairs):
    print('手动匹配:')
    while len(unpaired_idxes) > 0:
        # Find candidates for every unpaird subject
        candidates_list = get_candidates(unpaired_idxes, df)

        # Check if there's possibe couples left
        cand_sum = 0
        for _, candidates in candidates_list.items():
            cand_sum += len(candidates)
        if cand_sum == 0:
            print('无剩余可匹配cp')
            return

        # Get first subject
        idx1 = input_idx('请输入第一个匹配对象序号, 输入q停止手动匹配: ','已停止手动匹配', 
            lambda i : len(candidates_list[i]) != 0 and i in unpaired_idxes, 'q')
        if idx1 < 0:
            return
        
        # Get second subject
        print('已选对象(第一行)及其可匹配对象:')
        candidates = candidates_list[idx1]
        print_short_info([idx1] + candidates, df)
        idx2 = input_idx('请输入第二个匹配对象序号, 输入q停止手动匹配: ','已停止手动匹配', lambda i : i in candidates, 'q')
        if idx2 < 0:
            return

        # Update result and the unpaired subjects
        pairs += [(idx1, idx2)]
        unpaired_idxes.remove(idx1)
        unpaired_idxes.remove(idx2)        

        # Save result
        while True:
            user_input = input('是否保存结果？y/n: ')
            if user_input == 'y':
                save_result(args.output, pairs, df)
                break
            elif user_input == 'n':
                break

def get_candidates(unpaired_idxes, df):
    # Gender and gender preference must match
    candidates_list = {}
    for idx1 in unpaired_idxes:
        candiates = []
        for idx2 in unpaired_idxes:
            if idx1 == idx2:
                continue
            p1, p2 = df.iloc[idx1], df.iloc[idx2]
            if((p1[g_pref]=='不限' or p1[g_pref]==p2[gdr]) and (p2[g_pref]=='不限' or p2[g_pref]==p1[gdr])):
                candiates.append(idx2)
        candidates_list[idx1] = candiates
    # Pring information
    candidates_info = []
    for idx, candidates in candidates_list.items():
        candidates_info.append([idx,df.loc[idx, name], len(candidates)])
    print('剩余可选择的未匹配对象:')
    print(tabulate(candidates_info, headers = ['', name, '可匹配对象个数']))

    return candidates_list

def input_idx(prompt_msg, stop_msg, validity_check, stop_signal = None):
    while True:
        user_input = input(prompt_msg)
        if(user_input == stop_signal):
            print(stop_msg)
            # return an invalud idx when input is stop signal
            return -1
        try: 
            i = int(user_input)
        except ValueError:
            print('无效输入！')
            continue
        if validity_check(i):
            return i 
        print("无效序号!")  
            
def save_result(output_file, pairs, df):
    with open(output_file, 'w', encoding='utf-8') as f:
        for p in pairs:
            f.write(df.loc[p[0], name] + ' ' + df.loc[p[1], name] + '\n')
    print('已保存配对结果于{}'.format(output_file))

def main():
    # Parser arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-ic', '--input_clean', default='./data.xlsx', help='The    clean excel file')
    parser.add_argument('-s', '--score_matrix', default='./score_matrix.json',
            help='The score matrix file')
    parser.add_argument('-o', '--output', default='./output.txt', 
            help='The name of the output file, default is output.txt')
    args = parser.parse_args()

    # Process the data
    df = pd.read_excel(args.input_clean)
    with open(args.score_matrix) as f:
        scores = np.array(json.load(f))
    pairs = []

    # Priority pairs
    pairs += priority_pairing(df, scores)
    print('优先匹配cp共{}对'.format(len(pairs)))
    # Normal pairs
    pairs += normal_pairing(scores)
    print('自动匹配cp共{}对'.format(len(pairs)))
    save_result(args.output, pairs, df)
    # Manual pairing
    unpaired_idxes = set(np.arange(len(scores))) - set(np.array(pairs).flatten())
    manual_pairing(args, df, scores, unpaired_idxes, pairs)
               
    save_result(args.output, pairs, df) 
    print('剩余未匹配对象:')
    print_short_info(list(unpaired_idxes), df)
            
if __name__ == "__main__":
    main()