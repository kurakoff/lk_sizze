def separate_by_n(ar, n=2):
    new_ar = [[]]
    for i in range(0, len(ar)):
        if len(new_ar[-1]) == n:
            new_ar.append([])
        new_ar[-1].append(ar[i])
    return new_ar
