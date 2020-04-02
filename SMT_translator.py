from z3 import *
from JSP_functions import toSMTBenchmark
from JSP_instance_parser import parse_resource_file
from JSP_classes import operation,resource,relation,allocation
import os

def model_converter(archive,instance,model,H = None):
    print('i am parsing the instance')
    source_list,num_jobs,num_operations = parse_resource_file('benchmark/%s' % instance,4)

    if H == None:
        print('no bound given, using value from archive')
        H = round(archive[instance]*1.1)
    else:
        print('the value provided for the bound is: ', H)

    ops=[ operation(i+j*len(source_list[j]),source_list[j][i][1])
        for j in range(len(source_list))  for i in range(len(source_list[0])) ]
    ress=[ resource(i,1) for i in range(len(source_list[0])) ]
    rels=[ relation(ops[i+j*len(source_list[j])],ops[(i+j*len(source_list[j]))+1])
        for j in range(len(source_list)) for i in range(len(source_list[0])-1) ]
    allos=[ allocation(ress[int(source_list[j][i][0])],ops[i+j*len(source_list[j])])
        for j in range(len(source_list)) for i in range(len(source_list[0])) ]
    print('i am calling the model')
    s = Solver()
    if model == 'ds':
        from JSP_models import disjunctive
        start,dom,precedence_constraints,al2,minmax,Z = disjunctive(ops,rels,ress,allos,source_list,num_operations)
        s.add(dom+precedence_constraints+al2+minmax)

    elif model=='rb':
        from JSP_models import rank_based
        x,r,h,dom,uni,precedence,input_data,minmax,res_req,Z = rank_based(ops,ress,allos,source_list,num_jobs)
        s.add(dom+uni+precedence+input_data+minmax+res_req)

    elif model=='ti':
        from JSP_models import time_index
        ex,allo,count,preco,mini,minimax,cond,final,Z = time_index(ops,rels,ress,allos,H)
        s.add(preco+mini+minimax+cond+final)

    elif model == 'bv':
        from JSP_models import bit_vector
        Z, only_once, non_overlap, latest, precedence, first_bit, opti = bit_vector(source_list,H)
        s.add(only_once + non_overlap +  latest + precedence + first_bit + opti)
    else:
        raise ValueError('the model you are trying to use does not exists')

    data_log = open('Z_SMT_store.txt','w')
    data_log.write(toSMTBenchmark(s,""))
    data_log = open("Z_SMT_store.txt","r")
    lines = data_log.readlines()
    data_log.close()
    data_log = open("Z_SMT_store.txt","w")
    for line in lines:
        if line!="(check-sat)"+"\n":
            data_log.write(line)
    if model =='bv':
        data_log.write('(maximize Z)\n')
    else:
        data_log.write('(minimize Z)\n')
    data_log.write('(check-sat)\n')
    data_log.write('(get-objectives)')
    data_log.close()
    print('the model has been translated ')
    file_size = os.path.getsize('Z_SMT_store.txt')
    print('file size (in bytes): ', file_size)
    return H,file_size


#this function only measures the model size without actually running the instance
def store_size(archive,instance,model):
    print('#################################################')
    print('i am evaluating the instance %s \n with model %s' % (instance, model))

    H, file_size = model_converter(archive,instance,model)

    data_log = open('Z_models_data.txt','a')
    data_log.write('%s, %s, %s \n' % (instance, model, file_size))
    data_log.close()
    return file_size
