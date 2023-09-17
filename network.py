import numpy as np
from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

from utils import no_of_groups, no_of_real_groups, evidence_seq, country_sequence, \
    no_test_correctness_group, no_of_countries, visualise_tree

from conditional_probabilities import get_parent_cdf, \
    derive_cpd, get_evidence_node_cpd, get_country_priors, cheap_test_prob, test_correctness_prob

evidence_key = 'Evidence_'
country_node = "Country"

test_correctness_key = 'Test_Correctness_'
cheap_test_key = 'Cheap_Test_'


def get_evidence(data):
    evidence = {}
    for item in data["test-results"]:
        if item['type'] == "bloodtype-test":
            evidence[evidence_key + item['person']] = evidence_seq[item['result']]
        else:
            evidence[cheap_test_key + item['person']] = evidence_seq[item['result']]

    country = data['country'] if 'country' in data.keys() else None

    if country is not None:
        evidence[country_node] = country_sequence[country]

    return evidence


def get_queries(data):
    queries = []
    for item in data["queries"]:
        queries.append([evidence_key + item['person']])
    return queries


def get_parents(parents):
    arr = []
    for parent in parents:
        arr.append(parent['name'])
    return arr


def get_inference_obj(probabilities, query):
    obj = {
        "type": "bloodtype",
        "person": query[0].replace(evidence_key, ''),
        "distribution": {
            "O": probabilities.values[0],
            "A": probabilities.values[1],
            "B": probabilities.values[2],
            "AB": probabilities.values[3]
        }
    }
    return obj


def build_network(tree, data):
    edges = []
    nodes = []
    for item in tree.values():
        nodes.append(item['name'])
        for child in item['children']:
            edges.append([item['name'], child['name']])

    country = data['country'] if 'country' in data.keys() else 'North Wumponia'
    parent_cdf = get_parent_cdf()

    # model = BayesianNetwork(edges)
    model = BayesianNetwork()
    model.add_nodes_from(nodes)

    for edge in edges:
        model.add_edge(edge[0], edge[1])

    # single_cpd = derive_single_parent_cdf(country)
    multi_cpd = derive_cpd()
    country_priors = get_country_priors()

    cpds = []

    country_nodes = []

    country_cpd = TabularCPD(country_node, 2, country_priors)
    cpds.append(country_cpd)

    for node in nodes:
        parents = tree[node]['parents']
        if len(parents) == 0:

            model.add_edge(country_node, node)
            cpd = TabularCPD(node, no_of_groups, parent_cdf, evidence=[country_node], evidence_card=np.repeat(2, 1))
        else:

            probs = multi_cpd
            evidence = get_parents(parents)
            cpd = TabularCPD(node, no_of_groups, probs, evidence=evidence,
                             evidence_card=np.repeat(no_of_groups, len(evidence)))
        cpds.append(cpd)

    # Add Evidence Nodes
    for node in nodes:
        if node.startswith('Parent'):
            continue
        evidence_node = 'Evidence_' + node
        model.add_edge(node, evidence_node)
        prob = get_evidence_node_cpd()
        cpd = TabularCPD(evidence_node, no_of_real_groups, prob, evidence=[node],
                         evidence_card=np.repeat(no_of_groups, 1))
        cpds.append(cpd)

        # For cheap test
        evidence_Test_correctness = test_correctness_key + node
        evidence_Cheap_Test = cheap_test_key + node

        model.add_edge(evidence_node, evidence_Test_correctness)
        prob = test_correctness_prob()
        cpd = TabularCPD(evidence_Test_correctness, no_test_correctness_group, prob, evidence=[evidence_node],
                         evidence_card=np.repeat(no_of_real_groups, 1))
        cpds.append(cpd)

        model.add_edge(evidence_Test_correctness, evidence_Cheap_Test)
        model.add_edge(country_node, evidence_Cheap_Test)
        prob2 = cheap_test_prob()
        cpd = TabularCPD(evidence_Cheap_Test, no_of_real_groups, prob2,
                         evidence=[country_node, evidence_Test_correctness],
                         evidence_card=(no_of_countries, no_test_correctness_group))
        cpds.append(cpd)

    for tabular_cpd in cpds:
        model.add_cpds(tabular_cpd)

    # print(edges)

    # visualise_tree(model)
    infer = VariableElimination(model)
    evidence = get_evidence(data)
    queries = get_queries(data)

    distributions = []
    for query in queries:
        if query[0] in evidence.keys():
            # If evidence and query same - skip
            print('Skipped')
            continue
        probabilities = infer.query(query, evidence=evidence)
        distributionObj = get_inference_obj(probabilities, query)
        distributions.append(distributionObj)
    return distributions
