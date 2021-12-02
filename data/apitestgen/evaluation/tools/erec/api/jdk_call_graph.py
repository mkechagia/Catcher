#!/usr/bin/env python

__author___= "Maria Kechagia"
__copyright__= "Copyright 2018"
__license__= "Apache License, Version 2.0"
__email__= "m.kechagia@tudelft.nl"

'''
This script creates a call graph based on the JDK APIs
used by the analysed client app.
The depth of the exception propagation analysis, in the JDK APIs,
is set to level 3.
'''

import networkx as nx
from networkx.readwrite import json_graph

import re
import os
import json
import sys
import time

G=nx.Graph()
DG=nx.DiGraph(G)

# patterns for finding method signatures and API calls in .jimple files
p1 = "\s[a-z']+[a-zA-Z\$0-9]*\([a-zA-Z\$\_0-9\[\]\.\,\s]*\)[\s]*(throws)*.*$"
p2 = "[\s]*\{[\s]*$"
p3 = "\<[c]*[l]*init\>\([a-zA-Z\$\_0-9\[\]\.\,\s]*\)"
p4 = "catch\s"
p5 = "/\*[0-9]+\*/"
p6 = "(specialinvoke|staticinvoke|virtualinvoke|interfaceinvoke|dynamicinvoke)\s"
p7 = "throw\s"
p8 = "[a-z']+[a-zA-Z\$0-9]*\([a-zA-Z\$\_0-9\[\]\.\,\s]*\)"
p9 = "\$r[0-9]+"
p10 = "[a-z']+[a-zA-Z0-9\$]*\(.*\)"

# java or other 3rd-party library
global analysis_type
analysis_type = ""

def main():

	start = time.time()
	path = sys.argv[1] # folder where the .jimple files belong to
	path_api_json = sys.argv[2] # where to store the output .json (jdk nodes)
	# API version
	path2 = sys.argv[3] # 8
	analysis_type = sys.argv[4] # java
	read_folder(path, analysis_type)
	traverse_the_graph()
	add_dict_to_JSON(path2, path_api_json, DG)

	end = time.time()
	print("Annoteated JDK call graph building duration: "+str(end-start))

def read_folder(path, analysis_type):
	for subdir, dirs, files in os.walk(path):
		for file in files:
			e = re.search(analysis_type+"\..*\.jimple$", file)
			if e:
				f = subdir + "/" + file
				parse_jimple(f, analysis_type)

