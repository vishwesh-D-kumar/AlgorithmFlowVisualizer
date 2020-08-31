from django.shortcuts import render
import os
import sys
from django.http import HttpResponse,HttpResponseRedirect
from .recursion_visualize.stackgen import go
from .variableTrace.variable_trace import go_file
from .flowgen.connect import FlowGen,OutputRecorder
from pprint import pformat,pprint
import json
from texttable import Texttable
# w = go([
#     [1,0],
#     [1,1]

# ], file='/Users/vishweshdkumar/Desktop/gsoc/finalwork/finalrepo/djangotrials/demo_files/demo1.py', func='go')
# file = '/Users/vishweshdkumar/Desktop/gsoc/finalwork/finalrepo/djangotrials/demo_files/demo2.py'
# func = 'go'
# matr =   [  [1,0],
#     [1,1]]
# var_Tracer = go_file(matr, file=file, func=func,include_files = [])
# stack_Tracer = go(matr, file=file, func=func)
# flowchart_generator = FlowGen(file,func,matr)
# flowchart_generator.generate_flowchart('png',True)
# print()
step = 1
to_cutoff = 'flowview/viewer/static'
source_code = []
file_source_code_map = {}

# logging_file = open('var_debug_log.txt','a+')
def dbg(s):
	logging_file.write(s)
def view_flowchart(request):
	step = int(request.GET['step'])
	flowchart_image = flowchart_generator.final_dict[step]['images'].split('viewer/static')[1]
	return render(request,'viewer/view_flowchart.html',
		context={
		'flowchart_image':flowchart_image
		})
def index(request):
	return render(request,'viewer/index.html')
	# pass dict context to pass whatver you want to 
    # return HttpResponse(<pre>"###\n".join(pformat(stack_Tracer.final_dict),pformat(var_Tracer.final_dict),pformat(flowchart_generator.final_dict))</pre>)
def run_tracer(request):
	global step 
	global var_Tracer
	global stack_Tracer
	# global file 
	global func
	global flowchart_generator
	# global source_code
	global output_recorder
	global max_step
	global file_source_code_map
	step = 1
	file = request.POST['file']
	func = request.POST['func']
	config_json = request.POST['config']
	include_files = []
	file_source_code_map = {}
	if config_json:
		with open(config_json,'r+') as f:
			config = json.loads(f.read())
			file = config['file']
			func = config['func']
			include_files = config['include_files']
		# print(source_code)
	# return HttpResponse(source_code)
	# return HttpResponseRedirect('step?step=2')
	file_dir = os.path.dirname(file)
	sys.path.append(file_dir)
	if include_files:
		include_files.append(os.path.abspath(file))
	flowchart_generator = FlowGen(file,func,include_files)
	flowchart_generator.generate_flowchart()
	var_Tracer =  go_file(file= file,func = func,include_files = include_files)
	# return HttpResponse(f'<pre>{pformat(var_Tracer.final_dict)}</pre>')

	stack_Tracer = go(file=file,func = func,include_files=include_files)

	output_recorder  = OutputRecorder(file,func,include_files)
	output_recorder.record_output()
	# return HttpResponse("###<br>".join([str(stack_Tracer.final_dict),str(var_Tracer.final_dict),str(flowchart_generator.final_dict)]))
	curr_line = var_Tracer.final_dict[2]["line"]
	max_step = max(var_Tracer.final_dict.keys())
	return HttpResponseRedirect(f'step?step=2&all_vars=1;mode=1#play.{curr_line}')
	for step in var_Tracer.final_dict:
		var_changes = var_Tracer.final_dict[step]['changes']
		tree_images = var_Tracer.final_dict[step]['images']
		stack_images = stack_Tracer.final_dict[step]['images']
		flowchart_images = flowchart_generator.final_dict[step]

	return render(request,'viewer/steps.html')
	return HttpResponse(f"Path entered is :{file}, func entered is :{func}")
