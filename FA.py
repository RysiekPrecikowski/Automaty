from typing import Iterable, Any, Set, Dict

import networkx
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt
from pprint import pprint

def get_from_set(my_set, item):
    for i in my_set:
        if i == item:
            return i
    return None


class TransitionFunction:
    Epsilon = r'$\epsilon$'
    Epsilon_closure = r'$\epsilon ^*$'

    def __init__(self, table: Dict[Any, Dict[Any, Set[Any]]], accept_states: set, starting_state):
        self.table = table
        self.accepting_states = accept_states
        self.starting_state = starting_state
        self.alphabet = set()
        self.deterministic = True

        for options in table.values():
            for l in options.keys():
                self.alphabet.add(l)

            for state in options.values():
                if len(state) > 1:
                    self.deterministic = False
        if self.Epsilon in self.alphabet:
            self.deterministic = False

    def check_epsilon(self, state_to_check, state_parent, label):
        def _check(states, depth=1):
            states_to_add = []

            for _, state in states:
                if self.Epsilon not in self.table[state]:
                    continue
                for transition in self.table[state][self.Epsilon]:
                    states_to_add.append((depth, transition))

            if len(states_to_add) != 0:
                return states_to_add + _check(states_to_add, depth + 1)
            else:
                return []

        to_add = _check([(0, state_to_check)])

        res = set()
        for depth, state_to_add in to_add:
            if state_parent is not None:
                new_state = state_parent.add_child(state_to_add,
                                                   str(label) + '+' + str(depth)
                                                   + r'$\cdot$' + TransitionFunction.Epsilon)
            else:
                new_state = FiniteAutomata.State(state_to_add)

            res.add(new_state)

        return res

    def get_epsilon_closure(self, state):
        xd = self.check_epsilon(state, None, None)
        xd.add(state)
        return xd

    def convert_to_deterministic(self, table=None, alphabet=None, starting_states=None, accepting_states=None):
        if table is None:
            table = self.table
        if alphabet is None:
            alphabet = self.alphabet
        if starting_states is None:
            starting_states = self.starting_state
        if accepting_states is None:
            accepting_states = self.accepting_states

        pprint(table)

        res_table = {}
        res_accepting_states = set()

        states = {frozenset([starting_states])}

        starting_states_res = frozenset([starting_states])

        while states:
            current_states = states.pop()
            res_table[current_states] = {}

            if len(accepting_states & current_states) > 0:
                res_accepting_states.add(current_states)

            for l in alphabet - {self.Epsilon, self.Epsilon_closure}:
                new_state = set()
                for state in current_states:
                    transition_to = table[state][l]

                    for to_state in transition_to:
                        new_state.add(to_state)

                        for x in self.get_epsilon_closure(to_state):
                            new_state.add(x)

                        # print(l, to_state, self.get_epsilon_closure(to_state) )

                if frozenset(new_state) not in res_table:
                    states.add(frozenset(new_state))

                res_table[current_states][l] = frozenset(new_state)

        pprint(res_table)
        pprint(res_accepting_states)
        pprint(starting_states_res)

        res = TransitionFunction(res_table, res_accepting_states, starting_states_res)
        res.deterministic = True
        return res

    def __getitem__(self, item):
        return self.table[item]