# parse .jimple file and build a Graph
# the nodes are the methods and the edges the method calls
def parse_jimple(file, analysis_type):
	method_short_sig = ""
	cl_m = ""
	initial_method = ""
	upd_method = ""
	t_method = ""

	# keep the file (class-not embedded) that current methods belong to
	file_class = re.search(analysis_type+"\..*\.jimple$", file).group()
	fl_class = re.sub(".jimple", "", file_class)

	# Uncomment if embedded classes should be avoided
	#if (re.search("\$", fl_class)):
	#	cl_m = re.sub("\$.*.$", "", fl_class)
	#else:
		# found embedded class
		#cl_m = fl_class

	cl_m = fl_class

	f = open(file)
	lines = f.readlines()
	for l, k in enumerate(lines):
		if (l + 1 < len(lines)):
			# in case of new method signature
			if ((re.search(p1, lines[l]) and re.search(p2, lines[l + 1])) and (re.search(p5, lines[l-1]))):
				method_sig = re.search(p1, lines[l]).group()
				method_short_sig = re.search(p8, method_sig).group()
				method_nm = re.split("\(", method_short_sig)
				upd_method = update_md_args(method_short_sig, analysis_type)
				t_method = cl_m + "." + upd_method
				initial_method = t_method
				if (t_method not in G.nodes()):
					DG.add_node(t_method)
					if (t_method==""):
						print("Found here!")
					# level_0 -> throw new in method body, from intra procedural analysis
					DG.nodes[t_method]['level_0'] = []
					DG.nodes[t_method]['level_1'] = []
					DG.nodes[t_method]['level_2'] = []
			# in case of new constructor? We do not consider it here.
			if re.search(p3, lines[l]) and re.search(p2, lines[l + 1]):
				initial_method = "Constructor"
		'''
		Declared exception in throw new (in method body) in .jimple with code lines is such as:

		specialinvoke $r19.<java.lang.NumberFormatException: void <init>(java.lang.String)>("null");
		/*542*/

        throw $r19;
		'''
		if (l + 3 < len(lines)):
			if re.search(p6, lines[l]) and (re.search(p7, lines[l + 2]) or re.search(p7, lines[l + 3])) and (t_method == initial_method) and (t_method != ""):
				pat1 = ""
				pat2 = ""
				pat3 = ""
				# check in which lines are the right invoke and throw; search for same $r#
				if (re.search(p9, lines[l])):
					pat1 = re.search(p9, lines[l]).group()
				if(re.search(p9, lines[l + 2])):
					pat2 = re.search(p9, lines[l + 2]).group()
				if(re.search(p9, lines[l + 3])):
					pat3 = re.search(p9, lines[l + 3]).group()
				if (pat1 == pat2) or (pat1 == pat3):
					t_exc = re.split("\<", lines[l])
					exc = re.split("\:" , t_exc[1])
					# keep fully qualified exception type
					e_nm = exc[0]
					# exclude particular exception types
					if ((not re.search("(ClassNotFoundException|Throwable|Error)", str(e_nm))) and (re.search("Exception", str(e_nm)))):
						# code line number of exception declared in throw new, i.e.: /*542*/ in the above example
						e_l = re.search(p5, lines[l+1]).group()
						e_l_n = re.search("[0-9]+", e_l).group()
						DG.nodes[t_method]['level_0'].append((e_l_n, e_nm))
		# in case of a method call in the current method
		if re.search(p6, lines[l]) and (t_method == initial_method):
			jmp_1 = re.split("\<", lines[l])
			jmp_2 = re.split("\>", jmp_1[1])
			m_jmp = jmp_2[0]
			n_m_jmp = re.sub('\$', '.', m_jmp)
			if re.search(":", n_m_jmp):
				l_n_m_jmp = re.split("\:", str(n_m_jmp))
				if re.search(p10, n_m_jmp):
					called_method_sig = (re.search(p10, n_m_jmp)).group()
					mthd = l_n_m_jmp[0],".",called_method_sig
					n_mthd = ''.join(mthd)
					# new node for the called method signature
					called_method = update_md_args(n_mthd, analysis_type)
					m_l = re.search(p5, lines[l+1]).group()
					m_l_n = re.search("[0-9]+", m_l).group()
					if (called_method not in DG.nodes()):
						DG.add_node(called_method)
						DG.nodes[called_method]['level_0'] = []
						DG.nodes[called_method]['level_1'] = []
						DG.nodes[called_method]['level_2'] = []
					# new directed edge from the current method to the called method
					DG.add_edge(t_method, called_method)
					if (t_method==""):
						print("Called Found here " + str(f))
					# each edge has as attribute the code line number(s) of the call sites
					# note that a method can intraprocedually call another more than one time
					DG[t_method][called_method]['call-site-line'] = []
					DG[t_method][called_method]['call-site-line'].append(m_l_n)

# For keeping the same as in the following
# android.view.LayoutInflater.createView(java.lang.String, java.lang.String, android.util.AttributeSet)
# android.view.LayoutInflater.createView(java.lang.String, java.lang.String, AttributeSet)
# Also, if there is an arg from an embedded class, change $ to .
# i.e. setOnItemSelectedListener(AdapterView.OnItemSelectedListener)
def update_md_args(method_sig, analysis_type):
	# list for the method signature args
	method_sig_args = []
	# keep only the args of the method
	m_args = re.split("\(", method_sig)
	# split the method args to seek android or java case
	l_args = re.split(",", m_args[1])
	for l, k in enumerate(l_args):
		n_sp = re.sub(" ", "", l_args[l])
		if (re.search(analysis_type, n_sp) and not re.search("\$", n_sp)):
			s_args = re.split("\.", n_sp)
			last_elem = s_args[len(s_args) - 1]
			if (re.search("\)", last_elem)):
				last_part = re.sub("\)", '', last_elem)
				method_sig_args.append(last_part)
			else:
				method_sig_args.append(last_elem)
		elif (re.search(analysis_type, n_sp) and re.search("\$", n_sp)):
			n_eb = re.sub("\$", ".", n_sp)
			s_args = re.split("\.", n_eb)
			last_el1 = s_args[len(s_args) - 1]
			last_el2 = s_args[len(s_args) - 2]
			last_elem = last_el2 + "." + last_el1
			if (re.search("\)", last_elem)):
				last_part = re.sub("\)", '', last_elem)
				method_sig_args.append(last_part)
			else:
				method_sig_args.append(last_elem)
		else:
			if (re.search("\)", n_sp)):
				last_part = re.sub("\)", '', n_sp)
				method_sig_args.append(last_part)
			else:
				method_sig_args.append(n_sp)
	return m_args[0] + "(" + ", ".join(method_sig_args) + ")"

