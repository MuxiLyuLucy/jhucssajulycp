import numpy as np

def Gale_Shapley(raw_score):
    """
        Gale_Shapley stable match pairs algorithm

        :param name: raw_score (Two Dimensional Score Matrix)
        :return: returns pairs (List of Paired Tuple)
    """
    score_matrix = np.array(raw_score)
    pair = []
    matched_couple_number = -1
    while matched_couple_number!= len(pair):
        matched_couple_number = len(pair)
        prefer_cp_list = []
        for i, score_list in enumerate(score_matrix):
            prefer = np.argsort(score_list)
            prefer_cp = prefer[-1] if prefer[-1] != i else prefer[-2]
            if score_list[prefer_cp] == -2:
                prefer_cp = -1
            prefer_cp_list.append(prefer_cp)
        for proposer, proposed in enumerate(prefer_cp_list):
            if proposed == -1:
                continue
            offers = np.where(proposed == prefer_cp_list)
            if len(offers[0]) == 1:
                exist = check_exist(proposer, proposed, pair)
                if not exist and proposer != proposed:
                    pair.append((proposer, proposed))
                    score_matrix[:,proposed] = -2
                    score_matrix[:,proposer] = -2
                    score_matrix[proposed,:] = -2
                    score_matrix[proposer,:] = -2
            else:
                score_to_beat = -1
                choice = -1
                for offer in list(offers[0]):
                    new_score = max(score_matrix[offer][proposed], score_to_beat)
                    if new_score != score_to_beat:
                        score_to_beat = new_score
                        choice = offer
                if choice!= -1:
                    exist = check_exist(proposer, proposed, pair)
                    if not exist and proposer != proposed:
                        pair.append((choice, proposed))
                        score_matrix[:,proposed] = -2
                        score_matrix[:,choice] = -2
                        score_matrix[proposed,:] = -2
                        score_matrix[choice,:] = -2
    return pair

def check_exist(proposer, proposed, pair):
    for x, y in pair:
        if x == proposed or y == proposed or x == proposer or y == proposer:
            return True
    return False


# score_matrix = [[3, 2, 1], [2, 3, 1], [1, 2, 3]]
# print(Gale_Shapley(score_matrix))

