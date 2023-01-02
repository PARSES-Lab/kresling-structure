### Kresling module script
## Table of Contents  
[Description of project](#description)  
[Instructions for use](#instructions)  

<a name="description"/>
## Description of project
A Kresling module is a cylindrical origami shape that is representative of the buckling pattern formed when a cylinder of paper is twisted and buckles. In this script, each fold of the module is drawn as two sets of triangles that are lofted in between using Autodesk Fusion Python API. This results in a Kresling module with uniform sidewall thickness. An explanation of the math is available in the [Kresling notes file](../blob/main/Kresling_notes_for_CAD.pdf). 

<a name="instructions"/>
## Instructions
To use this script to generate a Kresling module STL, you will need Autodesk Fusion 360. If you already have Fusion 360 installed, skip to step 2.

1. Make an educational Autodesk account and [download Fusion 360](https://www.autodesk.com/products/fusion-360/education). Note that Fusion 360 permits educational licenses to be used for university research. 

2. Download the [Kresling generating script](../blob/main/Kresling.py) and put the .py file in a folder called "Kresling". 

3. Open Fusion 360 and select "UTILITIES" in the toolbar. 

4. Open the "ADD-INS" menu and select "Scripts and Add-Ins". 

5. Click the green "+" next to "My Scripts" in the "Scripts" tab. 

6. Navigate to the "Kresling" folder you created in step 2. 

7. Select your new Kresling script and click the Run button to generate a Kresling module. 
