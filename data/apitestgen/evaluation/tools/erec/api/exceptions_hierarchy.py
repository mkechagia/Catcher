#!/usr/bin/env python3

__author___= "Maria Kechagia"
__copyright__= "Copyright 2018"
__license__= "Apache License, Version 2.0"
__email__= "m.kechagiaATtudelft.nl"
__updated__="ataupill@ualberta.ca"

import re
import os
import json
import sys
import time

from collections import defaultdict
from collections import OrderedDict

import networkx as nx
from networkx.readwrite import json_graph
from networkx.algorithms.traversal.depth_first_search import dfs_edges

# folder for .jimple files
global path_app
path_app = sys.argv[1] # "../eRec/apps/jar/"
# folder for JSON files
global path_JSON
path_JSON = sys.argv[2] # "../experiment/$FILE/"
# version of the API used in the app
global api_version
api_version = sys.argv[3] # e.g. 8 (for Java 8)
# name of the API used in the app
global api_name
api_name = sys.argv[4] # java, apache-commons-lang, etc.

G=nx.Graph()
DG=nx.DiGraph(G)

def main():
	start = time.time()

	# open and parse .jimple files
	read_folder()
	#print(DG.nodes.data()
	#add_dict_to_JSON(DG)
	succ_dict = {}
	for nd in DG:
		# dictionary for node's successors (including the nd) for inter procedural analysis
		bfs_lst = list(nx.bfs_successors(DG, nd))
		path_lst = []
		for k, l in enumerate(bfs_lst):
			child_parent = bfs_lst[k]
			path_lst.append(child_parent[0])
			succ_dict.setdefault(nd, path_lst)
		#print "Predecessor of: "+ nd + " " + str(bfs_dict) + "\n"
	with open(path_JSON+"/exceptions-succ.json", 'w') as fp:
		json.dump(succ_dict, fp, indent = 4)
		end = time.time()

		print("Exception hierarchy building duration: "+str(end-start))

def read_folder():
	app_name = ""
	# list app folders (first level subfolders)
	dir_list = next(os.walk(path_app))[1]
	for k, l in enumerate(dir_list):
		app_name = dir_list[k]
		if ((re.search("^derbyTesting$", app_name)) or (re.search("^asm-3.1$", app_name)) or (re.search("^antlr-3.1.3$", app_name))):
			print("Possible issues with these .jar files ...") # from Dacapo benchmark
			continue
		else:
			path = path_app + "/" + dir_list[k]
			# search in the files of the app folder
			files = os.listdir(path)
			if ((len(files) > 2) and (api_version != "")):
				read_files(files, path)

def read_files(files, app_path):
	for f in files:
		e = re.search(".*(Exception)\.jimple", f)
		if e:
			j_file = app_path + "/" + f
			parse_jimple(j_file)

def parse_jimple(file):
	f = open(file)
	lines = f.readlines()
	for l, k in enumerate(lines):
		if re.search(".*(Exception).*(extends).*(Exception)", lines[l]):
			hierarchy = re.split("(extends)", lines[l])
			child = re.search("[a-z]+\..*(Exception)", hierarchy[0]).group()
			parent = re.search("[a-z]+\..*(Exception)", hierarchy[2]).group()
			if (parent not in DG.nodes()):
				DG.add_node(parent)
			if (child not in DG.nodes()):
				DG.add_node(child)
			DG.add_edge(child, parent)

# serialize the call graph
def add_dict_to_JSON(DG):
	file_name = 'exceptions.json'
	with open(file_name, 'w') as fp:
		data = json_graph.node_link_data(DG, attrs=None)
		json.dump(data, fp, indent = 4)

# run main
if __name__ == "__main__":
	main()
