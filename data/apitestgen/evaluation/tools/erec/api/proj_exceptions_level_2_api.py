#!/usr/bin/env python

__author___= "Maria Kechagia"
__copyright__= "Copyright 2018"
__license__= "Apache License, Version 2.0"
__email__= "m.kechagiaATtudelft.nl"

'''
This script precisely finds the might thrown exceptions
for each Java API method.
'''

import re
import os
import json
import sys
import copy
import time

from collections import defaultdict
from collections import OrderedDict

# API methods and exceptions from .jar file (caller method)
global app_dict
app_dict = OrderedDict([])

# patterns for finding method signatures
p1 = "\s[a-z']+[a-zA-Z\$0-9]*\([a-zA-Z\$\_0-9\[\]\.\,\s]*\)[\s]*(throws)*.*$"
p2 = "[\s]*\{[\s]*$"
# pattern for constructors
p3 = "\<[c]*[l]*init\>\([a-zA-Z\$\_0-9\[\]\.\,\s]*\)"
# patterns for thrown exceptions
p4 = "catch\s"
p6 = "(specialinvoke|staticinvoke|virtualinvoke|interfaceinvoke)\s" # to-do: dynamicinvoke
p7 = "throw\s"
p8 = "[a-z']+[a-zA-Z\$0-9]*\([a-zA-Z\$\_0-9\[\]\.\,\s]*\)"
p9 = "\$r[0-9]+"
p10 = "[a-z']+[a-zA-Z0-9\$]*\(.*\)"
# pattern for catch clause
p12 = "catch.*[\s]+from[\s]+label[0-9]+[\s]+to[\s]+label[0-9]+[\s]+with[\s]+label[0-9]+"
# pattern for new label
p13 = "^[\s]*label[0-9]+\:[\s]*$"
# patterns for cases in a method (lookupswitch or tableswitch)
p14 = "(lookup|table)switch\(\$*[a-zA-Z][0-9]+\)"

# folder for .jimple files
global path_app
path_app = sys.argv[1] # "../eRec/apps/jar/"
# folder for JSON files (different API versions)
global path_JSON
path_JSON = sys.argv[2] # "../experiment/$FILE/"
# version of the API used in the app
global api_version
api_version = sys.argv[3] # e.g. 8 (for Java 8)
# name of the API used in the app
global api_name
api_name = sys.argv[4] # java, apache-commons-lang, etc.

global p11
p11 = "(specialinvoke|staticinvoke|virtualinvoke|interfaceinvoke).*[\<]("+api_name+")\..*\s[a-z']+[a-zA-Z\$0-9]*\([a-zA-Z\$\_0-9\[\]\.\,\s]*\)" # todo: dynamicinvoke

global app_dict_might_thrown_exc
app_dict_might_thrown_exc = {}

global lib_dict
lib_dict = OrderedDict([])

global exc_dict
exc_dict = {}

def main():
	start = time.time()

	# exceptions hierarchy for the APIs used by the client project
	exc_path = path_JSON+"exceptions-succ.json"
	# decode json file with exceptions into dictionary
	exc_dict = decode_json(exc_path)
	# nodes (methods) of the API used by the client project
	api_path = path_JSON+"java-8_source_nodes.json"
	# decode json file with nodes into dictionary
	lib_dict = parse_api_nodes(api_path)
	# open and parse .jimple files
	read_folder(path_app, api_name, api_version, lib_dict)
	exclude_caught_prop_excps_in_jdk(exc_dict)
	file_name = path_JSON + "java-8_source_exceptions.json"
	with open(file_name, 'w') as fp:
		json.dump(lib_dict, fp, indent = 4)

		end = time.time()
		print("Exception propagation duration: "+str(end-start))

def parse_api_nodes(nodes_path):
	graph_dict = decode_json(nodes_path)
	nodes_list =  graph_dict['nodes']
	for s, t in enumerate(nodes_list):
		# each node is a dictionary
		node_dict= nodes_list[s]
		node_name = node_dict['id']
		lib_keys = lib_dict.keys()
		if (node_name not in lib_keys):
			lib_dict.setdefault(node_name, node_dict)
		else:
			print(str(node_name) + " is already in the library dictionary.")
	return lib_dict

