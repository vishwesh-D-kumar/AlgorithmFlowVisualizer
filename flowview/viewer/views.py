from django.shortcuts import render

from django.http import HttpResponse,HttpResponseRedirect
from .recursion_visualize.stackgen import go
from .variableTrace.variable_trace import go_file
from .flowgen.connect import FlowGen,OutputRecorder
from pprint import pformat
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
source_code = []
# logging_file = open('var_debug_log.txt','a+')
def dbg(s):
	logging_file.write(s)
def index(request):
	return render(request,'viewer/index.html')
	# pass dict context to pass whatver you want to 
    # return HttpResponse("###\n".join(str(stack_Tracer.final_dict),str(var_Tracer.final_dict),str(flowchart_generator.final_dict)))
def run_tracer(request):
	global step 
	global var_Tracer
	global stack_Tracer
	global file 
	global func
	global flowchart_generator
	global source_code
	global output_recorder
	step = 1
	file = request.POST['file']
	func = request.POST['func']
	with open(file,'r+') as f:
		source_code = f.read().split('\n')
		# print(source_code)
	# return HttpResponse(source_code)
	# return HttpResponseRedirect('step?step=2')
	var_Tracer =  go_file(file= file,func = func,include_files = [])
	stack_Tracer = go(file=file,func = func)
	flowchart_generator = FlowGen(file,func)
	flowchart_generator.generate_flowchart()
	output_recorder  = OutputRecorder(file,func)
	output_recorder.record_output()
	# return HttpResponse("###<br>".join([str(stack_Tracer.final_dict),str(var_Tracer.final_dict),str(flowchart_generator.final_dict)]))

	return HttpResponseRedirect('step?step=2&all_vars=1')
	for step in var_Tracer.final_dict:
		var_changes = var_Tracer.final_dict[step]['changes']
		tree_images = var_Tracer.final_dict[step]['images']
		stack_images = stack_Tracer.final_dict[step]['images']
		flowchart_images = flowchart_generator.final_dict[step]

	return render(request,'viewer/steps.html')
	return HttpResponse(f"Path entered is :{file}, func entered is :{func}")
def show_step(request):
	#TODO add multi file tracing /source showing
	# return render(request,'viewer/steps.html',context={'source_code':source_code})
	to_cutoff = 'flowview/viewer/static'
	step = int(request.GET['step'])
	show_all_vars = int(request.GET['all_vars'])
	var_changes = var_Tracer.final_dict[step]['changes']
	# if var_changes:
	# 	show_all_vars = False
	all_vars = var_Tracer.final_dict[step]['vars']
	tree_images = var_Tracer.final_dict[step]['images']
	stack_images = stack_Tracer.final_dict[step]['images'].split(to_cutoff)[1]
	new_imgs = []
	curr_line = flowchart_generator.final_dict[step]["line"]
	curr_output = output_recorder.final_dict[step]
	for img in tree_images:
		new_imgs.append(img.split(to_cutoff)[1])
	tree_images = new_imgs
	var_names = []
	var_prevs = []
	var_news = []
	for name,prev,new,line,file_name in var_changes:
		var_names.append(name)
		var_prevs.append(str(prev))
		var_news.append(str(new))
	if show_all_vars==0:
		if var_changes:
			show_all_vars=1
		else:
			show_all_vars=2

	flowchart_images = flowchart_generator.final_dict[step]['images'].split('viewer/static')[1]
	# print("stack_images",stack_images)
	# return render(request,'viewer/steps.html',context={'source_code':source_code})
	return render(request,'viewer/steps.html',context = {'file':file,\
		'func':func,\
		'var_changes':var_changes,\
		'all_vars':all_vars,\
		'show_all_vars':show_all_vars,\
		'tree_images':tree_images,\
		'stack_images':stack_images,\
		'flowchart_images':flowchart_images,\
		'source_code':source_code,\
		'curr_step':step,\
		'curr_line':curr_line,\
		'curr_output':curr_output})



