#!/usr/bin/env python

__author___= "Maria Kechagia"
__copyright__= "Copyright 2018"
__license__= "Apache License, Version 2.0"
__email__= "m.kechagiaATtudelft.nl"

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
p1 = "\s[a-zA-Z]+[a-zA-Z\$0-9]*\([a-zA-Z\$\_0-9\[\]\.\,\s]*\)[\s]*(throws)*.*$"
p2 = "[\s]*\{[\s]*$"
# pattern for constructors
p3 = "\<[c]*[l]*init\>\([a-zA-Z\$\_0-9\[\]\.\,\s]*\)"
# patterns for thrown exceptions
p4 = "catch\s"
p6 = "(specialinvoke|staticinvoke|virtualinvoke|interfaceinvoke)\s"
p7 = "throw\s"
p8 = "[a-zA-Z]+[a-zA-Z\$0-9]*\([a-zA-Z\$\_0-9\[\]\.\,\s]*\)"
p9 = "\$r[0-9]+"
p10 = "[a-z]+[a-zA-Z0-9\$]*\(.*\)"
# pattern for catch clause
p12 = "catch.*[\s]+from[\s]+label[0-9]+[\s]+to[\s]+label[0-9]+[\s]+with[\s]+label[0-9]+"
# pattern for new label
p13 = "^[\s]*label[0-9]+\:[\s]*$"
# patterns for cases in a method (lookupswitch or tableswitch)
p14 = "(lookup|table)switch\(\$*[a-zA-Z][0-9]+\)"
# serialization case
p15 = "\s(read|write)Object\([a-zA-Z\$\_0-9\[\]\.\,\s]*\)[\s]*(throws)*.*$"
# method with declared might thrown exception
p16 = "\s[a-zA-Z]+[a-zA-Z\$0-9]*\([a-zA-Z\$\_0-9\[\]\.\,\s]*\)[\s]*(throws).*$"

# folder for .jimple files
global path_app
path_app = sys.argv[1] # "../eRec/apps/jar/"
# folder for JSON files (different API versions)
global path_JSON
path_JSON = sys.argv[2] # "../eRec/api/JSON/"
# folder for JSON files (output from apps)
global path_JSON2
path_JSON2 = sys.argv[3] # "../eRec/apps/JSON/" or $cwd/experiment/project_folder
# version of the API used in the app
global api_version
api_version = sys.argv[4] # e.g. 8 (for Java 8)
# name of the API used in the app
global api_name
api_name = sys.argv[5] # java, apache-commons-lang, etc.

global p11
p11 = "(specialinvoke|staticinvoke|virtualinvoke|interfaceinvoke).*[\<]("+api_name+")\..*\s[a-z]+[a-zA-Z\$0-9]*\([a-zA-Z\$\_0-9\[\]\.\,\s]*\)"

# shaded in jar files; check: https://softwareengineering.stackexchange.com/questions/297276/what-is-a-shaded-java-dependency
# check following

# dict for redirecting the output to .json file
global app_dict_might_thrown_exc
app_dict_might_thrown_exc = {}

# dict for declared exceptions in throws (client app method signature)
global app_throws
app_throws = {}

#global exc_lst_a
#exc_lst_a = []

