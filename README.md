#Algorithm flow Visualizer

This is a GSOC'20 project .

I am currently using the [my public fork of StatiCfg](https://github.com/vishwesh-D-kumar/staticfg). 
Version history of 1.Staticfg's changes can be found in the repo.
This [PR](https://github.com/coetaur0/staticfg/pull/13) has been sent also , containing general purpose improvements


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
    
    * [ ] Remove unnecessary produced steps 
    
    * [ ] Only show blocks being used in runtime 
    
     
    Additional Features thought of:
    
    * Map comments to corresponding blocks too
4. Convert the cfg to a flowchart 

    * [ ] Decide on which flowchart blocks to use
    
    * [ ] Devise a algorithm to break up given cfg blocks based on statements 
    
    * [ ] Align the graphviz output to look better (Maybe only use straight lines?)
 
 
 
 ---
 How to run
 
 *Requires python 3.6 or above, due to use of f-strings*
1. Save file you want to visualize in the repo
2. Edit variable name filepath according to name of file saved
3. Edit function name to debug (required )
4. Run with 
    ```bash
        python connect.py
    ```
5. In output folder , you can see the svg files being made.Name of file corresponds to step of program.

 