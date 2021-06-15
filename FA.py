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

    @staticmethod
    def print_helper(s):
        res = '{'
        for i, state in enumerate(s):
            res += str(state) + (' ' if i < len(s) - 1 else '')

        return res + '}'

    def convert_to_deterministic(self, table=None, alphabet=None, starting_states=None, accepting_states=None):


        if table is None:
            table = self.table
        if alphabet is None:
            alphabet = self.alphabet
        if starting_states is None:
            starting_states = self.starting_state
        if accepting_states is None:
            accepting_states = self.accepting_states

        # pprint(table)

        res_table = {}
        res_accepting_states = set()

        states = {frozenset([starting_states])}

        # print(self.get_epsilon_closure(starting_states))

        x = set()
        for state in self.get_epsilon_closure(starting_states):
            x.add(state)

        states = {frozenset(x)}

        for xd in states:
            starting_state = set()
            for state in xd:
                # print(state)
                starting_state.add(state)

            # print(starting_state)

        starting_states_res = frozenset(starting_state)

        print("STARTING", self.print_helper(starting_states_res))
        while states:
            current_states = states.pop()
            res_table[current_states] = {}

            if len(accepting_states & current_states) > 0:
                res_accepting_states.add(current_states)

            for l in alphabet - {self.Epsilon, self.Epsilon_closure}:
                new_state = set()
                for state in current_states:
                    if l not in table[state]:
                        continue
                    transition_to = table[state][l]

                    for to_state in transition_to:
                        new_state.add(to_state)

                        for x in self.get_epsilon_closure(to_state):
                            new_state.add(x)

                        # print(l, to_state, self.get_epsilon_closure(to_state) )

                if frozenset(new_state) not in res_table:
                    states.add(frozenset(new_state))

                res_table[current_states][l] = frozenset(new_state)

        # pprint(res_table)
        print("\nCONVERTED TO DETERMINISTIC")


        for state, idk in res_table.items():
            spaces = ' ' * (len(str(self.print_helper(state))) + len(" ---> {"))
            print(self.print_helper(state), end=" ---> {\n")
            for symbol, to in idk.items():
                print(spaces + str(symbol)+' --> '+str(self.print_helper(to)), end=',\n')

            print(spaces+"}")


        print('\nACCEPTING STATES')
        for state in res_accepting_states:
            print(self.print_helper(state))


        res = TransitionFunction(res_table, res_accepting_states, starting_states_res)
        res.deterministic = True
        return res

    def __getitem__(self, item):
        return self.table[item]


    def minimize(self):
        class cell:
            def __init__(self):
                self.dist = False

            def __repr__(self):
                return str(self.dist)

        def get(s0, s1) -> cell:
            if s0 in arr and s1 in arr[s0]:
                return arr[s0][s1]
            if s1 in arr and s0 in arr[s1]:
                return arr[s1][s0]

            return cell()

        arr = {s : {} for s in list(self.table)[:len(self.table) -1]}

        for i in range(1, len(self.table)):
            for k in list(arr.keys())[:i]:
                for s in list(self.table)[i:]:
                    arr[k][s] = cell()

                    if (s in self.accepting_states) ^ (k in self.accepting_states): # ^ to xor
                        # if s in self.accepting_states and
                        arr[k][s].dist = True

        pprint(arr)


        change = True
        while change:
            change = False
            for s0 in arr.keys():
                for s1 in arr[s0].keys():
                    for l in self.alphabet:
                        try:
                            a0 = list(self[s0][l]).pop()
                            a1 = list(self[s1][l]).pop()
                        except BaseException:
                            continue

                        tile = get(a0, a1)
                        # print(a0, a1, tile)
                        if tile.dist and get(s0, s1).dist is False:
                            get(s0, s1).dist = True
                            change = True

        pprint(arr)
        states = set(self.table.keys())
        used_states = set()
        new_states = set()

        for s0 in arr.keys():
            for s1 in arr[s0].keys():
                if not arr[s0][s1].dist:
                    # print(s0, s1)
                    used_states.add(s0)
                    used_states.add(s1)
                    new_states.add(frozenset([s0, s1]))

        for state in states - used_states:
            new_states.add(frozenset([state]))

        new_starting_state = None
        new_accepting_states = set()
        new_table = {s : {} for s in new_states}
        for state in new_states:
            if self.starting_state in state:
                new_starting_state = state

            if len(self.accepting_states & state):
                new_accepting_states.add(state)

            original = list(state)[0]

            for l in self.alphabet:
                for s in new_states:
                    if not self.table[original][l]:
                        continue
                    if len(self.table[original][l] & s) > 0:
                        new_table[state][l] = s


        print()
        print("STARTING :", self.print_helper(new_starting_state))
        print("ACCEPTING:", end=" ")
        for state in new_accepting_states:
            print(self.print_helper(state), end=", ")
        print()

        for state, idk in new_table.items():
            spaces = ' ' * (len(str(self.print_helper(state))) + len(" ---> {"))
            print(self.print_helper(state), end=" ---> {\n")
            for symbol, to in idk.items():
                print(spaces + str(symbol) + ' --> ' + str(self.print_helper(to)), end=',\n')

            print(spaces + "}")
        # pprint(new_table)

        self.accepting_states = new_accepting_states
        self.starting_state = new_starting_state
        self.table = new_table

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

        def show(self, show_edge_labels=False, figsize=(5, 5)):
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
                if l not in self.transition_function[state.state]:
                    continue

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
                if l not in self.transition_function[state.state]:
                    continue

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
    # automata = FiniteAutomata(func_converted)
    #
    # automata.run('110100')
    #
    automata.run('111000')
    automata.visualizer.show(show_edge_labels=False)

