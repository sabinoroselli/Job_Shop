import subprocess
import os
import re
import time
from SMT_translator import model_converter
from JSP_functions import result_reader2

def SMT_exe(archive,model,prover,instance,t_out,bound):


    print('i am converting the instance into SMT-stdlib')
    generation_start = time.time()
    H, file_size = model_converter(archive,instance,model,bound)
    generation_end = time.time() - generation_start
    print('generation time: ', generation_end)
    print('the solver is running the instance')
    if prover == 'z3':

        start = time.time()
        p = subprocess.Popen("z3 -smt2 -t:%s Z_SMT_store.txt"
                             % (t_out*1000) , stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        end = time.time()
        output = output.decode('utf-8')
        feasibility = output.split()[0]
        if model == 'bv':
            result = [
                H - result_reader2(str(bin(int(x.group())))) - 1
                for x in re.finditer(r'\d+', output)][0] if feasibility == 'sat' else 'None'
        else:
            result = [int(x.group()) for x in re.finditer(r'\d+', output)][0] if feasibility != 'unsat' else 'None'

    elif prover == 'Opti':

        start = time.time()
        p = subprocess.Popen("optimathsat -model_generation=TRUE Z_SMT_store.txt",
                             stdout=subprocess.PIPE, shell=True)
        while time.time()-start<t_out and p.poll() == None:
            time.sleep(.250)

        if p.poll() == None:
            p.terminate()
            end=time.time()
            feasibility='unknown'
            result = []
            os.system('taskkill /f /im optimathsat.exe')
        else:
            (output, err) = p.communicate()
            end = time.time()
            output = output.decode('utf-8')
            feasibility = output.split()[0]
            if model == 'bv':
                result = [
                    H - result_reader2(str(bin(int(x.group())))) - 1
                    for x in re.finditer(r'\d+', output)][0] if feasibility == 'sat' else 'None'
            else:
                result = [int(x.group()) for x in re.finditer(r'\d+', output)][0] if feasibility != 'unsat' else 'None'

    else:
        raise ValueError('wrong prover name!!!')
    print('instance running is over:')
    print('optimum: ', result)
    print('runtime: ', round((end-start), 4))
    return H,feasibility, result, round((end-start), 4), round(generation_end,2), file_size

def SMT_instance_runner (archive,model,instance,solver,run_time = 1200, bound = None):
    print('#################################################')
    print('i am evaluating the instance %s \n with solver %s and model %s' % (instance,solver,model))
    obj_funs = []
    data_log = open('Z_models_data.txt','a')
    H,feasibility,obj_fun,duration,generation,file_size = SMT_exe(archive,model,solver,instance,run_time,bound)
    obj_funs.append((instance,solver,model,H,feasibility,obj_fun,duration,generation,file_size))
    data_log.write("%s, %s, %s, %s, %s, %s, %s, %s, %s  \n" % obj_funs[-1])
    data_log.close()
    return obj_funs
