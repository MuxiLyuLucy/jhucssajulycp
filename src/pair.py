from tabulate import tabulate
from gs import Gale_Shapley
import argparse, json, pickle, os
import pandas as pd 
import numpy as np

name = '姓名/昵称'
gdr = '性别'
g_pref = '意向CP性别'
short_info_headers = [0,6,7,8,9,10,11,12]
unfinished_result = '../data/unfinished.pkl'

def print_short_info(idxes, df):
    print(tabulate(df.iloc[idxes, short_info_headers], headers='keys', tablefmt='psql'))

def priority_pairing(df, scores):
    normal_cand_idxes = list(df[df['是否优先'] == 0].index)
    print(len(scores))
    print(len(normal_cand_idxes))
    print('共{}个需要优先匹配的对象'.format(len(scores) - len(normal_cand_idxes)))
    # Only subjects with priority can propose in the GS algorithm
    p_scores = np.array(scores)
    print(normal_cand_idxes)
    p_scores[normal_cand_idxes] = -2 * np.ones(p_scores[normal_cand_idxes].shape)
    p_pairs = Gale_Shapley(p_scores)
    # Cross out already paired subjects
    paired_idxes = np.array(p_pairs).flatten()

    print(paired_idxes)

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

def manual_pairing(args, df, scores, unpaired_idxes, unpairable_idxes, pairs,):
    print('手动匹配:')
    while len(unpaired_idxes) > 0:
        # Find candidates for every unpaird subject
        candidates_list, new_unpairable_idxes = get_candidates(list(unpaired_idxes), df)
        unpairable_idxes += new_unpairable_idxes
        for idx in new_unpairable_idxes:
            unpaired_idxes.remove(idx)

        # Check if there's possibe couples left
        cand_sum = 0
        for _, candidates in candidates_list.items():
            cand_sum += len(candidates)
        if cand_sum == 0:
            print('无剩余可匹配cp')
            save_status(pairs, unpaired_idxes, unpairable_idxes)
            return

        # Get first subject
        idx1 = input_idx('请输入第一个匹配对象序号, 输入q停止手动匹配: ','已停止手动匹配', 
            lambda i : len(candidates_list[i]) != 0 and i in unpaired_idxes, 'q')
        if idx1 < 0:
            save_status(pairs, unpaired_idxes, unpairable_idxes)
            return
        
        # Get second subject
        print('已选对象(第一行)及其可匹配对象:')
        candidates = candidates_list[idx1]
        print_short_info([idx1] + candidates, df)
        idx2 = input_idx('请输入第二个匹配对象序号, 输入q停止手动匹配: ','已停止手动匹配', lambda i : i in candidates, 'q')
        if idx2 < 0:
            save_status(pairs, unpaired_idxes, unpairable_idxes)
            return

        # Update result and the unpaired subjects
        pairs += [(idx1, idx2)]
        unpaired_idxes.remove(idx1)
        unpaired_idxes.remove(idx2) 
    save_status(pairs, unpaired_idxes, unpairable_idxes) 
    print('已匹配所有可行的CP')      

def get_candidates(unpaired_idxes, df):
    # Gender and gender preference must match
    print('正在计算可匹配对象列表...')
    unpairable = []
    candidates_list = {}
    for idx in unpaired_idxes:
        candidates_list[idx] = []
    
    for i in range(len(unpaired_idxes)):
        idx1 = unpaired_idxes[i]
        for idx2 in unpaired_idxes[i+1:]:
            p1, p2 = df.loc[idx1], df.loc[idx2]
            if((p1[g_pref]=='不限' or p1[g_pref]==p2[gdr]) and (p2[g_pref]=='不限' or p2[g_pref]==p1[gdr])):
                candidates_list[idx1].append(idx2)
                candidates_list[idx2].append(idx1)

    # Pring information
    candidates_info = []
    for idx, candidates in candidates_list.items():
        if len(candidates) > 0:
            candidates_info.append([idx,df.loc[idx, name], len(candidates)])
        else:
            unpairable.append(idx)
    print('剩余可选择的未匹配对象:')
    print(tabulate(candidates_info, headers = ['', name, '可匹配对象个数']))

    return candidates_list, unpairable

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
            
def save_result(output_file, pairs, df, total_unpaired_idxes):
    paired_dfs = []
    for pair in pairs:
        paired = df.loc[list(pair)]
        paired_dfs.append(paired)
        paired_dfs.append(pd.DataFrame([['']*paired.shape[1]], columns=paired.columns))
    paired_dfs = pd.concat(paired_dfs)
    paired_dfs.to_excel(output_file, index =False)
    print('已保存配对结果于{}'.format(output_file))

    # Print unpaired subjects
    if(len(total_unpaired_idxes) > 0): 
        print('剩余未匹配对象:')
        print_short_info(total_unpaired_idxes, df)
        unpaired_df = df.iloc[total_unpaired_idxes]
        unpaired_df.to_excel('../data/unpaired.xlsx', index =False)

def save_status(pairs, unpaired_idxes, unpairable_idxes):
    with open(unfinished_result, 'wb') as f:
        data = {'pairs':pairs, 'unpaired_idxes': unpaired_idxes, 'unpairable_idxes': unpairable_idxes}
        pickle.dump(data, f)

def load_last_time():
    while True:
        user_input = input('继续上次未完成配对？y/n: ')
        if user_input == 'y':
            if os.path.exists(unfinished_result):
                with open(unfinished_result, 'rb') as f:
                    return pickle.load(f)
            else:
                print('没有找到上次配对结果')
            break
        elif user_input == 'n':
            if os.path.exists(unfinished_result):
                os.remove(unfinished_result)
            break

def main():
    # Parser arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-ic', '--input_clean', default='../data/CP.xlsx', help='The clean excel file')
    parser.add_argument('-s', '--score_matrix', default='../data/score_matrix.json',
            help='The score matrix file')
    parser.add_argument('-o', '--output', default='../data/paired.xlsx', 
            help='The name of the output file, default is paired.xlsx')
    args = parser.parse_args()

    # Process the data
    df = pd.read_excel(args.input_clean)
    with open(args.score_matrix) as f:
        scores = np.array(json.load(f))

    # Try to load unfinished result first
    pairs, unpairable_idxes = [], []
    data = load_last_time()
    if data is not None:
        pairs, unpaired_idxes, unpairable_idxes = data['pairs'], data['unpaired_idxes'], data['unpairable_idxes']
    else:    
        # Priority pairs
        pairs += priority_pairing(df, scores)
        print('优先匹配cp共{}对'.format(len(pairs)))
        # Normal pairs
        pairs += normal_pairing(scores)
        unpaired_idxes = set(np.arange(len(scores))) - set(np.array(pairs).flatten())
        print('自动匹配cp共{}对'.format(len(pairs)))
    print('已匹配cp共{}对'.format(len(pairs)))

    # Manual pairing
    manual_pairing(args, df, scores, unpaired_idxes, unpairable_idxes, pairs)
    
    # Save result   
    save_result(args.output, pairs, df, list(unpaired_idxes) + unpairable_idxes)

if __name__ == "__main__":
    main()
