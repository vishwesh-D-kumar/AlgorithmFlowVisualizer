## Runtime instructions 



```
pip3 install - r requirements.txt
sudo apt-get install graphviz
```


## The StackVisualizer :

The stack visualizer is build with the idea to help others understand the 
algorithm flow for recursive functions 

It is implemented to show the following :

1. How was the function called from the previous function?

2. What are the argument values it was called with ?

3. What condition was used as a return value (for example which base case in a recursion was used?)

4. What was the return value?

7. Functionality to pass arguments to function where trace is being initiated

## Features of Stack Visualization

1. Multi File support

2. Since call stack saved at every instance , this makes the timeline of it extremely acessible , able to go back and forth between the steps


In [demo_files](demo_files) a sample recursive path finding algorithm dfs is used .
 
### Steps to run the StackVisualizer 

1. Navigate to the repo directory

2. Run the following in a python file
    ```python
   from recursion_visualize.stackgen import StackVisualizer
   
   filepath = 'your/filepath/here'
   func = 'name of function you want visualize stack for'
   s = StackVisualizer(filepath, func)
   # Pass the args/kwargs you want to pass to the function
   s.generate_flow("Arguments you want here")
 
    ``` 
3. Run the file `python3 file.py`

4. All files will be created in the output dir in the same path as that of file

Important Limitations :

* Multiline expressions are not supported  of the sort ```rec(i,j) = rec(i-1,j-1) + rec(i-2,j-2)```.
One function call per line is supported. 
 


## Variable Tracer :

The variable tracer was made to watch _selected_ variables by users. The intention is to
watch how and where the variable is being changed in runtime , something which a lot of modern debuggers 
require done manually. This can be quite tedious in specially a project environment.

The variable tracer covers the following
1. Variables can be marked using interactive comments , and added to watching

2. Attributes can be marked for tracing , allowing for classes to be traced.(See limitations for more)

3. Variables , once added to tracing , will be traced through subsequent function calls also , without being 
required to be marked once again. 

4. Support for visualization of trees. Special types of variables such as trees can be added for
visualizations , via interactive comments. They will be visualized at every step.


## Features : 

1. Attribute tracing through function calls :
    After a mutable object has been marked for tracing 
    it will be traced through all incoming function calls (example, self.dp in demo2.py)

2. Globals tracing :
    Supports tracing of global variables 

3. Variable tracing across modules : can trace attributes of modules 
    (as shown in the demo with helper.DEBUG)


4. Tree Visualization on every step 

5. Adding referrers for Tree Visualizations, to see pointers 

6. Functionality to add files to check for , instead of initiating a trace for all files, which the file calls upon .
Can considerably save time. 

7. Functionality to pass arguments to function where trace is being initiated

Important Limitations :

* The attribute based tracing works only for 1 attribute of the referenced object :
 ie : it wont work for comments like ```watchvar self.x.y``` .
 
    
### Steps to run variable Tracer

1. Navigate to the repo directory

2. ```python
   from pprint import pprint
   from variableTrace.variable_trace import Tracer
   filepath = 'your/filepath/here'
   func = 'name of function to start trace at'
   w = Tracer(file=filepath,func=func,include_files = ['Files to include'])
   w.run_func("Args here to pass to function")
   pprint(w.changes) #Print all changes in format of (name_of_variable,prev_val , new_val,line_at ,file at which change is there)

   
   ```

3. Steps to mark variables for variable tracing 
    
    ```python
   # Normal Variables :
    
    x = 0 # watchvar x
    
    # Attributes of classes 
    
    node.neighbours = [node1,node2] # watchvar node.neighbours
   class Node:
        def __init__(self, val):
            self.val = val
            self.right = None
            self.left = None
   class FullNode:
        def __init__(self, val):
            self.data = val
            self.children = []
   # Visualizing BinaryTrees:
      root = Node(2) # watchvar btree:left:right:val root
   # Adding a referrer to the binary tree : only for binary trees
       root_ref = root # watchvar ref:root:btree root_ref
   # Visualizing trees with N nodes:
     root = FullNode(1) # watchvar tree:children:data root
   
   
     
    ```
   Important parameters to note above
   
   * ```# watchvar btree:left:right:val root```
   
   left : The attribute to the left node of the given node
   
   right : The attribute to the right node of the given node
   
   val : The attribute to the value stored in the node , this node stores 
   
   The attribute is accessed by getattr , ie
   ``` getattr(root,'left')``` -> gives object to the left node
   
   ``` getattr(root,'right')``` -> gives object to the right node
   If you change the attribute , from 'left' to lets say 'node1', then the comment attached would change 
   accordingly : ```# watchvar btree:node1:right:val root```
   
   Similarly:
   
   * ```# watchvar tree:children:data root``` 
   
   children : attribute to iterable of children of node
   
   data: attribute to the data of the node
   
   * ```# watchvar ref:root:btree root_ref```
   
   ref : shows a reference being defined
   root : variable tree to refer to 
   btree : type of tree of variable
   root_ref : name of watching element
   * include_files -> Files to include .To not initiate trace for all files, which may be quite a trace for 
   large projects. If a directory has been provided in paths , then it matches all files in the directories
        By default , the file provided is included by default. 
   
   Include files checks the path via lowercase conversion of file path , so case matching is not supported as of now.
    
4. All outputs produced in tree_visualizations will be saved in [output](/output). Do clear it before running once again.
 
   

 # For a demo:
    
   
   ### 3 sample runs have been added to  [demo.py](/demo.py) 

   

   * Run it using ```python3 demo.py > log```
   
   * The source code being debugged is in [demo_files](/demo_files) , the function 'go' in [demo1.py](demo_files/demo1.py)
   
   * Solution.findPath finds if a path exists from 0,0 to the bottom right corner of the matrix , considering 0 to be an obstacle and 1 to be 
   a traversable block, using dfs
   
   * The stack trace would be available as individual images in [demo_files/output](demo_files/output)
   
   * For tree demo , the go to [/output](/output). The file being debugged in it is [tree_demo.py](/demo_files/tree_demo.py) 
   
   ## DEMO
A sample gif is attached below ,showing the stack trace visualized across files , created by the demo


What the gif entails:
for every call made: it gives the following in order : 

1. The way the call was made from the previous function

2. The line the call was made at

3. The Arguments used in the call

For every return :
1. The condition that was used to return the function

2. The return value


![Demo](demo_files/demo.gif) 
   

## A sample output gif for trees is added . It runs  [tree_demo.py](/demo_files/tree_demo.py) as a sample run

This code corresponds to multiple insertions in a binary search tree, and marks x as the pointer to follow to the leaf node on which to enter

![demo_tree](/demo_files/tree_demo.gif)   
   


   