def read_folder(path_app, api_name, api_version, api_dict):
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
				read_files(files, path, api_version, app_name, api_dict)

def decode_json(f_json):
	try:
		with open(f_json) as f:
			return json.load(f)
	except ValueError:
		print('Decoding JSON has been failed: ', f_json)

def read_files(files, app_path, ap_version, app_name, api_dict):
	for f in files:
		e = re.search("^(java)\..*\.jimple$", f) # We exclude sun e.g. sun.util.logging.PlatformLogger: void fine and javax
		if e:
			j_file = app_path + "/" + f
			parse_jimple(j_file, "java", api_version, api_dict)

# parse current jimple file
def parse_jimple(file, app_name, api_version, api_dict):
	# flag for a new method
	is_method = 0
	# class where the method belongs to
	cl_m = ""
	# total method with class
	t_method = ""
	# keep the current method (including the class)
	initial_method = ""
	# method's dictionary (label: lines, API methods, exceptions)
	m_dict = OrderedDict([])
	# method's subdictionary (one dict per label -see above)
	attributes = {}
	# for a new label block
	is_new_level = 0
	# new label's name
	new_label = ""
	# flag for a new label
	is_label = 0

	# keep the file (class-not embedded) that current methods belongs to
	file_class = re.search(".*\.jimple$", file).group()
	fl_class = re.sub(".jimple", "", file_class)

	# Uncomment to exclude subclasses
	#if (re.search("\$", fl_class)):
	#	cl_m = re.sub("\$.*.$", "", fl_class)
	#else:
	cl_m = fl_class

	cl_m = fl_class

	f = open(file)
	lines = f.readlines()
	for l, k in enumerate(lines):
		# in case of new method signature
		if ((l + 1 < len(lines)) and not (re.search(p14, lines[l])) and (re.search(p1, lines[l]) and re.search(p2, lines[l + 1])) and (is_new_level == 0) and (is_method == 0)):
			method_sig = re.search(p1, lines[l]).group()
			method_s = re.search(p8, method_sig).group()
			method_nm = re.split("\(", method_s)
			upd_method = update_md_args(method_s)
			t_method = cl_m + "." + upd_method
			# keep only method and cut the previous path
			cl_m_l = re.split("/", cl_m)
			# keep class, method and signature
			tmthd = cl_m_l[len(cl_m_l) - 1] + "." + upd_method
			initial_method = tmthd
			# change flag to indicate the existance of a new method signature
			is_method = 1
			# update dictionary of the application -> add new dictionary for a new method
			#app_dict.setdefault(initial_method, m_dict)
			# new dictionary for the current method -> intialize dict
			m_dict = OrderedDict([])
			# change flag for new label to 0
			is_new_level = 0
			# not known label name yet
			new_label = ""
			# get a subset of the lines in the current jimple file
			lines_l = lines[l:]
			# in case of there is not any label in the current method
			if (is_exist_label(lines_l, is_method) == False):
				# change flag to show that we are in a new level - key -block
				is_new_level = 1
				# define that we haven't got a new label
				new_label = "withoutLabel"
				# add the new label as key in the current method dictionary
				# subdictionary for m_dict
				attributes = {}
				#attributes.setdefault("lines", [])
				attributes.setdefault("api_methods", [])
				attributes.setdefault("exceptions", [])
				m_dict.setdefault(new_label, attributes)
		# in case of a new label, add new label -key in method dictionary
		if ((l + 1 < len(lines)) and (re.search(p13, lines[l])) and (is_method == 1)):
			# in case of a new label, add new label - key in method dictionary
			label_ptrn = re.search(p13, lines[l])
			# change flag to show that we are in a new label - key -block
			is_new_level = 1
			# define the new label's name
			new_label_1 = label_ptrn.group()
			new_label_2 = re.sub("\:\n", "", new_label_1)
			new_label_3 = re.sub("[\s]+", " ", new_label_2)
			new_label_lst = re.split(" ", new_label_3)
			new_label = new_label_lst[1]
			# add the new label as key in the current method dictionary, initializing label's attributes first
			attributes = {}
			#attributes.setdefault("lines", [])
			attributes.setdefault("api_methods", [])
			attributes.setdefault("exceptions", [])
			m_dict.setdefault(new_label, attributes)
		# in case of new line in the current level
		if ((l + 1 < len(lines)) and (is_new_level == 1) and (is_method == 1)):
			# add values (lines) to the current label -key
			#attributes.setdefault("lines", []).append(lines[l])
			# check if in the current line there exists an API method
			if (re.search(p11, lines[l])):
				#print file, " ", method_sig, " ",lines[l]
				api_m = isolate_api_method(lines[l])
				attributes.setdefault("api_methods", []).append(api_m)
				#print api_m
				#if (re.search("/\*[0-9]+\*/", lines[l-3])):
					#l_l_no = re.split("\*", lines[l-3])
				if (re.search("/\*[0-9]+\*/", lines[l+1])):
					l_l_no = re.split("\*", lines[l+1])
					k_api = api_dict.keys()
					excp_api = []
					if (api_m in k_api):
						excp_api = api_dict.get(api_m)
						#if (len(excp_api) > 0):
						class_name = re.split("/",file)
						clazz_name = class_name[len(class_name)-1]
						#print clazz_name
						signature_name = re.sub("jimple", "", clazz_name)
						total_sig = re.sub(" ", "", signature_name+method_sig)
						total_sig_1 = re.sub("\).+", ")", total_sig)
						total_sig_2 = re.sub("\n", "", total_sig_1)
						#print total_sig
						j_file = re.sub("\.jimple", ".java", clazz_name)
						j_class_list = re.split("\.",j_file)
						j_class = j_class_list[len(j_class_list)-2] + ".java"
						line = str(l_l_no[1])
						exceptions_list = set(excp_api)
						uniq_exc_list = list(exceptions_list)
						attr = {}
						attr.setdefault("call-site-line", line)
						attr.setdefault("call-site-sig", total_sig_2)
						attr.setdefault("api-method-sig", api_m)
						attr.setdefault("java-file-path", j_class)
						#attr.setdefault("exception-list", str(uniq_exc_list))
						app_dict_might_thrown_exc.setdefault(total_sig_2+"-"+api_m,attr)
							#print app_dict_might_thrown_exc
							#print "API call: " + " : " + str(l_l_no[1]) + " : " + api_m + " : " + total_sig_1 + " : " + j_class + " : " + str(excp_api)
			# check if in the next line exists a new label
			if (re.search(p13, lines[l + 1])):
				is_new_level = 0
		# in case of new line and throw in the current level
		if ((l + 2 < len(lines)) and (is_new_level == 1) and (is_method == 1)):
			# exception patterns according to a jimple file (see a jimple file for example)
			thr_exc = re.search(p6, lines[l]) and (re.search(p7, lines[l + 1]) or re.search(p7, lines[l + 2])) and (t_method == initial_method) and (t_method != "")
			if (thr_exc):
				pat1 = ""
				pat2 = ""
				pat3 = ""
				# check in which lines are the right specialinvoke and throw
				if (re.search(p9, lines[l])):
					pat1 = re.search(p9, lines[l]).group()
				if(re.search(p9, lines[l + 1])):
					pat2 = re.search(p9, lines[l + 1]).group()
				if(re.search(p9, lines[l + 2])):
					pat3 = re.search(p9, lines[l + 2]).group()
				if (pat1 == pat2) or (pat1 == pat3):
					t_exc = re.split("\<", lines[l])
					exc = re.split("\:" , t_exc[1])
					#e_nm = keep_exc_name(exc[0])
					e_nm = exc[0]
					# exclude Throwable found from Soot
					if (e_nm != "Throwable"):
						# add values (lines) to the current label - key
						#attributes.setdefault("lines", []).append("exc."+e_nm)
						attributes.setdefault("exceptions", []).append(e_nm)
				# check for a new label in the next line
				if (re.search(p13, lines[l + 1])):
					# initialize variable for the next new label
					is_new_level = 0
		# in case of exceptions (catch clause in jimple file)
		catch_ptrn = re.search(p12, lines[l])
		if ((l + 1 < len(lines)) and (catch_ptrn) and (is_method == 1)):
			#print "found catch!"
			new_catch = catch_ptrn.group()
			# initialize dictionary for new_catch (as it was for a new label!)
			attributes = {}
			#attributes.setdefault("lines", [])
			attributes.setdefault("api_methods", [])
			attributes.setdefault("exceptions", [])
			m_dict.setdefault(new_catch, attributes)
			#attributes.setdefault("lines", []).append(lines[l])
			locate_labels_in_catch(lines[l], m_dict, attributes)
			#print lines[l]
		# in case of a new method
		if (l + 2 < len(lines)) and not (re.search(p14, lines[l + 1])) and (is_method == 1) and (re.search(p1, lines[l + 1]) and re.search(p2, lines[l + 2])):
			m_catch_dict = m_dict
			# apply set operations on methods from the API and from the .apk files
			app_dict.setdefault(initial_method, m_dict)
			#apply_set_operations(tmthd, m_dict, lib_dict, app_name, api_version)
			#print app_dict
			m_dict = {}
			is_method = 0
			is_new_level = 0
		# in case of lookupswitch
		if (l + 2 < len(lines)) and (re.search(p14, lines[l])):
			continue

