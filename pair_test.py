import argparse, json, pandas as pd, numpy as np
from gs import Gale_Shapley

def priority_pairing(df, scores):
    normal_cand_idxes = list(df[df['是否优先'] == 0].index)
    p_scores = np.array(scores)
    p_scores[normal_cand_idxes] = -2 * np.ones(p_scores[normal_cand_idxes].shape)
    p_pairs = Gale_Shapley(p_scores)
    paired_idxes = np.array(p_pairs).flatten()
    scores[paired_idxes, :] = -2
    scores[:, paired_idxes] = -2
    return p_pairs

def normal_pairing(scores):
    n_pairs = Gale_Shapley(scores)
    paired_idxes = np.array(n_pairs).flatten()
    scores[paired_idxes, :] = -2
    scores[:, paired_idxes] = -2
    return n_pairs
    
def main():
    # Parser arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-ic', '--input_clean', default='./test.xlsx', help='The    clean excel file')
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
    # Normal pairs
    pairs += normal_pairing(scores)
    
    unpaired_idxes = set(np.arange(len(scores))) - set(np.array(pairs).flatten())

    # Output
    with open(args.output, 'w', encoding='utf-8') as f:
        for p in pairs:
            f.write(df['姓名/昵称'][p[0]] + ' ' + df['姓名/昵称'][p[1]] + '\n')
    
if __name__ == "__main__":
    main()