def get_source_code(file):
	if file in file_source_code_map:
		return file_source_code_map[file]
	with open(file,'r+') as f:
		source_code = f.read().split('\n')
		file_source_code_map[file] = source_code
		return source_code
def render_matrices(matr):
	print(matr)
	if len(matr)==0:
		return str(matr)
	max_len = 0
	has_nesting = True
	
	for row in matr:
		if type(row)==list:
			max_len = max(max_len,len(row))
		else:
			has_nesting = False
	table = Texttable(0)
	table.set_chars(['-','|','+','-'])
	

	if not has_nesting:
		table.set_cols_dtype(['t']*(len(matr)))
		table.add_row(matr)
	else:
		table.set_cols_dtype(['t']*(max_len))
		new_matr = []
		for row in matr:
			if len(row)<max_len:
				row.extend(['']*(max_len-len(row)))
			new_matr.append(row)
		table.add_rows(new_matr)
	return table.draw()

def show_step(request):
	#TODO add multi file tracing /source showing
	# return render(request,'viewer/steps.html',context={'source_code':source_code})
	step = int(request.GET['step'])
	curr_mode = int(request.GET['mode'])
	show_all_vars = int(request.GET['all_vars'])
	var_changes = var_Tracer.final_dict[step]['changes']
	# if var_changes:
	# 	show_all_vars = False
	all_vars = var_Tracer.final_dict[step]['vars']
	new_all_vars = []
	for name,vari in all_vars:
		if type(vari)==list:
			new_all_vars.append((name,render_matrices(vari)))

		else:
			new_all_vars.append((name,vari))
	all_vars = new_all_vars
	new_var_changes = []
	for name,prev,new,line,file in var_changes:
		if type(prev)==list:
			prev = render_matrices(prev)
		if type(new)==list:
			new = render_matrices(new)
		new_var_changes.append((name,prev,new,line,file))
	var_changes = new_var_changes





	tree_images = var_Tracer.final_dict[step]['images']
	stack_images = stack_Tracer.final_dict[step]['images'].split(to_cutoff)[1]
	new_imgs = []
	curr_line = var_Tracer.final_dict[step]["line"]
	next_line,prev_line=1,1
	if step<max_step:
		next_line = var_Tracer.final_dict[step+1]["line"]
	if step>2:
		prev_line = var_Tracer.final_dict[step-1]["line"]
	curr_output = output_recorder.final_dict[step]
	for img in tree_images:
		new_imgs.append(img.split(to_cutoff)[1])
	tree_images = new_imgs
	# var_names = []
	# var_prevs = []
	# var_news = []
	# for name,prev,new,line,file_name in var_changes:
	# 	var_names.append(name)
	# 	var_prevs.append(str(prev))
	# 	var_news.append(str(new))
	if show_all_vars==0:
		if var_changes:
			show_all_vars=1
		else:
			show_all_vars=2

	flowchart_images = flowchart_generator.final_dict[step]['images'].split('viewer/static')[1]
	file = flowchart_generator.final_dict[step]['file']
	# print("stack_images",stack_images)
	# return render(request,'viewer/steps.html',context={'source_code':source_code})
	# return render(request,'viewer/debug.html',context={'debug':debug})
	file_path_to_show = "/".join(file.split("/")[-2:])
	return render(request,'viewer/new_steps.html',context = {'file':file_path_to_show,\
		'func':func,\
		'var_changes':var_changes,\
		'all_vars':all_vars,\
		'show_all_vars':show_all_vars,\
		'tree_images':tree_images,\
		'stack_images':stack_images,\
		'flowchart_images':flowchart_images,\
		'source_code':get_source_code(file),\
		'curr_step':step,\
		'curr_line':curr_line,\
		'curr_output':curr_output,
		'next_line':next_line,
		'prev_line':prev_line,
		'curr_mode':curr_mode,
		'max_step':max_step})



