from z3 import *


def result_reader(val):
    count = 0
    while val[count] == '0':
        count += 1
    return count-1

def result_reader2(val):
    return len(list(val)[2:])

def dur_writer(dur):
    buffer = ['1' for i in range(dur)]
    return ''.join(buffer)

def iterate_and(lista):
    if len(lista)==1:
        return lista[0]
    elif len(lista)== 2:
        return lista[0] & lista[1]
    else:
        return lista[0] & iterate_and(lista[1:])

def iterate_or(lista):
    if len(lista)==1:
        return lista[0]
    elif len(lista)== 2:
        return lista[0] | lista[1]
    else:
        return lista[0] | iterate_or(lista[1:])

def toSMTBenchmark(f, logic="", status="unknown", name="benchmark"):
    v = (Ast * 0)()
    if isinstance(f, Solver):
        a = f.assertions()
        if len(a) == 0:
            f = BoolVal(True)
        else:
            f = And(*a)
    r = Z3_benchmark_to_smtlib_string(f.ctx_ref(), name, logic, status, "", 0, v, f.as_ast())
    Z3_set_ast_print_mode(f.ctx_ref(), Z3_PRINT_SMTLIB2_COMPLIANT)  # Restore SMTLIB 2.x pretty print mode
    return r