class FiniteAutomata:
    class Visualizer:
        def __init__(self, accepting=None):
            if accepting is None:
                accepting = set()
            self.roots = []
            self.g = nx.DiGraph()

            self.accepting_states = accepting
            self.accepting_nodes = set()

        def set_root(self, nodes):
            self.roots = list(nodes)

        def show(self, show_edge_labels=False, figsize=(9, 9)):
            q = self.roots
            i = 0

            while q:
                node = q.pop()

                if node.index is None:
                    node.index = i

                    self.g.add_node(node.index, label=node.label)

                    for child in list(node.children)[::-1]:
                        q.append(child)

                    if node.state in self.accepting_states:
                        self.accepting_nodes.add(i)

                    i += 1

                if node.parent is not None:
                    if type(node.parent) is list:
                        for parent, label in zip(node.parent, node.label_to_parent):
                            self.g.add_edge(parent.index, node.index, label=label)
                    else:
                        self.g.add_edge(node.parent.index, node.index, label=node.label_to_parent)


            pos = graphviz_layout(self.g, prog='dot')

            if None in self.g.nodes:
                self.g.remove_node(None)
            node_labels = {u: l['label'] for u, l in self.g.nodes(data=True)}
            edge_labels = {(s, t): l['label'] for s, t, l in self.g.edges(data=True)}

            normal = node_labels.keys() - self.accepting_nodes
            accepting = node_labels.keys() - normal

            plt.figure(figsize=figsize, dpi=150)
            nx.draw_networkx_labels(self.g, pos, {k: node_labels[k] for k in normal}, font_color='black')
            nx.draw_networkx_labels(self.g, pos, {k: node_labels[k] for k in accepting}, font_color='r')
            nx.draw_networkx_edges(self.g, pos, arrows=True)

            if show_edge_labels:
                nx.draw_networkx_edge_labels(self.g, pos, edge_labels)
            # nx.draw(self.g, pos=pos)

            plt.show()

    class State:
        def __init__(self, state):
            self.state = state
            self.children = []
            self.label_to_parent = None
            self.parent = None
            self.index = None
            self.label = state

            if type(state) == frozenset:
                self.label = set(self.state)

        def add_child(self, child_state, label):
            child = FiniteAutomata.State(child_state)
            self.children.append(child)

            child.add_parent(self, label)

            return child

        def add_parent(self, parent, label):
            if type(self.parent) == list:
                self.parent.append(parent)
                self.label_to_parent.append(label)
            elif self.parent is None:
                self.parent = parent
                self.label_to_parent = label
            else:
                self.parent = [self.parent] + [parent]
                self.label_to_parent = [self.label_to_parent] + [label]

        def __repr__(self):
            return str(self.state)

        def __hash__(self):
            return hash(self.state)

        def __eq__(self, other):

            if type(other) == FiniteAutomata.State:
                return self.state == other.state
            else:
                return self.state == other

    def __init__(self, transition_function: TransitionFunction):
        self.transition_function = transition_function
        self.visualizer = self.Visualizer(accepting=transition_function.accepting_states)

    def run(self, word: Iterable):
        start = self.State(self.transition_function.starting_state)

        states = [start]
        print("\nSTART", start)
        states += self.transition_function.check_epsilon(start, None, None)

        self.visualizer.set_root(states)

        for l in word:
            print("STATES", states,"L", l)
            new_states = []
            for state in states:
                # if l not in self.transition_function[state.state]: #TODO chyba można wywalić
                #     continue

                if self.transition_function.deterministic:
                    to = self.transition_function[state.state][l]

                    # taki zapis, bo dla deterministycznego zwykłego set składa sie tylko z jednego stanu
                    # dla deterministycznego, przerobionego z niedeterministycznego frozensety to pojedyncze stany
                    new_state = state.add_child(to, l) \
                        if type(state.state) is frozenset \
                        else state.add_child(*to, l)

                    new_states.append(new_state)
                else:
                    for to in self.transition_function[state.state][l]:
                        new_state = state.add_child(to, l)

                        new_states.append(new_state)

                        new_states += self.transition_function.check_epsilon(new_state, state, l)

            states = new_states
        print("STATES", states)
        accepted = True if len(set(states) & self.transition_function.accepting_states) > 0 else False

        print(accepted)

    def run_set(self, word):
        """
        ONLY NON DETERMINISTIC (without states-sets)
        """
        start = self.State(self.transition_function.starting_state)
        if type(start.state) is frozenset:
            raise Exception("STATES-SETS NOT SUPPORTED, use ordinary run method")

        states = {start}
        states |= self.transition_function.check_epsilon(start, None, None)

        self.visualizer.set_root(states)

        for l in word:
            print(states, l)
            new_states = set()
            for state in states:
                # if l not in self.transition_function[state.state]: #TODO chyba można wywalić
                #     continue

                for to in self.transition_function[state.state][l]:
                    new_state = state.add_child(to, l)

                    if new_state in new_states:
                        old_node = get_from_set(new_states, new_state)
                        old_node.parent.children.remove(old_node)
                        node_parent = old_node.parent
                        node_parent.children.append(new_state)
                        new_state.add_parent(node_parent, l)

                        new_states.remove(new_state)
                        # parent_state.children.append(new_state)
                    # else:
                    new_states.add(new_state)

                    new_states |= self.transition_function.check_epsilon(new_state, state, l)

            states = new_states

        accepted = True if len(set(states) & self.transition_function.accepting_states) > 0 else False

        print(accepted)


def main():
    xd = {
        1: {'0': {1}, '1': {1, 2}},
        2: {'0': {3}, '1': {3}},
        3: {'0': {4}, '1': {4}},
        4: {'0': {}, '1': {}},
    }
    func = TransitionFunction(xd, {4}, 1)
    func_converted = func.convert_to_deterministic()

    automata = FiniteAutomata(func)
    automata = FiniteAutomata(func_converted)
    #
    # automata.run('110100')
    #
    automata.run('111000')
    automata.visualizer.show(show_edge_labels=False)

def test_enas():
    xd = {
        1: {'0': {1}, '1': {1, 2}, TransitionFunction.Epsilon: {}},
        2: {'0': {3}, '1': {}, TransitionFunction.Epsilon: {3}},
        3: {'0': {}, '1': {4}, TransitionFunction.Epsilon: {}},
        4: {'0': {4}, '1': {4}, TransitionFunction.Epsilon: {}},
    }
    func = TransitionFunction(xd, {4}, 1)
    automata = FiniteAutomata(func)

    automata.run_set('010110')

    # automata.run('1110')
    automata.visualizer.show(show_edge_labels=True)

def test_enas_to_nas():
    xd = {
        1: {'a': {2, 4}, 'b': {}, 'c': {4}, TransitionFunction.Epsilon: {}},
        2: {'a': {}, 'b': {3}, 'c': {}, TransitionFunction.Epsilon: {1}},
        3: {'a': {2}, 'b': {}, 'c': {}, TransitionFunction.Epsilon: {}},
        4: {'a': {}, 'b': {}, 'c': {3}, TransitionFunction.Epsilon: {3}},
    }
    func = TransitionFunction(xd, {3}, 1)
    func_converted = func.convert_to_deterministic()

    # automata = FiniteAutomata(func)
    automata = FiniteAutomata(func_converted)

    automata.run('abacc')

    # automata.run('1110')
    automata.visualizer.show(show_edge_labels=True, figsize=(6,6))

if __name__ == '__main__':
    # main()
    # test_enas()
    test_enas_to_nas()