global defects4j_dict
defects4j_dict = {
					'jfreechart-1.2.0':'jfree',
					'commons-lang-2.3-SNAPSHOT':'lang',
					'commons-lang-2.4-SNAPSHOT':'lang',
					'commons-lang-3.0':'lang3',
					'commons-lang-3.0-SNAPSHOT':'lang',
					'commons-lang3-3.0-SNAPSHOT':'lang',
					'commons-lang3-3.2-SNAPSHOT':'lang',
					'commons-math-1.3-SNAPSHOT':'math',
					'commons-math-2.0-SNAPSHOT':'math',
					'commons-math-2.1-SNAPSHOT':'math',
					'commons-math-2.2-SNAPSHOT':'math',
					'commons-math3-3.1-SNAPSHOT':'math',
					'commons-math3-3.3-SNAPSHOT':'math',
					'commons-math3-3.6.1':'math3',
					'gson-2.8.5':'gson',
					'jfreechart-1.5.0':'jfree',
					'joda-time-2.1.alpha':'joda',
					'joda-time-2.3-SNAPSHOT':'joda',
					'joda-time-2.4-SNAPSHOT':'joda',
					'joda-time-2.10':'joda',
					'neo4j-java-driver-1.6.2':'neo4j',
					'Ektorp-1.5.0':'ektorp',
					'pgjdbc-REL42.2.3':'postgresql',
					'xwiki-commons-job-10.6':'org.xwiki',
					'bcel-6.2':'bcel',
					'shiro-core-1.3.2':'shiro',
					'hamcrest-core-1.3':'hamcrest',
					'commons-cli-1.4':'cli',
					'commons-codec-1.12-SNAPSHOT':'codec',
					'commons-collections4-4.2':'collections4',
					'commons-compress-1.17':'compress',
					'commons-lang3-3.7':'lang3',
					'easymock-3.6':'easymock',
					'javassist-3.23.1-GA':'javassist',
					'jcommander-1.71':'jcommander',
					'jopt-simple-5.0.4':'joptsimple',
					'xwiki-commons-text-13.10':'xwiki',
					'guava-19.0':'google.common',
                                        'jackson-databind-2.9.6':'jackson.databind',
					'natty-0.13':'natty',
				}

global lib_dict
lib_dict = OrderedDict([])

global exc_dict
exc_dict = {}

def main():
	start = time.time()	

	api_path = path_JSON+"java-8_source_exceptions.json"
	lib_dict = decode_json(api_path)
	dict_exc = copy_dictionary(lib_dict)
	exc_path = path_JSON+"exceptions-succ.json"
	exc_dict = decode_json(exc_path)
	# open and parse .jimple files
	read_folder(path_app, api_name, api_version, lib_dict, exc_dict, dict_exc, defects4j_dict)
	#exclude_caught_prop_excps_in_client(lib_dict)
	#print app_dict_might_thrown_exc
	#print app_throws

	end = time.time()
	print("Exception propagation within app duration: "+str(end-start))

# for immutability
def copy_dictionary(lib_dict):
	# new code here DICTIONARY
	dict_exc = {}
	lib_keys = list(lib_dict.keys())

	#print lib_dict
	print("\n")

	for y, t in enumerate(lib_keys):

		node_exc_dict = lib_dict.get(lib_keys[y])
		node_exc_dict_keys = node_exc_dict.keys()

		level_0 = node_exc_dict['level_0']
		copy_level_0 = level_0[:]

		data = {}
		dict_exc.setdefault(lib_keys[y], data)
		data.setdefault('level_0', copy_level_0)

		level_1 = node_exc_dict['level_1']
		copy_level_1 = level_1[:]
		data.setdefault('level_1', copy_level_1)

		level_2 = node_exc_dict['level_2']
		copy_level_2 = level_2[:]
		data.setdefault('level_2', copy_level_2)

		id = node_exc_dict['id']
		data.setdefault('id', id)

	#print dict_exc
	print("\n")
	return dict_exc

def read_folder(path_app, api_name, api_version, lib_dict, exc_dict, dict_exc, defects4j_dict):
	defects4j_dict_keys = list(defects4j_dict.keys())
	app_name = ""
	# list app folders (first level subfolders)
	dir_list = next(os.walk(path_app))[1]
	for k, l in enumerate(dir_list):
		app_name = dir_list[k]
		if ((re.search("^derbyTesting$", app_name)) or (re.search("^asm-3.1$", app_name)) or (re.search("^antlr-3.1.3$", app_name))):
			print("Possible issues with these .jar files ...") # from Dacapo benchmark
			continue
		else:
			print("App name: " + app_name)
			path = path_app + "/" + dir_list[k]
			# search in the files of the app folder
			files = os.listdir(path)
			if ((len(files) > 2) and (api_version != "")):
				# update doc_dict for the currently used API javadoc version (for throws, @throws)
				#doc_dict = read_right_api_version(api_version, True)
				# update sc_dict for the currently used API source code version (for throw new, throws)
				#sc_dict = read_right_api_version(api_version, False)
				# create dictionary with API methods and exceptions from javadoc and the source code
				#doc_dict = {}
				#api_dict = get_doc_sc_api_methods_exc(doc_dict, sc_dict)
				for b, d in enumerate(defects4j_dict_keys):
					if (defects4j_dict_keys[b] == app_name):
						app = defects4j_dict[app_name]
						print(app)
						read_files(files, path, api_version, app, lib_dict, lib_dict, exc_dict, dict_exc)
						check_throws(app_dict_might_thrown_exc, app_throws, exc_dict)
						app_dict_might_thrown_exc_keys = list(app_dict_might_thrown_exc.keys())
						for z, w in enumerate(app_dict_might_thrown_exc_keys):
							call_dict = app_dict_might_thrown_exc[app_dict_might_thrown_exc_keys[z]]
							n_dict = call_dict.get('exception-list')
							if ((len(n_dict["level_0"]) <= 0) and (len(n_dict["level_1"]) <= 0) and (len(n_dict["level_2"]) <= 0)):
								del app_dict_might_thrown_exc[app_dict_might_thrown_exc_keys[z]]
						add_dict_to_JSON(app_dict_might_thrown_exc, app_name)

