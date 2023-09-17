import networkx as nx
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('TkAgg')


def add_element(arr, person, owner):
    if owner['name'] == person['name']:
        return arr
    found = False
    for index, obj in enumerate(arr):
        if obj['name'] == person['name']:
            found = True
            arr[index] = person
    if not found:
        arr.append(person)
    return arr


def construct_tree(item):
    # print(item)
    obj = {}
    tree = item['family-tree']

    parent_relations = [d for d in tree if d['relation'] in ['mother-of', 'father-of']]
    sibling_relation = [d for d in tree if d['relation'] in ['brother-of', 'sister-of']]

    for rel in parent_relations:
        subject = rel['subject']
        other = rel['object']
        person1 = obj[subject] if subject in obj else {'name': subject, 'children': [], 'parents': [], 'siblings': []}
        person2 = obj[other] if other in obj else {'name': other, 'children': [], 'parents': [], 'siblings': []}

        # Add to children of person 1
        person1['children'] = add_element(person1['children'], person2, person1)

        # Add to parent of person 2
        person2['parents'] = add_element(person2['parents'], person1, person2)

        obj[subject] = person1
        obj[other] = person2

    for rel in sibling_relation:
        subject = rel['subject']
        other = rel['object']
        person1 = obj[subject] if subject in obj else {'name': subject, 'children': [], 'parents': [], 'siblings': []}
        person2 = obj[other] if other in obj else {'name': other, 'children': [], 'parents': [], 'siblings': []}

        # Connect if parents:
        for parent_1 in person1['parents']:
            parent_1['children'] = add_element(parent_1['children'], person2, parent_1)
            person2['parents'] = add_element(person2['parents'], parent_1, person2)
            for sibling in person2['siblings']:
                parent_1['children'] = add_element(parent_1['children'], sibling, parent_1)
                sibling['parents'] = add_element(sibling['parents'], parent_1, sibling)

        # Connect if parents:
        for parent_2 in person2['parents']:
            parent_2['children'] = add_element(parent_2['children'], person1, parent_2)
            person1['parents'] = add_element(person1['parents'], parent_2, person1)
            for sibling in person1['siblings']:
                parent_2['children'] = add_element(parent_2['children'], sibling, parent_2)
                sibling['parents'] = add_element(sibling['parents'], parent_2, sibling)

        # Establish Connection with their siblings
        for sibling in person2['siblings']:
            sibling['siblings'] = add_element(sibling['siblings'], person1, sibling)

            for next_sibling in person1['siblings']:
                sibling['siblings'] = add_element(sibling['siblings'], next_sibling, sibling)

                next_sibling['siblings'] = add_element(next_sibling['siblings'], sibling, next_sibling)
            person1['siblings'] = add_element(person1['siblings'], sibling, person1)

        for sibling in person1['siblings']:
            sibling['siblings'] = add_element(sibling['siblings'], person2, sibling)
            person2['siblings'] = add_element(person2['siblings'], sibling, person2)

        # establish direct connection between them
        person2['siblings'] = add_element(person2['siblings'], person1, person2)
        person1['siblings'] = add_element(person1['siblings'], person2, person1)

        obj[subject] = person1
        obj[other] = person2

        # Add a common parent to people with siblings and no parent

    # Add fake thing
    obj_keys = list(obj.keys())
    for key in obj_keys:
        person = obj[key]
        if len(person['parents']) == 0 and len(person['siblings']) > 0:
            fake_parent_name = 'Parent_' + key
            fake_parent = obj[fake_parent_name] if fake_parent_name in obj else {'name': fake_parent_name,
                                                                                 'children': [person],
                                                                                 'parents': [],
                                                                                 'siblings': []}
            fake_parent_name_two = 'Parent2_' + key
            fake_parent_two = obj[fake_parent_name_two] if fake_parent_name_two in obj else {
                'name': fake_parent_name_two,
                'children': [person],
                'parents': [],
                'siblings': []}
            person['parents'] = [fake_parent, fake_parent_two]
            for sibling in person['siblings']:
                sibling['parents'] = add_element(sibling['parents'], fake_parent, sibling)
                sibling['parents'] = add_element(sibling['parents'], fake_parent_two, sibling)

                fake_parent['children'] = add_element(fake_parent['children'], sibling, fake_parent)
                fake_parent_two['children'] = add_element(fake_parent_two['children'], sibling, fake_parent_two)

            obj[fake_parent_name] = fake_parent
            obj[fake_parent_name_two] = fake_parent_two

    # Add fake thing again
    for key in obj_keys:
        person = obj[key]
        if len(person['parents']) == 1:
            fake_parent_name = 'Parent1_' + key
            fake_parent = obj[fake_parent_name] if fake_parent_name in obj else {'name': fake_parent_name,
                                                                                 'children': [person],
                                                                                 'parents': [],
                                                                                 'siblings': []}
            person['parents'] = add_element(person['parents'], fake_parent, person)
            for sibling in person['siblings']:
                sibling['parents'] = add_element(sibling['parents'], fake_parent, sibling)
                fake_parent['children'] = add_element(fake_parent['children'], sibling, fake_parent)

            obj[fake_parent_name] = fake_parent
    return obj


country_priors = {
    'North Wumponia': {
        'A': 0.25,
        'B': 0.1,
        'O': .65
    },
    'East Wumponia': {
        'A': 0.35,
        'B': 0.05,
        'O': 0.60
    }
}

groups = ['OO', 'AO', 'AA', 'BO', 'BB', 'AB']

evidence_seq = {
    'O': 0,
    'A': 1,
    'B': 2,
    'AB': 3
}

country_sequence = {
    'North Wumponia': 0,
    'East Wumponia': 1
}

countries_list = ['North Wumponia', 'East Wumponia']

sequence = {
    'OO': 0,
    'AO': 1,
    'OA': 1,
    'AA': 2,
    'BO': 3,
    'OB': 3,
    'BB': 4,
    'AB': 5,
    'BA': 5,
}

combinations_map = {
    'A': ['AO', 'AA'],
    'B': ['BO', 'BB'],
    'O': ['OO'],
    'AB': ['AB']

}

test_correct_seq = {
    'O_T': 0, 'A_T': 1, 'B_T': 2, 'AB_T': 3, 'F': 4
}

evidence_groups = ['O', 'A', 'B', 'AB']

test_group = ['O_T', 'A_T', 'B_T', 'AB_T', 'F']

no_of_groups = 6

no_of_real_groups = 4

no_test_correctness_group = 5

no_of_countries = 2


def visualise_tree(model):
    graph = nx.DiGraph(model.edges())

    # Plot the graph
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, node_color='lightblue', node_size=800, arrowsize=15)
    labels = nx.get_edge_attributes(graph, 'weight')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)

    # Show the plot
    plt.show()
