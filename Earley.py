#All credits goes to ???? (its not my code, i don't know where I've got this

from queue import PriorityQueue


class State(object):
    def __init__(self, lhs, rhs, loc, origin=None, pos=0):
        assert len(rhs) >= pos
        self.lhs = lhs
        self.rhs = tuple(rhs)
        self.pos = pos
        self.loc = loc
        if origin is None:
            self.origin = self.loc
        else:
            self.origin = origin

    def __str__(self):
        rhs_dot = list(self.rhs)
        rhs_dot.insert(self.pos, '•')
        rhs_str = ' '.join(rhs_dot)
        return '(%d, %s -> %s, %d)' % (self.loc, self.lhs, rhs_str, self.origin)

    __repr__ = __str__

    def __eq__(self, other):
        return (self.loc, self.origin, self.lhs, self.rhs, self.pos) == \
               (other.loc, other.origin, other.lhs, other.rhs, other.pos)

    def __lt__(self, other):
        return (self.loc, self.origin, self.lhs, self.rhs, self.pos) < \
               (other.loc, other.origin, other.lhs, other.rhs, other.pos)

    def __hash__(self):
        return hash((self.lhs, self.rhs, self.pos, self.origin, self.loc))

    def finished(self):
        return self.pos == len(self.rhs)

    def next_word(self):
        return self.rhs[self.pos]

    def incr_word(self, loc):
        return State(self.lhs, self.rhs, loc, self.origin, self.pos + 1)


def parse(grammar, sentence):
    work = PriorityQueue()
    chart = set()
    history = []

    def enqueue(s):
        if s not in chart:
            work.put((s.loc, s))
            history.append(s)
        chart.add(s)

    def predict(s):
        for rhs in grammar[s.next_word()]:
            enqueue(State(s.next_word(), rhs, s.loc))

    def scan(s):
        if s.loc + 1 <= len(sentence) and sentence[s.loc] == s.next_word():
            enqueue(s.incr_word(s.loc + 1))

    def complete(s):
        for c in [c for c in chart if (not c.finished()) and c.next_word() == s.lhs and c.loc == s.origin]:
            enqueue(c.incr_word(s.loc))

    for rhs in grammar['START']:
        enqueue(State('START', rhs, 0))

    while not work.empty():
        (loc, s) = work.get()
        if not s.finished():
            if s.next_word() in grammar:
                predict(s)
            else:
                scan(s)
        else:
            complete(s)


    return history

#
# grammar = {
#     'START': {'E'},
#     'E': {'T', 'E+T'},
#     'T': {'P', 'T*P'},
#     'P': {'a'}
# }
from pprint import pprint

# pprint(parse(grammar, 'a+a*a'))

# grammar = {
#     'START': {'S'},
#     'S': {'AB', 'BC'},
#     'A': {'BA', 'a'},
#     'B': {'CC', 'b'},
#     'C': {'AB', 'a'}
# }
#
# pprint(parse(grammar, 'baaa'))
# print(len(parse(grammar, 'baaa')))



grammar = {
    'START': {'E'},
    'E': {'E+E', 'E*E', '(E)', 'I'},
    'I': {'a'},
}

pprint(parse(grammar, '((a))'))
# print(len(parse(grammar, 'baaa')))


from collections import Counter

c = Counter("""2:1>3
4:1>5
3:$>4
0:$>2,6,22
5:$>1
10:1>11
8:$>10,12,14,20
11:$>9
12:0>13
13:$>9
14:1>15
18:1>19
16:$>17,18
19:$>18,17
15:$>16
17:$>9
20:1>21
21:$>9
6:$>7,8
9:$>8,7
7:$>1
24:1>25
26:0>27
25:$>26
30:1>31
28:$>29,30
31:$>30,29
27:$>28
22:$>24,32,36
29:$>23
32:1>33
34:1>35
33:$>34
35:$>23
36:0>37
37:$>23
23:$>1""")

pprint(c)