# decode json files into dictionary
def decode_json(f_json):
	print("json file ", f_json)
	try:
		with open(f_json) as f:
			return json.load(f)
	except ValueError:
		print('Decoding JSON has been failed: ', f_json)

def read_files(files, app_path, ap_version, app_name, api_dict, lib_dict, exc_dict, dict_exc):
	a_type = re.split("-", app_name)
	for f in files:
		# check for libraries included in Soot; keep only files from the app not from 3rd-party libs
		e = (not re.search("^(java)\..*", f)) and (not re.search("(shaded)\..*", f)) and (re.search(str(a_type[0])+".*\.jimple$", f))
		if e:
			j_file = app_path + "/" + f
			#if (re.search("org.apache.commons.compress.archivers.zip.jimple", j_file)):
			parse_jimple(j_file, app_name, api_version, api_dict, lib_dict, exc_dict, dict_exc)
		d = re.search("^(java)\..*", f) and re.search("\.jimple$", f)
		if d:
			l = app_path + "/" + f

# parse current jimple file
def parse_jimple(file, app_name, api_version, api_dict, lib_dict, exc_dict, dict_exc):
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
	total_sig_2 = ""
	is_serial = 1

	# keep the file (class-not embedded) that current methods belongs to
	file_class = re.search(".*\.jimple$", file).group()
	fl_class = re.sub(".jimple", "", file_class)
	#if (re.search("\$", fl_class)):
	#	cl_m = re.sub("\$.*.$", "", fl_class)
	#else:
	cl_m = fl_class

	f = open(file)
	lines = f.readlines()
	for l, k in enumerate(lines):
		print("Current line:" + lines[l])
		# in case of new method signature
		#if ((l + 1 < len(lines)) and re.search(p15, lines[l]) and re.search(p2, lines[l + 1])):
		#	print "Here the method!!!!!!!!" + lines[l]
		#	is_serial = 1
		if ((l + 1 < len(lines)) and not (re.search(p14, lines[l])) and not (re.search(p15, lines[l])) and (re.search(p1, lines[l]) and re.search(p2, lines[l + 1])) and (is_new_level == 0) and (is_method == 0)):
			is_serial = 0
			# check for method with declared exception in signature and update dictionary
			if (re.search(p16, lines[l])):
				print("\n")
				print("Here:", lines[l])
				th_lst = re.split("\s(throws)\s", lines[l])
				th_app = th_lst[2]
				th = re.sub(" ", "", th_app)
				#th = []
				if (re.search("\n",th)):
					th = re.sub("\n", "", th)
				if (re.search(",", th)):
					th = re.split(",", th)
					#print "found!!!"
				#else:
				#	th.append(th1)
					
				#print th
				print(th)
				print(th_lst)
				method_sig = re.search(p1, th_lst[0]).group()
				method_s = re.search(p8, method_sig).group()
				method_nm = re.split("\(", method_s)
				upd_method = update_md_args(method_s)
				t_method = cl_m + "." + method_s
				t_method_1 = cl_m + "." + upd_method
				print("Here is the method!!!!"+t_method)
				cl_m_l = re.split("/", cl_m)
				# keep class, method and signature
				#tmthd = cl_m_l[len(cl_m_l) - 1] + "." + upd_method
				tmthd = cl_m_l[len(cl_m_l) - 1] + "." + method_s
				total_sig = re.sub(" ", "", tmthd)
				total_sig_1 = re.sub("\).+", ")", total_sig)
				total_sig_2 = re.sub("\n", "", total_sig_1)
				print("t_method:",total_sig_2)
				#if isinstance(th, list):
				app_throws.setdefault(total_sig_2, th)
				#else:
				#	app_throws.setdefault(total_sig_2, []).append(th)
				print("Here throws finishes!")

			method_sig = re.search(p1, lines[l]).group()
			method_s = re.search(p8, method_sig).group()
			print(file)
			print("Here we continue: " + method_s)
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
		if ((l + 1 < len(lines)) and (re.search(p13, lines[l])) and (is_method == 1) and (is_serial ==0)):
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
		if ((l + 1 < len(lines)) and (is_new_level == 1) and (is_method == 1) and (is_serial ==0)):
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
					# get relevant exceptions from api_dict
					k_api = api_dict.keys()
					excp_api = []
					if (api_m in k_api):
						excp_api = api_dict.get(api_m)
						if (len(excp_api) > 0):
							class_name = re.split("/",file)
							clazz_name = class_name[len(class_name)-1]
							#print clazz_name
							signature_name = re.sub("jimple", "", clazz_name)
							total_sig = re.sub(" ", "", signature_name+method_sig)
							total_sig_1 = re.sub("\).+", ")", total_sig)
							total_sig_2 = re.sub("\n", "", total_sig_1)
							#print total_sig
							j_file = re.sub("\.jimple", ".java", clazz_name)
							#j_file_1 = "../eRec-v2/apps/jar/app_name/" + j_file
							j_class_list = re.split("\.",j_file)
							j_class = j_class_list[len(j_class_list)-2] + ".java"
							line = str(l_l_no[1])
							exceptions_list = set(excp_api)
							uniq_exc_list = list(exceptions_list)
							# new code here
							lib_keys = list(dict_exc.keys())
							for y, t in enumerate(lib_keys):
								if (api_m == lib_keys[y]):
									libr_exc = dict_exc[api_m]
									if ((len(dict_exc[api_m]['level_0']) > 0) or (len(dict_exc[api_m]['level_1']) > 0) or (len(dict_exc[api_m]['level_2']) > 0)):
										#uniq_exc_list = list(exceptions_list)
										attr = {}
										attr.setdefault("call-site-line", line)
										attr.setdefault("call-site-sig", total_sig_2)
										attr.setdefault("api-method-sig", api_m)
										attr.setdefault("java-file-path", j_class)
										#attr.setdefault("exception-list", str(uniq_exc_list))
										attr.setdefault("exception-list", libr_exc)
										app_dict_might_thrown_exc.setdefault(total_sig_2+"-"+api_m,attr)
							#print app_dict_might_thrown_exc
							#print "API call: " + " : " + str(l_l_no[1]) + " : " + api_m + " : " + total_sig_1 + " : " + j_class + " : " + str(excp_api)
							#print app_dict_might_thrown_exc
							#print "API call: " + " : " + str(l_l_no[1]) + " : " + api_m + " : " + total_sig_1 + " : " + j_class + " : " + str(excp_api)
			# check if in the next line exists a new label
			if (re.search(p13, lines[l + 1])):
				is_new_level = 0
		# in case of new line and throw in the current level
		if ((l + 2 < len(lines)) and (is_new_level == 1) and (is_method == 1) and (is_serial ==0)):
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
		if ((l + 1 < len(lines)) and (catch_ptrn) and (is_method == 1) and (is_serial ==0)):
			print("found catch!")
			new_catch = catch_ptrn.group()
			# initialize dictionary for new_catch (as it was for a new label!)
			attributes = {}
			#attributes.setdefault("lines", [])
			attributes.setdefault("api_methods", [])
			attributes.setdefault("exceptions", [])
			m_dict.setdefault(new_catch, attributes)
			#attributes.setdefault("lines", []).append(lines[l])
			print("first new current line"+lines[l])
			locate_labels_in_catch(lines[l], m_dict, attributes)
			print("new current line"+lines[l])
		# in case of a new method
		if (l + 2 < len(lines)) and not (re.search(p14, lines[l + 1])) and not (re.search(p15, lines[l + 1])) and (is_method == 1) and (re.search(p1, lines[l + 1]) and re.search(p2, lines[l + 2]) and (is_serial ==0)):
			print("\nOKKK: " + tmthd + " " + str(m_dict))
			m_catch_dict = m_dict
			class_name = re.split("/",file)
			clazz_name = class_name[len(class_name)-1]
			#print clazz_name
			signature_name = re.sub("jimple", "", clazz_name)
			total_sig = re.sub(" ", "", signature_name+method_sig)
			total_sig_1 = re.sub("\).+", ")", total_sig)
			total_sig_2 = re.sub("\n", "", total_sig_1)
			#print "\n"
			#print "initial_method: " + initial_method
			#print "total_sig_2: " + update_md_args(initial_method)
			#print "\n"
			# apply set operations on methods from the API and from the .apk files
			app_dict.setdefault(total_sig_2, m_dict)
			apply_set_operations(total_sig_2, m_dict, lib_dict, app_name, api_version, exc_dict, dict_exc)
			#print app_dict
			m_dict = {}
			is_method = 0
			is_new_level = 0
			total_sig_2 = 0
			is_serial = 0
		# in case of lookupswitch
		if (l + 2 < len(lines)) and (re.search(p14, lines[l]) and (is_serial ==0)):
			continue
		if (l + 2 < len(lines)) and (re.search(p15, lines[l]) and (is_serial ==0)):
			is_serial = 1
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
	print("current m_dict: "+str(m_dict))
	# list for the labels in catch (e.g. catch java.lang.Throwable from label1 to label2 with label3;)
	labels_lst = []
	# keys (labels) from dictionary
	m_dict_keys = m_dict.keys()
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
			print("labels lst: " + str(labels_lst))
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
		elif ((m_dict_keys[k] == labels_lst[1]) or (labels_lst[0] == labels_lst[1]))  and (state == 1):
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
	#app_name = "jfree"
	#file_name = path_JSON2 + "/" + app_name + ".json"
	file_name = path_JSON2 + "/erec.json"
	with open(file_name, 'w') as fp:
		json.dump(app_dict_might_thrown_exc, fp, indent = 4)