# For keeping the same as in the following
# android.view.LayoutInflater.createView(java.lang.String, java.lang.String, android.util.AttributeSet)
# android.view.LayoutInflater.createView(java.lang.String, java.lang.String, AttributeSet)
# Also, if there is an arg from an embedded class, change $ to .
# i.e. setOnItemSelectedListener(AdapterView.OnItemSelectedListener)
def update_md_args(method_sig):
	# list for the method signature args
	method_sig_args = []
	# keep only the args of the method
	m_args = re.split("\(", method_sig)
	# split the method args to seek android or java case
	l_args = re.split(",", m_args[1])
	for l, k in enumerate(l_args):
		n_sp = re.sub(" ", "", l_args[l])
		if (re.search("java", n_sp) and not re.search("\$", n_sp)):
			s_args = re.split("\.", n_sp)
			last_elem = s_args[len(s_args) - 1]
			if (re.search("\)", last_elem)):
				last_part = re.sub("\)", '', last_elem)
				method_sig_args.append(last_part)
			else:
				method_sig_args.append(last_elem)
		elif (re.search("java", n_sp) and re.search("\$", n_sp)):
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

# search if there exists a label in the current method
def is_exist_label(lines, is_method):
	label = False
	for l, k in enumerate(lines):
		# there exists at least one label
		if ((l + 1 < len(lines)) and (re.search(p13, lines[l]))):
			label = True
			break
		# next new method
		#if (l + 2 < len(lines)) and (re.search(p1, lines[l + 1]) and re.search(p2, lines[l + 2])):
		if (l + 2 < len(lines)) and not (re.search(p14, lines[l + 1])) and (is_method == 1) and (re.search(p1, lines[l + 1]) and re.search(p2, lines[l + 2])):
			break
	return label