# get the called methods (successors) by each node and their exceptions (throw new) up to depth 3
def traverse_the_graph():
	for nd in DG:
		# level_1
		DG.nodes[nd]['level_1'] = []
		# dictionary for node's successors (including the nd) for inter procedural analysis
		bfs_dict = dict(nx.bfs_successors(DG, nd))
		succ_of_nd = bfs_dict[nd]
		for k, l in enumerate(succ_of_nd):
			call_site_l = ""
			# call sites for a particular called method in a caller's method body
			call_sites_l = []
			call_sites_l = DG.edges[nd, succ_of_nd[k]]['call-site-line']
			for c, d in enumerate(call_sites_l):
				call_site_l = call_sites_l[c]
				# search the levels of the successor
				l_l_exc_l0 = DG.nodes[succ_of_nd[k]]['level_0']
				if (len(l_l_exc_l0) > 0):
					for x, z in enumerate(l_l_exc_l0):
						if ((not re.search("(ClassNotFoundException|Throwable|Error)", str(l_l_exc_l0[x]))) and (re.search("Exception", str(l_l_exc_l0[x])))):
							DG.nodes[nd]['level_1'].append([(call_site_l, succ_of_nd[k]), l_l_exc_l0[x]])
							if (nd==""):
								print("Found")
			# level_2
			DG.nodes[nd]['level_2'] = []
			succ_bfs_dict = dict(nx.bfs_successors(DG, succ_of_nd[k]))
			succ_of_succ = succ_bfs_dict[succ_of_nd[k]]
			for m, n in enumerate(succ_of_succ):
				succ_call_sites_l = []
				succ_call_sites_l = DG.edges[succ_of_nd[k], succ_of_succ[m]]['call-site-line']
				for t, e in enumerate(succ_call_sites_l):
					l_l_exc_l1 = DG.nodes[succ_of_succ[m]]['level_0']
					if (len(l_l_exc_l1) > 0):
						for x, z in enumerate(l_l_exc_l1):
							if ((not re.search("(ClassNotFoundException|Throwable|Error)", str(l_l_exc_l1[x]))) and (re.search("Exception", str(l_l_exc_l1[x])))):
								DG.nodes[nd]['level_2'].append([(call_site_l, succ_of_nd[k]), (succ_call_sites_l[t], succ_of_succ[m]), l_l_exc_l1[x]])
	#print DG.nodes.data()

	'''
	Hypothetical example:
	G.add_node("derive(float)")
	G.nodes["derive(float)"]['level_0'] = [("l2", "Exc1")]
	# getInstance(int, float) has declared in its method body at line l1 Exc1
	# getInstance propagates Exc1 at line l3 in derive's method body where getInstance(int, float) is called
	G.nodes["derive(float)"]['level_1'] = [[("l3", "getInstance(int, float)"), ("l1", "Exc1")]]
	# getInstance(int, float) which is called at line l3 in derive, calls toString at l2 in its body
	# Exc3 is declared as throw new in the body of toString at line l2
	G.nodes["derive(float)"]['level_2'] = [[("l3", "getInstance(int, float)"), ("l2", "toString()"), ("l2", "Exc3")]]
	print G.nodes.data()
	'''

# serialize the call graph
def add_dict_to_JSON(api_version, nodes_json, DG):
	file_name = nodes_json+"/java-"+api_version+'_source_nodes.json'
	with open(file_name, 'w') as fp:
		data = json_graph.node_link_data(DG, attrs=None)
		json.dump(data, fp, indent = 4)

# run main
if __name__ == "__main__":
	main()