def exclude_caught_prop_excps_in_client(lib_dict):
	#print app_dict_might_thrown_exc
	app_keys = list(app_dict.keys())

	#tmthd = "java.time.Duration.parseNumber(CharSequence, String, int, String)"
	#m_dict = app_dict[tmthd]

	#apply_set_operations(tmthd, m_dict, lib_dict, api_name, api_version)
	for k, l in enumerate(app_keys):
		tmthd = app_keys[k]
		m_dict = app_dict[tmthd]
		apply_set_operations(tmthd, m_dict, lib_dict, api_name, api_version, dict_exc)

# compare API methods and exceptions between app_dict and lib_dict_dict
def apply_set_operations(tmthd, m_dict, lib_dict, app_name, api_ver, exc_dict, dict_exc):
	# get values from dictionary for catch label attributes
	m_dict_keys = list(m_dict.keys())
	for k, l in enumerate(m_dict_keys):
		if (re.search("(catch).*", m_dict_keys[k])):
			attributes = m_dict.get(m_dict_keys[k])
			api_mthd = attributes.get('api_methods')
			excp = attributes.get('exceptions')
			# check if the apis in try-catch exist in the lib dict with the might-thrown exceptions
			lib_dict_keys = list(lib_dict.keys())
			for d, c in enumerate(lib_dict_keys):
				lib_method = lib_dict_keys[d]
				node_dict = lib_dict[lib_method]
				# I THINK THAT FOR LEVEL 0 WE DON'T NEED TO CHECK THE lib_method -> fix that if it is needed!!!
				if (lib_method in api_mthd) and ((len(node_dict['level_0']) > 0) or (len(node_dict['level_1']) > 0) or (len(node_dict['level_2']) > 0)):
				#if (lib_method in api_mthd) and ((len(node_dict['level_0']) > 0) or (len(node_dict['level_1']) > 0) or (len(node_dict['level_2']) > 0)):
					call = tmthd + "-" + lib_method
					if (call in app_dict_might_thrown_exc.keys()):
						call_dict = app_dict_might_thrown_exc[call]
						n_dict = call_dict.get('exception-list')
						if (len(n_dict["level_0"]) > 0):
							n_dict_0 = n_dict["level_0"]
							list_orig = copy.deepcopy(n_dict_0)
							#list_orig = n_dict_0[:]
							for j, g in enumerate(list_orig):
								exc_line = list_orig[j]
								exc = exc_line[1]
								exc_keys = exc_dict.keys()
								exc_parents = set(exc_dict[exc])
								comm_exc = exc_parents.intersection(set(excp))
								print("Common exc ", comm_exc)
								if (((lib_method in api_mthd) and (len(comm_exc) > 0)) or ((lib_method in api_mthd) and ("java.lang.Exception" in excp))):
									print("Old node 0: " + str(node_dict) + "\n")
									print("Old call 0: " + str(app_dict_might_thrown_exc[call]) + "\n")
									print("App method and catch: " + tmthd + str(m_dict) + "\n")
									print("Removed level entry: " + str(list_orig[j]) + "\n")
									n_dict_0.remove(list_orig[j])
									print("New call 0: " + str(app_dict_might_thrown_exc[call]) + "\n")
									print("New node 0: " + str(node_dict) + "\n")
						# thrown exception from API call (exception declared with _throw new_ in the called method's body)
						if (len(n_dict["level_1"]) > 0):
							list_orig = copy.deepcopy(n_dict["level_1"])
							for j, g in enumerate(list_orig):
								api_call = list_orig[j]
								api_line = api_call[0]
								exc_line = api_call[1]
								api = api_line[1]
								exc = exc_line[1]
								print("Client method and exceptions: " + tmthd + str(m_dict) + "\n")
								print("Lib api and exc" + api + " " + exc + "\n")
								print("Node 1: " + str(node_dict) + "\n")
								exc_keys = exc_dict.keys()
								exc_parents = set(exc_dict[exc])
								comm_exc = exc_parents.intersection(set(excp))
								if (((lib_method in api_mthd) and (len(comm_exc) > 0)) or ((lib_method in api_mthd) and ("java.lang.Exception" in excp))):
									print("Found api and exception!!!")
									print("Found api and exception!!!")
									print("Old node 1: " + str(node_dict))
									call = str(tmthd) + "-" + str(lib_method)
									#print app_dict_might_thrown_exc
									call_dict = app_dict_might_thrown_exc[call]
									n_dict = call_dict['exception-list']
									n_dict["level_1"].remove(list_orig[j])
									#node_dict["level_1"].remove(list_orig[j])
									print(tmthd + str(m_dict) + "\n")
									print("Removed 1: " + str(list_orig[j]) + "\n")
									print("New node 1: " + str(node_dict) + "\n")
						# propagated exceptions via the called method
						if (len(n_dict["level_2"]) > 0):
							list_orig = copy.deepcopy(n_dict["level_2"])
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
								exc_parents = set(exc_dict[exc])
								comm_exc = exc_parents.intersection(set(excp))
								if (((lib_method in api_mthd) and (len(comm_exc) > 0)) or ((lib_method in api_mthd) and ("java.lang.Exception" in excp))):
									print("Found api and exception!!!")
									print("Old node 2: " + str(node_dict) + "\n")
									print("Found api and exception!!!")
									print("Old node 1: " + str(node_dict))
									n_dict["level_2"].remove(list_orig[l])
									#node_dict["level_2"].remove(list_orig[l])
									print(tmthd + str(m_dict) + "\n")
									print("Removed 2: " + str(list_orig[l]))
									print("New node 2: " + str(node_dict) + "\n")
						if ((len(n_dict["level_0"]) <= 0) and (len(n_dict["level_1"]) <= 0) and (len(n_dict["level_2"]) <= 0)):
							del app_dict_might_thrown_exc[call]

