from SMT_executor import SMT_exe, SMT_instance_runner
from SMT_translator import store_size
from JSP_dictonaries import sfr_archive, lawrence_archive, fisher_archive, applegate_archive, adams_archive

models = ['bv','ti']

solvers = ['z3','Opti']

archives = [lawrence_archive, applegate_archive, adams_archive, fisher_archive]

# SMT_instance_runner(sfr_archive,'bv','sfr30','Opti',1200,200)

for bound in range(129,2*126+3,3):
	SMT_instance_runner(sfr_archive,'bv','sfr30','Opti',1200,bound)
	SMT_instance_runner(sfr_archive,'ti','sfr30','z3',1200,bound)


# for instance in temp_archive:
#     SMT_instance_runner(temp_archive, 'ti', instance, 'z3', 10)
#
# for instance in sfr_archive:
#     SMT_instance_runner(sfr_archive, 'bv', instance, 'z3', 10)

# for solver in solvers:
#         for instance in lawrence_archive:
#             SMT_instance_runner(lawrence_archive,'bv',instance,'Opti')
#
# SMT_instance_runner(fisher_archive,'ti','ft06','z3')
# SMT_instance_runner(fisher_archive,'ti','ft06','Opti')

# for model in models:
#     for solver in solvers:
#         for instance in sfr_archive_2:
#             SMT_instance_runner(sfr_archive_2, model, instance, solver)

# for model in models:
#     for instance in sfr_archive:
#         store_size(sfr_archive,instance,model)
