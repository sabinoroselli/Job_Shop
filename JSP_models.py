from z3 import *
from JSP_functions import dur_writer, iterate_or, iterate_and

def bit_vector(source_list,H):

    #sum(elem[1] for row in source_list for elem in row)
    print('bound',H)
    # impostazione funzione obiettivo
    Z = BitVec('Z', H)

    #duration of operations
    duration = [[elem[1] for elem in row] for row in source_list]

    # Start_ij is a bit vector of length H representing operation i and job j
    start = [[BitVec('start_%s_%s' % (j + 1, i + 1), H)
              for i in range(len(source_list[j]))] for j in range(len(source_list))]


    # d variables are used to set the latest started time for each operation
    d = [[BitVecVal(int(dur_writer(duration[j][i]), 2), H)
          for i in range(len(source_list[j]))] for j in range(len(source_list))]

    # this constraint states that the bit vectors have to be different from zero
    only_once_1 = [start[j][i] != 0 for j in range(len(source_list)) for i in range(len(source_list[j]))]

    # this constraint states that each bitvector should be a power of two
    only_once_2 = [start[j][i] & (start[j][i] - 1) == False for j in range(len(source_list))
                   for i in range(len(source_list[j]))]

    only_once = only_once_1 + only_once_2

    # this list contains sub-lists that group all operations sharing the same resource
    sharing = [
        [(j, i) for j in range(len(source_list)) for i in range(len(source_list[j]))
         if source_list[j][i][0] == n]
        for n in range(len(source_list))
    ]

    # this is the non-overlapping constraint, preventing operations sharing the same resource
    # to take place at the same time
    non_overlap = [
        iterate_or([(start[sharing[k][i][0]][sharing[k][i][1]] >> n) for n in
                    range(duration[sharing[k][i][0]][sharing[k][i][1]])])
        &
        iterate_or([(start[sharing[k][j][0]][sharing[k][j][1]] >> n) for n in
                    range(duration[sharing[k][j][0]][sharing[k][j][1]])])
        == 0
        for k in range(len(sharing))
        for i in range(len(sharing[k]))
        for j in range(i)
    ]

    # this constraint sets the latest possible start for an operation so that it can be completed within the time horizon
    latest = [
        start[j][i] & d[j][i] == 0 for j in range(len(source_list)) for i in range(len(source_list[j]))
    ]


    # this is the prececence constraint
    precedence = [
        (~(~(iterate_or([(start[j][i] >> n) for n in range(duration[j][i])]) | (
            -iterate_or([(start[j][i] >> n) for n in range(duration[j][i])]))))) & start[j][i + 1] == 0
        for j in range(len(source_list))
        for i in range(len(source_list[j]) - 1)
    ]

    # this function makes the most significant bit equal to zero
    first_bit = [
        start[j][i] & (1 << H - 1) == 0
        for j in range(len(source_list))
        for i in range(len(source_list[j]))
    ]

    # setting the objective function
    opti = [Z == iterate_and([~(iterate_or([(start[j][i] >> n) for n in range(duration[j][i])]) | (
        -iterate_or([(start[j][i] >> n) for n in range(duration[j][i])]))) for j in range(len(start)) for i in
                              range(len(start[j]))])]

    return  Z, only_once, non_overlap, latest, precedence, first_bit, opti


def rank_based(ops, ress, allos, source_list, num_jobs):
    num_positions = num_jobs

    Z = Int('Z')

    # x(i,j,k) is true is machine i is assigned to job j at the k-th position
    x = [[[Bool('x_%s_%s_%s' % (i, j, k)) for k in range(num_positions)] for j in range(len(ops))] for i in
         range(len(ress))]
    # r(i,j) is true if job j requires machine i
    r = [[Bool('r_%s_%s' % (i, j)) for j in range(len(ops))] for i in range(len(ress))]
    # h(i,k) is the start time of the job at the k-th position of machine i
    h = [[Int('h_%s_%s' % (i, k)) for k in range(num_positions)] for i in range(len(ress))]

    # operation start time cannot be negative
    dom = [h[i][k] >= 0 for i in range(len(ress)) for k in range(num_positions)]
    # only one job is assigned to a machine at a certain position
    assign_one_pos = [
        PbLe([(x[i][j][k], 1) for j in range(len(ops))], 1) for i in range(len(ress)) for k in range(num_positions)
    ]

    # the job can be assigned to the machine only once
    get_one_job = [
        PbLe([(x[i.resource.name][i.operation.name][k], 1) for k in range(num_positions)], 1) for i in allos
    ]

    uni = get_one_job + assign_one_pos
    # if a job is assigned to a machine at a position, the nex one cannot be assigned till the process is running
    machine_precedence = [
        Implies(
            x[i.resource.name][i.operation.name][k],
            h[i.resource.name][k] + i.operation.duration <= h[i.resource.name][k + 1]
        )
        for i in allos for k in range(num_positions - 1)
    ]
    # operations belonging to the same job must follow the predecided sequence
    job_precedence1 = [
        Implies(
            And(x[source_list[j][i][0]][len(ress) * j + i][k1], x[source_list[j][i + 1][0]][len(ress) * j + i + 1][k2]),
            h[source_list[j][i][0]][k1] + source_list[j][i][1] <= h[source_list[j][i + 1][0]][k2]
        )
        for j in range(len(source_list)) for i in range(len(source_list[j]) - 1)
        for k1 in range(num_positions) for k2 in range(num_positions)
    ]

    precedence = job_precedence1 + machine_precedence

    minmax = [
        Implies(
            x[j.resource.name][j.operation.name][k],
            h[j.resource.name][k] + j.operation.duration <= Z
        ) for j in allos for k in range(num_positions)
    ]

    input_data = [
        And(r[i.resource.name][i.operation.name]) for i in allos
    ]

    res_req = [
        Implies(
            r[i.resource.name][i.operation.name],
            Or([x[i.resource.name][i.operation.name][k] for k in range(num_positions)])
        )
        for i in allos
    ]

    return x, r, h, dom, uni, precedence, input_data, minmax, res_req, Z

