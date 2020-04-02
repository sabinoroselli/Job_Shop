import csv
def parse_resource_file(filename, num_skipped_rows):
    with open(filename, mode="r") as in_file:
        reader = csv.reader(in_file, delimiter=" ")
        jobs = []
        for i in range(num_skipped_rows):
            next(reader)
        num_jobs, num_operations = next(reader)
        num_jobs = int(num_jobs)
        num_operations = int(num_operations)

        for i, row in enumerate(reader):
            filtered_row = list(filter(lambda x: x != "", row))
            jobs.append([(int(filtered_row[j]), int(filtered_row[j+1])) for j in range(0, len(filtered_row), 2)])
            ultimate=[x for x in jobs if x!=[]]
    return ultimate, num_jobs, num_operations


# an example of how to use the parser
# from z3 import *
# source_list,num_jobs,num_operations = parse_resource_file('benchmark/ft06',4)
# a=sum(int(elem[1]) for row in source_list for elem in row )
# pp(source_list[0])