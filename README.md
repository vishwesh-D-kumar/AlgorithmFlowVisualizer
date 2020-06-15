#Algorithm flow Visualizer

This is a GSOC'20 project .

I am currently using the [my public fork of StatiCfg](https://github.com/vishwesh-D-kumar/staticfg). 
Version history of 1.Staticfg's changes can be found in the repo.
This [PR](https://github.com/coetaur0/staticfg/pull/13) has been sent also , containing general purpose improvements.
The above PR has been merged into master of StatiCfg !


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
 
0. Install required packages from requirements.txt. Do have a look at how to install graphviz.(will be required to be installed from package managers also (apt-get,brew))
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
   Or if you just want the blocks timeline ,without any pdf/svg creted
   ```python
   timeline = f.generate_flowchart('pdf', False)
   ```
5. In output folder , you can see the svg/pdf files being made.Name of file corresponds to step of program.

 