# find method calls to the Java API in each app method's body
def isolate_api_method(line):
	new_api_method = ""
	line_spl = re.split("\<", line)
	java_elems = re.split("\:", line_spl[1])
	java_cls = java_elems[0]
	if re.search(p1, java_elems[1]):
		method_elems = re.split("\>", re.search(p1, java_elems[1]).group())
		java_method = re.sub(" ", "", method_elems[0])
		java_mthd_cls = java_cls + "." + java_method
		new_api_method = update_md_args(java_mthd_cls)
		#print "\n*API method* ", new_api_method, "\n"
		return new_api_method

# keep only exception names (e.g. java.lang.IllegalArgumentException -> IllegalArgumentException)
# do not keep embedded exception (e.g. IntentSender$SendIntentException -> IntentSender.SendIntentException)
def keep_exc_name(exc):
	# for case java.lang.IllegalArgumentException
	if re.search("\.", exc):
		e_nm = re.split("\.", exc)
		l_elem = e_nm[len(e_nm) - 1]
		# for case IntentSender$SendIntentException
		if re.search("\$", l_elem):
			n_emb = re.split("\$", l_elem)
			#n_emb = re.sub("\$", ".", l_elem)
			return n_emb[1]
		else:
			return l_elem
	# for case IllegalArgumentException (there is not java.lang)
	else:
		return exc