def check_throws(app_dict_might_thrown_exc, app_throws, exc_dict):
	exc_lst_a_g = []
	app_might_thrown_keys = list(app_dict_might_thrown_exc.keys())
	app_throws_keys = list(app_throws.keys())
	for k, l in enumerate(app_might_thrown_keys):
		#print app_might_thrown_keys[k]
		call_dict = app_dict_might_thrown_exc[app_might_thrown_keys[k]]
		n_dict = call_dict.get('exception-list')
		call_site_sig = call_dict.get('call-site-sig')
		# check if the client method is in the dictionary with the declared exceptions (throws)
		print("\n")
		print("Call site for throws: "+str(call_site_sig))
		print("n_dict: "+str(n_dict))
		#print "List for app throws: "+str(app_throws)
		print("\n")
		if (call_site_sig in app_throws_keys):
			print("Common methods")
			# get the (declared) exceptions (value) of this method
			print("Get throws from app throws: "+str(app_throws.get(call_site_sig)))
			exc_lst_a = app_throws.get(call_site_sig)
			#exc_lst_a = []
			#if isinstance(app_throws.get(call_site_sig), list):
			#	exc_lst_a = app_throws.get(call_site_sig)
			#	print "Throws: "+str(exc_lst_a)
			#else:
			#	exc_lst_a = []
			#	exc_lst_a.append(app_throws.get(call_site_sig))
			#	print "Throws: "+str(exc_lst_a)
			if (len(n_dict["level_0"]) > 0):
				n_dict_0 = n_dict["level_0"]
				list_orig = copy.deepcopy(n_dict_0)
				for j, g in enumerate(list_orig):
					exc_line = list_orig[j]
					exc = exc_line[1]
					exc_keys = exc_dict.keys()
					# get the parents of the exception
					exc_parents = set(exc_dict[exc])
					# intersection of the set from the exceptions hierarchy and the list of app_throws
					comm_exc = exc_parents.intersection(set(exc_lst_a))
					if (exc in exc_lst_a) or ("java.lang.Exception" in exc_lst_a) or (len(comm_exc) > 0):
						print("Exception to remove:"+str(list_orig[j])+" for "+str(call_site_sig))
						n_dict_0.remove(list_orig[j])
			if (len(n_dict["level_1"]) > 0):
				list_orig = copy.deepcopy(n_dict["level_1"])
				print(list_orig)
				for j, g in enumerate(list_orig):
					api_call = list_orig[j]
					api_line = api_call[0]
					exc_line = api_call[1]
					api = api_line[1]
					exc = exc_line[1]
					exc_keys = exc_dict.keys()
					#exc_parents = Set(map(str, exc_dict[exc]))
					exc_parents = set(exc_dict[exc])
					print(str(call_site_sig))
					print(exc_parents)
					#exc_lst_a_1 = []
					#if not isinstance(exc_lst_a, list):
					#	exc_lst_a_1.append(exc_lst_a)
					#	exc_lst_a_g=exc_lst_a_1
					#else:
					#	exc_lst_a_g=exc_lst_a
					print("exc list: "+str(exc_lst_a))
					#exc_lst_a = []
					#exc_lst_a.append(exc_lst_a)
					#exc_lst_a_g=exc_lst_a_1
					if isinstance(exc_lst_a, list):
						print(set(exc_lst_a))
						comm_exc = exc_parents.intersection(set(exc_lst_a))
						print("Common exc: "+str(comm_exc))
						if (exc in exc_lst_a) or ("java.lang.Exception" in exc_lst_a) or (len(comm_exc) > 0):
							print("Exception to remove:"+str(list_orig[j])+" for "+str(api))
							n_dict["level_1"].remove(list_orig[j])
					else:
						print(exc_lst_a)
						if (exc_lst_a in list(exc_parents)):
							print("Common exc: "+str(exc_lst_a))
							if (exc == exc_lst_a) or ("java.lang.Exception" == exc_lst_a) or (exc_lst_a in list(exc_parents)):
																											print("Exception to remove:"+str(list_orig[j])+" for "+str(api))
																											n_dict["level_1"].remove(list_orig[j])
			# propagated exceptions via the called method
			if (len(n_dict["level_2"]) > 0):
				list_orig = copy.deepcopy(n_dict["level_2"])
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
					exc_parents = set(exc_dict[exc])
					comm_exc = exc_parents.intersection(set(exc_lst_a))
					if (exc in exc_lst_a) or ("java.lang.Exception" in exc_lst_a) or (len(comm_exc) > 0):
						print("Exception to remove:"+str(list_orig[l])+" for "+str(caller))
						n_dict["level_2"].remove(list_orig[l])
			if ((len(n_dict["level_0"]) <= 0) and (len(n_dict["level_1"]) <= 0) and (len(n_dict["level_2"]) <= 0)):
					del app_dict_might_thrown_exc[app_might_thrown_keys[k]]

# run main
if __name__ == "__main__":
	main()