def time_index(ops, rels, ress, allos, H):
    # impostazione funzione obiettivo
    Z = Int('Z')
    ts = H  # sum(elem[1] for row in source_list for elem in row )

    ex = [[Bool('ex%s_%s' % (i + 1, j + 1)) for j in range(ts)] for i in range(len(ops))]
    allo = [[[Bool('allo%s_%s_%s' % (i + 1, j + 1, k + 1)) for k in range(ts)] for j in range(len(ops))]
            for i in range(len(ress))]
    count = [[Int('count%s_%s' % (i + 1, j + 1)) for j in range(ts)] for i in range(len(ops))]

    # non posso eseguire B se non ho eseguito A
    preco11 = [
        Implies(
            And([Not(ex[rels[i].op1.name][k]) for k in range(t)]),
            And([Not(ex[rels[i].op2.name][j]) for j in range(t + rels[i].op1.duration)])
        )
        for i in range(len(rels)) for t in range(1, ts - rels[i].op1.duration)
    ]

    preco12 = [And([Not(ex[rels[i].op2.name][j]) for j in range(rels[i].op1.duration)]) for i in range(len(rels))]

    preco1 = preco11 + preco12
    # allocamento risorse per esecuzione

    preco2 = [
        Implies(
            Not(allo[allos[i].resource.name][allos[i].operation.name][t]),
            Not(ex[allos[i].operation.name][t])
        )
        for i in range(len(allos)) for t in range(ts)
    ]

    # sorting the allocation by operations that require a certain resource to execute
    sort2 = [[x for x in allos if x.resource.name == i] for i in range(len(ress))]

    # constraint preco 3 had to be split in two parts to make the model readible by OptiMathSAT (in order two avoid
    # empty And() clauses that are ok for z3, but not with Opti)
    preco32 = [
        Implies(
            allo[sort2[i][0].resource.name][sort2[i][0].operation.name][t],
            And([Not(allo[sort2[i][k].resource.name][sort2[i][k].operation.name][t]) for k in range(1, len(sort2[i]))]),
        )
        for i in range(len(sort2)) for t in range(ts)
    ]

    preco33 = [
        Implies(
            allo[sort2[i][j].resource.name][sort2[i][j].operation.name][t],
            And([Not(allo[sort2[i][k].resource.name][sort2[i][k].operation.name][t]) for k in
                 range(j + 1, len(sort2[i]))])
        )
        for i in range(len(sort2)) for j in range(len(sort2[i]) - 1) for t in range(ts)
    ]
    preco3 = preco32 + preco33

    preco = preco1 + preco2 + preco3

    # if an operation takes place it wil last for as long as its duration (does this make sense?)

    final = [
        Implies(
            And(
                ex[allos[i].operation.name][t],

            ),
            And([allo[allos[i].resource.name][allos[i].operation.name][k]
                 for k in range(t, t + allos[i].operation.duration)])
        )
        for i in range(len(allos)) for t in range(ts - allos[i].operation.duration)
    ]

    # esecuzione delle operazioni
    cond = [
        Or([
            ex[i][k] for k in range(ts)
        ])
        for i in range(len(ops))
    ]

    # minimizzazione del tempo
    mini = [
        If(
            ex[i.name][t],
            count[i.name][t] == t + i.duration,
            count[i.name][t] == 0
        )
        for i in ops for t in range(ts)
    ]

    minimax = [
        Z >= Sum([count[i][t] for t in range(ts)])
        for i in range(len(ops))
    ]

    return ex, allo, count, preco, mini, minimax, cond, final, Z


def disjunctive(ops, rels, ress, allos, source_list, num_operations):
    # declatation of the objective function
    Z = Int('Z')

    # variables of the problem
    start = [Int('start%s' % (i + 1)) for i in range(len(ops))]

    # start and idle variables values must be set larger or equal than zero

    dom = [start[i] >= 0 for i in range(len(ops))]

    # if an operation is executed, then its starting time must be larger than the end time of the previous one
    precedence_constraints = [start[rels[i].op2.name] >= start[rels[i].op1.name] + ops[rels[i].op1.name].duration for i
                              in range(len(rels))]

    # sorting thew allocation by operations that require a certain resource to execute
    sorted_list = [[x for x in allos if x.resource.name == i] for i in range(len(ress))]

    # if a resource is allocated to more than one operation, these can not overlap
    al2 = [
        And(
            [Or(
                start[sorted_list[k][i].operation.name] >= start[sorted_list[k][j].operation.name] + ops[
                    sorted_list[k][j].operation.name].duration,
                start[sorted_list[k][j].operation.name] >= start[sorted_list[k][i].operation.name] + ops[
                    sorted_list[k][i].operation.name].duration
            )
                for i in range(len(sorted_list[k])) for j in range(i + 1, len(sorted_list[k]))]
        ) for k in range(len(sorted_list))
    ]

    # if we have multiple sequences it is a minmax problem, therefore we set the following constraint
    minmax = [Z >= start[i * num_operations - 1] + ops[i * num_operations - 1].duration for i in
              range(1, len(source_list) + 1)]

    return start, dom, precedence_constraints, al2, minmax, Z