# find labels, API methods, and exceptions and add them in catch's dictionary accordingly
def locate_labels_in_catch(line, m_dict, attributes):
	# list for the labels in catch (e.g. catch java.lang.Throwable from label1 to label2 with label3;)
	labels_lst = []
	# keys (labels) from dictionary
	m_dict_keys = list(m_dict.keys())
	# states for labels
	state = 0
	# last label to search for new exceptions
	last_label = ""
	# list of actual labels (in case for instance we have from label 2 to label 4 with label 2)
	actual_labels_lst = []

	# split catch
	catch_elem = re.split("[\s]+", line)
	# get the exception (referred in the catch clause -jimple file)
	exc = catch_elem[2]
	for c, e in enumerate(catch_elem):
		ptrn_l = re.search("label[0-9]+", catch_elem[c])
		# search for label in catch statement
		if (ptrn_l):
			ptrn = ptrn_l.group()
			labels_lst.append(ptrn)
	# search for the labels and their attributes in the current method's dictionary
	for k, l in enumerate(m_dict_keys):
		# "first " label in catch
		if (m_dict_keys[k] == labels_lst[0]) and (state == 0):
			state = 1
			actual_labels_lst.append(m_dict_keys[k])
			# get api methods from current label and add them in the catch dictionary
			api_mthds = get_label_api_methods(m_dict_keys[k], m_dict)
			for j, g in enumerate(api_mthds):
				attributes.setdefault("api_methods", []).append(api_mthds[j])
		# "next " label in catch
		elif (m_dict_keys[k] not in labels_lst) and (state == 1):
			actual_labels_lst.append(m_dict_keys[k])
			# get api methods from current label and add them in the catch dictionary
			api_mthds = get_label_api_methods(m_dict_keys[k], m_dict)
			for j, g in enumerate(api_mthds):
				attributes.setdefault("api_methods", []).append(api_mthds[j])
		# "second  " label in catch
		elif (m_dict_keys[k] == labels_lst[1]) and (state == 1):
			state = 2
			actual_labels_lst.append(m_dict_keys[k])
			# get api methods from current label and add them in the catch dictionary
			api_mthds = get_label_api_methods(m_dict_keys[k], m_dict)
			for j, g in enumerate(api_mthds):
				attributes.setdefault("api_methods", []).append(api_mthds[j])
		# "third " label in catch
		elif (m_dict_keys[k] == labels_lst[2]) and (state == 2):
			state = 0
			actual_labels_lst.append(m_dict_keys[k])
			exc = get_label_exception(labels_lst[2], m_dict, exc)
			# update exceptions of the current catch clause
			for j, g in enumerate(exc):
				attributes.setdefault("exceptions", []).append(exc[j])
		# "third " label in catch
		elif (labels_lst[2] in m_dict_keys) and (state == 2):
			state = 0
			actual_labels_lst.append(labels_lst[2])
			exc = get_label_exception(labels_lst[2], m_dict, exc)
			for j, g in enumerate(exc):
				attributes.setdefault("exceptions", []).append(exc[j])

# check if there is an exception in the current label
def get_label_exception(label, m_dict, e):
	exc = []
	exc.append(e)
	# get the exceptions of the third label
	attr = m_dict.get(label)
	label_exceptions = attr.get("exceptions")
	if (len(label_exceptions) > 0):
		for l, b in enumerate(label_exceptions):
			# add found exceptions in the list of catch exceptions
			exc.append(label_exceptions[l])
	return exc

# check if there is an API method in the current label
def get_label_api_methods(label, m_dict):
	api_methds = []
	# get the API methods from the current label
	attributes = m_dict.get(label)
	label_api_methods = attributes.get("api_methods")
	if (len(label_api_methods) > 0):
		api_methds = label_api_methods
	return api_methds

def add_dict_to_JSON(app_dict_might_thrown_exc, app_name):
	file_name = path_JSON + app_name + ".json"
	with open(file_name, 'w') as fp:
		json.dump(app_dict_might_thrown_exc, fp, indent = 4)

def exclude_caught_prop_excps_in_jdk(exc_dict):
	app_keys = list(app_dict.keys())

	#tmthd = "java.time.Duration.parseNumber(CharSequence, String, int, String)"
	#m_dict = app_dict[tmthd]

	for k, l in enumerate(app_keys):
		tmthd = app_keys[k]
		m_dict = app_dict[tmthd]
		#if (tmthd == 'java.awt.color.ICC_Profile.run()'):
           	# print "Caution, here is the run method from ICC_Profile: "+str(m_dict)
		apply_set_operations(tmthd, m_dict, lib_dict, api_name, api_version, exc_dict)

