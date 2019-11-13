import math


def calculate_slot(priority, N, heuristic_value, bap_type):
    # adjustment parameter calculation:
    p = N / (((priority ** 3) * heuristic_value) + N)

    time = range(0, N)
    binomial_list = []
    # Binomial calculation:
    for r in range(0, N):
        nCr = math.factorial(N) / (math.factorial(r) * math.factorial(N - r))  # Generate nCr
        binomial = nCr * (p ** r) * ((1 - p) ** (N - r))  # Binomial equation
        binomial_list.append(binomial)

    if bap_type >= len(binomial_list):
        return "Null", "Null"

    binomial_ls = sorted(binomial_list, reverse=True)
    index_of_max = binomial_list.index(binomial_ls[bap_type])

    return time[index_of_max], binomial_list[index_of_max]
