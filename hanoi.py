import sys


def create_domain_file(domain_file_name, n_, m_):
    disks = ['d_%s' % i for i in list(range(n_))]  # [d_0,..., d_(n_ - 1)]
    pegs = ['p_%s' % i for i in list(range(m_))]  # [p_0,..., p_(m_ - 1)]
    domain_file = open(domain_file_name, 'w')  # use domain_file.write(str) to write to domain_file

    for p in pegs:
        domain_file.write(f"CLEAR{p}")
        for d in disks:
            domain_file.write(f"{d}SMALLER{p}")
            domain_file.write(f"{d}ON{p}")

    for d in disks:
        domain_file.write(f"CLEAR{d}")

    for i, d1 in enumerate(disks):
        for d2 in disks[i + 1:]:
            domain_file.write(f"{d1}SMALLER{d2}")
            domain_file.write(f"{d1}ON{d2}")

    for d in disks:
        for a in disks + pegs:
            for b in disks + pegs:
                if (a[0] == "d" and d >= a) or (b[0] == "d" and d >= b):
                    continue
                domain_file.write(f"Name: M{d}P{a}P{b}")
                domain_file.write(f"Pre: CLEAR{d} {d}ON{a} CLEAR{b} {a}SMALLER{b}")
                domain_file.write(f"Add: CLEAR{a} {d}ON{b}")
                domain_file.write(f"Del: {d}ON{a} CLEAR{b}")

    domain_file.close()


def create_problem_file(problem_file_name_, n_, m_):
    disks = ['d_%s' % i for i in list(range(n_))]  # [d_0,..., d_(n_ - 1)]
    pegs = ['p_%s' % i for i in list(range(m_))]  # [p_0,..., p_(m_ - 1)]
    problem_file = open(problem_file_name_, 'w')  # use problem_file.write(str) to write to problem_file
    "*** YOUR CODE HERE ***"

    problem_file.close()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: hanoi.py n m')
        sys.exit(2)

    n = int(float(sys.argv[1]))  # number of disks
    m = int(float(sys.argv[2]))  # number of pegs

    domain_file_name = 'hanoi_%s_%s_domain.txt' % (n, m)
    problem_file_name = 'hanoi_%s_%s_problem.txt' % (n, m)

    create_domain_file(domain_file_name, n, m)
    create_problem_file(problem_file_name, n, m)
