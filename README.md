JOB SHOP SCHEDULER

the scheduler requires the SMT solvers Z3Opt and OptiMathSAT to be installed in order to work. 

additional python packages such as "subprocess", "os", "re", "time", "csv" are required.

the file "interface" is used to show examples on how to call the main functions of the scheduler and what parameters to set.
it is possible to solve a single instance or to make dictonaries that contain batches of instances and solve all of them. the data
generated when solving an instance is stored in the file 'Z_models_data'.



every time the scheduler has to solve an instance, the parser function 'parse_resource_file' contained in the file 'JSP_instance_parser'
generates the list of jobs (for each job, the sequence of machines and the respective duration are specified)

then, depending on what formulation is chosen (models are written in the file 'JSP_models'), a model is created and then 
translated into the SMT standard language through the file 'SMT_translator' and save it in the txt file 'Z_SMT_store'.

the model is then read using the function 'SMT_exe' from the file 'SMT_executor', which calls either z3 or optimathsat to solve it. 
the function 'SMT_instance_runner', also contained in the same file, iterates the function 'SMT_exe' over a batch of instances whose names
are stored in a dictonary (input for the function). 


the following files contain additional functions that support the main ones in the scheduling process:
JSP_classes : python classes for operations, resources, etc. that help build the models;
JSP_dictonaries: here are stored the dictonaries to use when one wants to run a batch of instances automatically;
JSP_functions: additional functions that are used to iterate bit-wise operations to build the bit vectors model. also the 
fuction that translates a z3 model generated through the python API into SMT standard language.
