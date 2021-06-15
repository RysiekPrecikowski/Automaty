from pprint import pprint

def concatenate_languages(l1, l2):
    res = set()

    for c1 in l1:
        for c2 in l2:
            res.add(str(c1)+str(c2))

    return res

def l_to_pow(l, to_pow):
    l_curr = {''}

    for i in range(to_pow):
        l_curr = (concatenate_languages(l, l_curr))

    return l_curr

if __name__ == '__main__':
    l = {'0', '10', '111', '001'}
    m = {'', '1', '01', '10'}


    x = l_to_pow(m, 3)
    i = 2
    x = concatenate_languages(l_to_pow(l, i), l_to_pow(m, i))
    pprint(x)
    print(len(x))
