# Algorithm flow Visualizer

This is a GSOC'20 project .

Welcome to Algorithm Flow Visualizer ! 

The flowchart visualizer attempts to do the following : Given a function to visualize , it breaks it down into every step of its.
Then , it shows the control flow jumps being made with every step . This aims to give the programmer a great deal of help in 
visualizing the flow of a algorithm , and how they actually behave given an input.

### Current Runtime instructions of the webapp:

``` 
python3 flowview/manage.py runserver >log
```

* Go to http://127.0.0.1:8000/viewer
    
* Enter path to file and function to run



### For Phase 2 work : Ie , the stack visualizer , the variable tracer : go to [demo.md](demo.md)

#### For instructions on how to run flowchart visualizer , go to the bottom!.The file [connect.py](/connect.py) contains a sample run at the end of the file

## Features :


1. Created a runtime based depictor of program , rather than a static version enveloping the entire program regardless of its use or not
Only created cfgs of functions being used in runtime , with blocks being show if they were used in runtime

2. Added functionality for arguments to be passed  to the function being debugged

3. There are currently two modes available , a visual mode , and a non visual mode.
A generated timeline of blocks is created : which is basically the timeline of the control flow of the code on runtime.

    If the visual mode is used , the program creates a flowchart highlighting every link being used at every step.Formats that can be selected are 
    among graphviz's formats ,can be seen [here](https://graphviz.org/doc/info/output.html)

4. A flowchart on every step  allow for stepping back and forth, through every step of the code.

5. Have subclassed blocks for ease of developement/extensibility, and replaced generated blocks with new subclassed blocks. 

6. Subclassing of blocks allowed for user changes to the appearance of control flow blocks, using  color and shape,
extending to the full range of [graphviz's options](https://graphviz.org/doc/info/shapes.html)
 To try it out , just go ahead in [control_models.py](control_models.py) and change LoopBlock.shape="polygon" and colour to "red"

7.  Since StatiCfg was the repo I was using , I added support for control flow statements in addition to the ones it was covering (refer to TODO #1 for Phase #1).
This greatly helped me understand the working of the code , and how to use it in my project.

8. Implemented tests on popular algorithms ,selection sort , insertion sort , knapsack.

[This blog](https://vishwesh-d-kumar.github.io/GSoC-2020-Journey-so-far!/) post has been written about the same , which has a overwiew of what I learnt , and the logic I followed in implementing the targets.

I am currently using the [my public fork of StatiCfg](https://github.com/vishwesh-D-kumar/staticfg). 
Version history of 1.Staticfg's changes can be found in the repo.

This [PR](https://github.com/coetaur0/staticfg/pull/13) has been sent also , containing general purpose improvements.

[UPDATE] The above PR has been merged into master of StatiCfg !


Current TODO's for Phase #1:

1. Staticfg

    * [x] Add support for continue statements in staticfg 
    
    * [x] Stop breakage of code on statements of type 
        ```python
        [1,2].count()
        ```
    
    * [x] Improve Clean_cfg to make sure no empty blocks pop up in cfg

2. Generating timeline of given program
    * [x] Create A timeline generator
    
    * [x] Take care of statements that have no such blocks created for them  and hence cannot be mapped to any block(ie : break , continue)

3. Connect staticfg to timeline generation

    * [x] Map every line to its corresponding block
    
    * [x] Create runtime depictor of the program , with a pdf being given as an output at every step
    
    * [x] Remove unnecessary produced steps 
    
    * [x] Only show blocks being used in runtime 
    
     
    Additional Features thought of:
    
    * Map comments to corresponding blocks too
4. Convert the cfg to a flowchart 

    * [x] Decide on which flowchart blocks to use
    
    * [x] Devise a algorithm to break up given cfg blocks based on statements 
    
    * [x] Create a class for the entire process
    
    * [x] Highlight control flow blocks with colors for better visual representation
    
    * [x] Align the graphviz output to look better (Maybe only use straight lines?)
    
    * [ ] Add a legend for users to refer to
 
5. Write unittests for the same

    * [x] Write simple tests to check for continue/break statements
    * [x] Check with popular sorting algorithms
 
 ---
 How to run
 
 *Requires python 3.6 or above, due to use of f-strings*
 
0. Install required packages from requirements.txt. Do have a look at how to install [graphviz](https://graphviz.gitlab.io/download)

    Assuming apt to be your system package manager , this should work
    ```
        pip3 install -r requirements.txt
        apt-get install graphviz  
    ```

1. Lets call the file you want to visualize as test.py (a sample test.py is in the repo)
2. Instantiate in the following manner
    ```python
   from connect import FlowGen
   f = FlowGen('test.py', 'f4',[1,2,3,4,5])
    ```
   where f4  is the function name , test.py is the file name , and [1,2,3,4] are the arguments to pass to the function (can be multiple)
3. To generate the flowchart in a directory output in the same directory as test.py/file which was passed , 
    ```python
   timeline = f.generate_flowchart('pdf')
    ```
   Or if you just want the blocks timeline ,without any pdf/svg created, pass the parameter False after the type
   ```python
   timeline = f.generate_flowchart('pdf', False)
   ```
4. In output folder , you can see the svg/pdf files being made.Name of file corresponds to step of program.

 Current TODO's for Recursion Visualizer:
 
 * [x] Add the stack frame on every call , while noting parameters being called on 
        Using frame.f_locals as of now , can switch to inspect module instead if errors occur

 * [ ] Figure out a way to figure out the function parameters called with(i+1,j-1 instead of 1,2)(Can be done by parsing AST?)
 
 * [ ] Show Graphviz output once stack generation is done (Using cells type)
 
