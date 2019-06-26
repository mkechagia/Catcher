#!/usr/bin/env python

__author___= "Maria Kechagia"
__copyright__= "Copyright 2019"
__license__= "Apache License, Version 2.0"
__email__= "m.kechagiaATtudelft.nl"

import re
import os
import csv
import sys

from collections import defaultdict
from collections import OrderedDict

def main():
	count_tests = 0

	csv_files = sys.argv[1]
	files = get_csv_files(csv_files)

	with open('/home/guest/Documents/postprocessing/files.csv', mode='w') as files_csv:
		files_csv = csv.writer(files_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

		f_txt = open("/home/guest/Documents/postprocessing/files.txt","w") 

		# each file is a different class
		for f in files:
			f = re.sub("\n", "", f)
			coverage_dict = OrderedDict([])
			gen_test_list = []
			coverage_dict = append_dict(f,coverage_dict)
			gen_test_list = filter_dict(coverage_dict)
			if (len(gen_test_list) > 0):
				count_tests = count_tests + len(gen_test_list)
				first_log = gen_test_list[0]
				project = str(re.sub("\-[0-9]+$", "", first_log))
				for k, l in enumerate(gen_test_list):
					print str(gen_test_list[k])+".log"
					f_txt.write(str(gen_test_list[k])+".log\n")
				lst_full_path = re.split("stacktraces",f)
				class_name_1 = lst_full_path[1]
				lst_class_name_1 = re.split('/',class_name_1)
				class_name = lst_class_name_1[1]
				lst = []
				lst.append(project)
				lst.append(class_name)
				lst.append(str(gen_test_list))
				files_csv.writerow(lst)

	print "Number of tests: "+ str(count_tests)

def get_csv_files(csv_files):
	res_files = []
	f = open(csv_files, 'r')
	lines = f.readlines()
	for file in lines:
		file = re.sub("^./", "/home/guest/Documents/data/apitestgen/evaluation/experiment_all/", file)
		if (re.search("catchy_fast_results", file)):
			res_files.append(file)
	# list of files for catchy fast only
	return res_files

def append_dict(file, coverage_dict):
	coverage_dict = OrderedDict([])
	with open(file, "rb") as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		
		count = 0
		header = []

		for row in csv_reader:
			# the first line in the csv file has the names of the columns
			if (count == 0):
				# header is like: ['bcel-6.2-163', 'bcel-6.2-45']
				header = row
				for k,l in enumerate(header):
					if (header[k] not in coverage_dict.keys()):
						# dictionary will be {'bcel-6.2-163': [0], 'bcel-6.2-45': [1]}, where in [] we have the values
						coverage_dict.setdefault(header[k], []).append(k) # k is the index of the key and the first value
			elif (count > 0):
				# rows represent values: [0.0, 0.0] that sould be correclty added to the above dictionary
				for m, n in enumerate(row):
					cov_keys = coverage_dict.keys()
					for x, z in enumerate(cov_keys):
						current_vaules = coverage_dict.get(cov_keys[x])
						# index to know to which key to add the appropriate value
						index = current_vaules[0]
						if (m == index):
							coverage_dict.setdefault(cov_keys[m], []).append(row[m])
			# increase the counter				
			count = count + 1
	return coverage_dict

# remove the keys that have only non-zero values
def filter_dict(coverage_dict):
	gen_test_list = []
	cov_keys = coverage_dict.keys()
	for k, l in enumerate(cov_keys):
		current_vaules = coverage_dict.get(cov_keys[k])
		if ('0.0' in current_vaules):
			gen_test_list.append(cov_keys[k])
	return gen_test_list

# run main
if __name__ == "__main__":
	main()