def test_minimize():
    xd = {
        'A': {'0': {'B'}, '1': {'F'}},
        'B': {'0': {'G'}, '1': {'C'}},
        'C': {'0': {}, '1': {'C'}},
        'D': {'0': {'C'}, '1': {'G'}},
        'E': {'0': {'H'}, '1': {'F'}},
        'F': {'0': {'C'}, '1': {'G'}},
        'G': {'0': {'G'}, '1': {'E'}},
        'H': {'0': {'G'}, '1': {'C'}},
    }
    func = TransitionFunction(xd, {'C'}, 'A')
    func.minimize()

    xd = {
        'A': {'0': {'B'}, '1': {'A'}},
        'B': {'0': {'A'}, '1': {'C'}},
        'C': {'0': {'D'}, '1': {'B'}},
        'D': {'0': {'D'}, '1': {'A'}},
        'E': {'0': {'D'}, '1': {'F'}},
        'F': {'0': {'G'}, '1': {'E'}},
        'G': {'0': {'F'}, '1': {'G'}},
        'H': {'0': {'G'}, '1': {'D'}},
    }
    func = TransitionFunction(xd, {'D'}, 'A')
    func.minimize()

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
    # test_enas_to_nas()
    test_minimize()

    # func5c = TransitionFunction(
    #     {
    #         'q0': {'0': {},
    #                TransitionFunction.Epsilon: {'q1', 'q3'}},
    #
    #         'q1': {'0': {'q2'},
    #                TransitionFunction.Epsilon: {}},
    #
    #         'q2': {'0': {'q1'},
    #                TransitionFunction.Epsilon: {}},
    #
    #         'q3': {'0': {'q4'},
    #                TransitionFunction.Epsilon: {}},
    #
    #         'q4': {'0': {'q5'},
    #                TransitionFunction.Epsilon: {}},
    #
    #         'q5': {'0': {'q3'},
    #                TransitionFunction.Epsilon: {}},
    #
    #     },
    #     {'q1', 'q3'},
    #     'q0'
    # )
    # func_converted5c = func5c.convert_to_deterministic()