# compare API methods and exceptions between app_dict and lib_dict_dict
def apply_set_operations(tmthd, m_dict, lib_dict, app_name, api_ver, exc_dict):
	if (list(lib_dict.keys())):
		m_dict_keys = list(m_dict.keys())
		lib_dict_keys = list(lib_dict.keys())
		for k, l in enumerate(m_dict_keys):
			if (re.search("(catch).*", m_dict_keys[k])):
				attributes = m_dict.get(m_dict_keys[k])
				# get values from dictionary for catch label attributes
				api_mthd = attributes.get('api_methods')
				excp = attributes.get('exceptions')
				for d, c in enumerate(lib_dict_keys):
					if (tmthd == lib_dict_keys[d]):
						node_dict = lib_dict[tmthd]
						# thrown exception from API call (exception declared with _throw new_ in the called method's body)
						if (len(node_dict["level_1"]) > 0):
							list_orig = copy.deepcopy(node_dict["level_1"])
							for j, g in enumerate(list_orig):
								api_call = list_orig[j]
								api_line = api_call[0]
								exc_line = api_call[1]
								api = api_line[1]
								exc = exc_line[1]
								exc_keys = exc_dict.keys()
								if (exc in exc_keys):
									exc_parents = set(exc_dict[exc])
									comm_exc = exc_parents.intersection(set(excp))
									#if (api in api_mthd) and (exc in excp):
									if (((api in api_mthd) and (len(comm_exc) > 0)) or ((api in api_mthd) and (exc == "java.lang.Exception"))):
										print("Old node: " + str(node_dict))
										node_dict["level_1"].remove(list_orig[j])
										print(tmthd + str(m_dict) + "\n")
										print("Removed: " + str(list_orig[j]) + "\n")
										print("New node: " + str(node_dict) + "\n")
						# propagated exceptions via the called method
						if (len(node_dict["level_2"]) > 0):
							list_orig = copy.deepcopy(node_dict["level_2"])
							for l, m in enumerate(list_orig):
								api_call = list_orig[l]
								caller_line = api_call[0]
								callee_line = api_call[1]
								exc_line = api_call[2]
								caller = caller_line[1]
								caller_l = caller_line[0]
								callee = callee_line[1]
								exc = exc_line[1]
								exc_keys = exc_dict.keys()
								if (exc in exc_keys):
									exc_parents = set(exc_dict[exc])
									comm_exc = exc_parents.intersection(set(excp))
									#if (caller in api_mthd) and (exc in excp):
									if (((caller in api_mthd) and (len(comm_exc) > 0)) or ((caller in api_mthd) and (exc == "java.lang.Exception"))):
										print("Old node: " + str(node_dict) + "\n")
										node_dict["level_2"].remove(list_orig[l])
										print(tmthd + str(m_dict) + "\n")
										print("Removed: " + str(list_orig[l]))
										print("New node: " + str(node_dict) + "\n")
									# app here we mean all the methods of the analyzed JDK!
									app_keys = list(app_dict.keys())
									# check if the caller (methodB) has the callee (methodC) in try-catch
									if (caller in app_keys):
										caller_dict = app_dict[caller]
										caller_keys = list(caller_dict.keys())
										for r, s in enumerate(caller_keys):
											if (re.search("(catch).*", caller_keys[r])):
												attributes = caller_dict.get(caller_keys[r])
												# get values from dictionary for catch label attributes
												api_mthds = attributes.get('api_methods')
												excps = attributes.get('exceptions')
												comm_excs = exc_parents.intersection(set(excps))
												#if (callee in api_mthds) and (exc in excps):
												if (((callee in api_mthds) and (len(comm_excs) > 0)) or ((callee in api_mthds) and (exc == "java.lang.Exception"))):
													print("Old node 2: " + str(node_dict) + "\n")
													if (list_orig[l] in node_dict["level_2"]):
														print("Old node 2: " + str(node_dict) + "\n")
														node_dict["level_2"].remove(list_orig[l])
														print(caller + str(caller_dict) + "\n")
														print("Removed 2: " + str(list_orig[l]))
														print("New node 2: " + str(node_dict) + "\n")
	else:
		print("API version not available!", api_ver)

# run main
if __name__ == "__main__":
    main()
