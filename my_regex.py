from typing import Dict, Any, Set

import FA



class TransictionFunction(FA.TransitionFunction):
    def __init__(self, regex):
        def xd(text):
            stack = [(i, c) for i, c in enumerate(text)][::-1]

            para = []
            i = 0
            while i < len(text):

                c = text[i]

                if c == '(':
                    print(i, c, text)
                    xd(text[i + 1:])

                if c == ')':
                    None
                    print(i, c, text)
                    return text[:i]

                i += 1

        xd(regex)




if __name__ == '__main__':
    test = TransictionFunction('A((A+B)*)')