import itertools
from collections import Counter

from utils import no_of_groups, sequence, groups, country_priors, combinations_map, no_of_real_groups, \
    countries_list, test_correct_seq, test_group, evidence_groups
import numpy as np


def get_child_prob(parent1, parent2):
    combinations = list(itertools.product(parent1, parent2)) + list(itertools.product(parent2, parent1))
    frequency = Counter(combinations)
    total = 0
    li = [0] * no_of_groups
    for combo, freq in frequency.items():
        total = total + freq
        group = combo[0] + combo[1]
        li[sequence[group]] = li[sequence[group]] + freq
    return [number / total for number in li]


def derive_cpd():
    probs = []
    for parent1 in groups:
        for parent2 in groups:
            child_probs = np.array(get_child_prob(parent1, parent2)).reshape(-1, 1)
            probs.append(child_probs)
    probs = np.array(probs)
    combined_array = np.concatenate(tuple(probs), axis=1)
    return combined_array


def get_parents_priors(country='North Wumponia'):
    prior = country_priors[country]
    AA = prior['A'] * prior['A']
    AO = 2 * prior['A'] * prior['O']
    BB = prior['B'] * prior['B']
    BO = 2 * prior['B'] * prior['O']
    AB = 2 * prior['A'] * prior['B']
    OO = prior['O'] * prior['O']
    arr = [OO, AO, AA, BO, BB, AB]
    out = []
    for elt in arr:
        out.append([elt])
    return out


def get_group_prior(country):
    prior = country_priors[country]
    AA = prior['A'] * prior['A']
    AO = 2 * prior['A'] * prior['O']
    BB = prior['B'] * prior['B']
    BO = 2 * prior['B'] * prior['O']
    AB = 2 * prior['A'] * prior['B']
    OO = prior['O'] * prior['O']
    arr = [OO, AO + AA, BO + BB, AB]
    return np.array(arr)


def get_priors(country='North Wumponia'):
    prior = country_priors[country]
    AA = prior['A'] * prior['A']
    AO = 2 * prior['A'] * prior['O']
    BB = prior['B'] * prior['B']
    BO = 2 * prior['B'] * prior['O']
    AB = 2 * prior['A'] * prior['B']
    OO = prior['O'] * prior['O']
    arr = [OO, AO, AA, BO, BB, AB]
    return np.array(arr)


def get_parent_cdf():
    prior_north = get_priors('North Wumponia').reshape(-1, 1)
    prior_east = get_priors('East Wumponia').reshape(-1, 1)
    combined_array = np.concatenate((prior_north, prior_east), axis=1)
    return combined_array


def test_correctness_prob():
    probs = np.diag([0.7] * no_of_real_groups)
    ones = np.ones((1, no_of_real_groups)) * .3
    probs = np.vstack((probs, ones))
    return probs


def cheap_test_prob():
    probs = []
    for country in countries_list:
        for test in test_group[:-1]:
            child_probs = np.zeros(no_of_real_groups)
            child_probs[test_correct_seq[test]] = 1
            probs.append(child_probs.reshape(-1, 1))
        prior = get_group_prior(country).reshape(-1, 1)
        probs.append(prior)
    probs = np.array(probs)
    combined_array = np.concatenate(tuple(probs), axis=1)
    return combined_array


def get_country_priors():
    return [[0.5], [0.5]]


def get_evidence_node_cpd():
    probs = []
    for g1 in groups:
        li = np.zeros(len(evidence_groups))
        for i, g2 in enumerate(evidence_groups):
            if g1 in combinations_map[g2]:
                li[i] = 1
        probs.append(li.reshape(-1, 1))
    probs = np.array(probs)
    combined_array = np.concatenate(tuple(probs), axis=1)
    return combined_array
