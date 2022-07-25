{\rtf1\ansi\ansicpg1252\cocoartf2580
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fnil\fcharset0 Menlo-Regular;}
{\colortbl;\red255\green255\blue255;\red89\green138\blue67;\red23\green23\blue23;\red202\green202\blue202;
\red183\green111\blue179;\red67\green192\blue160;\red66\green179\blue255;\red167\green197\blue152;\red140\green211\blue254;
\red212\green214\blue154;\red70\green137\blue204;\red194\green126\blue101;}
{\*\expandedcolortbl;;\cssrgb\c41569\c60000\c33333;\cssrgb\c11765\c11765\c11765;\cssrgb\c83137\c83137\c83137;
\cssrgb\c77255\c52549\c75294;\cssrgb\c30588\c78824\c69020;\cssrgb\c30980\c75686\c100000;\cssrgb\c70980\c80784\c65882;\cssrgb\c61176\c86275\c99608;
\cssrgb\c86275\c86275\c66667;\cssrgb\c33725\c61176\c83922;\cssrgb\c80784\c56863\c47059;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\deftab720
\pard\pardeftab720\sl360\partightenfactor0

\f0\fs24 \cf2 \cb3 \expnd0\expndtw0\kerning0
\outl0\strokewidth0 \strokec2 #Kristen L. Dorsey, Northeastern University\cf4 \cb1 \strokec4 \
\
\pard\pardeftab720\sl360\partightenfactor0
\cf5 \cb3 \strokec5 import\cf4 \strokec4  \cf6 \strokec6 adsk\cf4 \strokec4 .\cf6 \strokec6 core\cf4 \strokec4 , \cf6 \strokec6 adsk\cf4 \strokec4 .\cf6 \strokec6 fusion\cf4 \strokec4 , \cf6 \strokec6 adsk\cf4 \strokec4 .\cf6 \strokec6 cam\cf4 \cb1 \strokec4 \
\cf5 \cb3 \strokec5 import\cf4 \strokec4  \cf6 \strokec6 math\cf4 \cb1 \strokec4 \
\
\pard\pardeftab720\sl360\partightenfactor0
\cf2 \cb3 \strokec2 #Kresling dimensions\cf4 \cb1 \strokec4 \
\pard\pardeftab720\sl360\partightenfactor0
\cf7 \cb3 \strokec7 R\cf4 \strokec4  = \cf8 \strokec8 1\cf4 \strokec4  \cf2 \strokec2 #Length of Kresling polygon face\cf4 \cb1 \strokec4 \
\pard\pardeftab720\sl360\partightenfactor0
\cf9 \cb3 \strokec9 t\cf4 \strokec4  = \cf8 \strokec8 0.05\cf4 \strokec4  \cf2 \strokec2 #Thickness of the Kresling in cm \cf4 \cb1 \strokec4 \
\pard\pardeftab720\sl360\partightenfactor0
\cf7 \cb3 \strokec7 N\cf4 \strokec4  = \cf8 \strokec8 6\cf4 \strokec4  \cf2 \strokec2 #Number of Kresling polygon faces\cf4 \cb1 \strokec4 \
\pard\pardeftab720\sl360\partightenfactor0
\cf9 \cb3 \strokec9 alpha\cf4 \strokec4  = \cf6 \strokec6 math\cf4 \strokec4 .\cf9 \strokec9 pi\cf4 \strokec4 *\cf8 \strokec8 45\cf4 \strokec4 /\cf8 \strokec8 180\cf4 \cb1 \strokec4 \
\pard\pardeftab720\sl360\partightenfactor0
\cf7 \cb3 \strokec7 L1\cf4 \strokec4  = \cf8 \strokec8 4\cf4 \cb1 \strokec4 \
\pard\pardeftab720\sl360\partightenfactor0
\cf9 \cb3 \strokec9 makeBase\cf4 \strokec4  = \cf8 \strokec8 1\cf4 \strokec4  \cf2 \strokec2 #Make the base of the Kresling? (Boolean)\cf4 \cb1 \strokec4 \
\
\cf9 \cb3 \strokec9 gamma\cf4 \strokec4  = \cf6 \strokec6 math\cf4 \strokec4 .\cf9 \strokec9 pi\cf4 \strokec4 /\cf7 \strokec7 N\cf4 \cb1 \strokec4 \
\pard\pardeftab720\sl360\partightenfactor0
\cf7 \cb3 \strokec7 P\cf4 \strokec4  = \cf7 \strokec7 R\cf4 \strokec4 /\cf6 \strokec6 math\cf4 \strokec4 .\cf10 \strokec10 sin\cf4 \strokec4 (\cf9 \strokec9 gamma\cf4 \strokec4 ) \cf2 \strokec2 #Redefine R so that the dimensions are correct for center of Kresling polygon to one polygon angle\cf4 \cb1 \strokec4 \
\
\pard\pardeftab720\sl360\partightenfactor0
\cf11 \cb3 \strokec11 def\cf4 \strokec4  \cf10 \strokec10 PolygonPoints\cf4 \strokec4 (\cf9 \strokec9 P\cf4 \strokec4 ,\cf9 \strokec9 N\cf4 \strokec4 ,\cf9 \strokec9 alpha\cf4 \strokec4 ,\cf9 \strokec9 X\cf4 \strokec4 ):\cb1 \
\pard\pardeftab720\sl360\partightenfactor0
\cf4 \cb3     \cf2 \strokec2 #Generate the polygon points for top or bottom face. By convention, bottom face should be alpha = 0\cf4 \cb1 \strokec4 \
\cb3     \cf2 \strokec2 #Create N points in X or Y\cf4 \cb1 \strokec4 \
\
\cb3     \cf5 \strokec5 for\cf4 \strokec4  \cf9 \strokec9 k\cf4 \strokec4  \cf5 \strokec5 in\cf4 \strokec4  \cf6 \strokec6 range\cf4 \strokec4 (\cf9 \strokec9 N\cf4 \strokec4 ):\cb1 \
\cb3         \cf5 \strokec5 if\cf4 \strokec4  \cf9 \strokec9 X\cf4 \strokec4 ==\cf8 \strokec8 1\cf4 \strokec4 :\cb1 \
\cb3             \cf9 \strokec9 outerPts\cf4 \strokec4  = [\cf9 \strokec9 P\cf4 \strokec4 *\cf6 \strokec6 math\cf4 \strokec4 .\cf10 \strokec10 cos\cf4 \strokec4 ((\cf8 \strokec8 2\cf4 \strokec4 *\cf9 \strokec9 k\cf4 \strokec4 *\cf6 \strokec6 math\cf4 \strokec4 .\cf9 \strokec9 pi\cf4 \strokec4 /\cf9 \strokec9 N\cf4 \strokec4 )-\cf9 \strokec9 alpha\cf4 \strokec4 ) \cf5 \strokec5 for\cf4 \strokec4  \cf9 \strokec9 k\cf4 \strokec4  \cf5 \strokec5 in\cf4 \strokec4  \cf6 \strokec6 range\cf4 \strokec4 (\cf9 \strokec9 N\cf4 \strokec4 )]\cb1 \
\cb3         \cf5 \strokec5 else\cf4 \strokec4 :\cb1 \
\cb3             \cf9 \strokec9 outerPts\cf4 \strokec4  = [\cf9 \strokec9 P\cf4 \strokec4 *\cf6 \strokec6 math\cf4 \strokec4 .\cf10 \strokec10 sin\cf4 \strokec4 ((\cf8 \strokec8 2\cf4 \strokec4 *\cf9 \strokec9 k\cf4 \strokec4 *\cf6 \strokec6 math\cf4 \strokec4 .\cf9 \strokec9 pi\cf4 \strokec4 /\cf9 \strokec9 N\cf4 \strokec4 )-\cf9 \strokec9 alpha\cf4 \strokec4 ) \cf5 \strokec5 for\cf4 \strokec4  \cf9 \strokec9 k\cf4 \strokec4  \cf5 \strokec5 in\cf4 \strokec4  \cf6 \strokec6 range\cf4 \strokec4 (\cf9 \strokec9 N\cf4 \strokec4 )]\cb1 \
\
\cb3     \cf5 \strokec5 return\cf4 \strokec4  \cf9 \strokec9 outerPts\cf4 \cb1 \strokec4 \
\
\pard\pardeftab720\sl360\partightenfactor0
\cf11 \cb3 \strokec11 def\cf4 \strokec4  \cf10 \strokec10 CreateOffsetPlane\cf4 \strokec4 (\cf9 \strokec9 cPlanes\cf4 \strokec4 ,\cf9 \strokec9 offsetWidth\cf4 \strokec4 ):\cb1 \
\pard\pardeftab720\sl360\partightenfactor0
\cf4 \cb3     \cf9 \strokec9 offsetPlane\cf4 \strokec4  = \cf9 \strokec9 cPlanes\cf4 \strokec4 .createInput()\cb1 \
\cb3     \cf9 \strokec9 offset\cf4 \strokec4  = \cf6 \strokec6 adsk\cf4 \strokec4 .\cf6 \strokec6 core\cf4 \strokec4 .\cf6 \strokec6 ValueInput\cf4 \strokec4 .\cf10 \strokec10 createByString\cf4 \strokec4 (\cf6 \strokec6 str\cf4 \strokec4 (\cf9 \strokec9 offsetWidth\cf4 \strokec4 )+\cf12 \strokec12 'cm'\cf4 \strokec4 )\cb1 \
\cb3     \cf9 \strokec9 offsetPlane\cf4 \strokec4 .setByOffset(\cf9 \strokec9 rootComp\cf4 \strokec4 .xYConstructionPlane, \cf9 \strokec9 offset\cf4 \strokec4 )\cb1 \
\cb3     \cf9 \strokec9 planeName\cf4 \strokec4  = \cf9 \strokec9 cPlanes\cf4 \strokec4 .add(\cf9 \strokec9 offsetPlane\cf4 \strokec4 )\cb1 \
\cb3     \cf5 \strokec5 return\cf4 \strokec4  \cf9 \strokec9 planeName\cf4 \cb1 \strokec4 \
\
\pard\pardeftab720\sl360\partightenfactor0
\cf11 \cb3 \strokec11 def\cf4 \strokec4  \cf10 \strokec10 CreateKTriangle\cf4 \strokec4 (\cf9 \strokec9 cPlanes\cf4 \strokec4 ,\cf9 \strokec9 zOffS\cf4 \strokec4 ,\cf9 \strokec9 p0\cf4 \strokec4 ,\cf9 \strokec9 p1\cf4 \strokec4 ,\cf9 \strokec9 p2\cf4 \strokec4 ):\cb1 \
\pard\pardeftab720\sl360\partightenfactor0
\cf4 \cb3     \cf9 \strokec9 TriPlane\cf4 \strokec4  = \cf10 \strokec10 CreateOffsetPlane\cf4 \strokec4 (\cf9 \strokec9 cPlanes\cf4 \strokec4 ,\cf9 \strokec9 zOffS\cf4 \strokec4 )\cb1 \
\cb3     \cf9 \strokec9 Triangle\cf4 \strokec4  = \cf9 \strokec9 sketchObjs\cf4 \strokec4 .add(\cf9 \strokec9 TriPlane\cf4 \strokec4 )\cb1 \
\
\cb3     \cf2 \strokec2 # #define the triangle points\cf4 \cb1 \strokec4 \
\cb3     \cf9 \strokec9 dP0\cf4 \strokec4  = \cf6 \strokec6 adsk\cf4 \strokec4 .\cf6 \strokec6 core\cf4 \strokec4 .\cf6 \strokec6 Point3D\cf4 \strokec4 .\cf10 \strokec10 create\cf4 \strokec4 (\cf9 \strokec9 p0\cf4 \strokec4 [\cf8 \strokec8 0\cf4 \strokec4 ], \cf9 \strokec9 p0\cf4 \strokec4 [\cf8 \strokec8 1\cf4 \strokec4 ], \cf9 \strokec9 p0\cf4 \strokec4 [\cf8 \strokec8 2\cf4 \strokec4 ])\cb1 \
\cb3     \cf9 \strokec9 dP1\cf4 \strokec4  = \cf6 \strokec6 adsk\cf4 \strokec4 .\cf6 \strokec6 core\cf4 \strokec4 .\cf6 \strokec6 Point3D\cf4 \strokec4 .\cf10 \strokec10 create\cf4 \strokec4 (\cf9 \strokec9 p1\cf4 \strokec4 [\cf8 \strokec8 0\cf4 \strokec4 ], \cf9 \strokec9 p1\cf4 \strokec4 [\cf8 \strokec8 1\cf4 \strokec4 ], \cf9 \strokec9 p1\cf4 \strokec4 [\cf8 \strokec8 2\cf4 \strokec4 ])\cb1 \
\cb3     \cf9 \strokec9 dP2\cf4 \strokec4  = \cf6 \strokec6 adsk\cf4 \strokec4 .\cf6 \strokec6 core\cf4 \strokec4 .\cf6 \strokec6 Point3D\cf4 \strokec4 .\cf10 \strokec10 create\cf4 \strokec4 (\cf9 \strokec9 p2\cf4 \strokec4 [\cf8 \strokec8 0\cf4 \strokec4 ], \cf9 \strokec9 p2\cf4 \strokec4 [\cf8 \strokec8 1\cf4 \strokec4 ], \cf9 \strokec9 p2\cf4 \strokec4 [\cf8 \strokec8 2\cf4 \strokec4 ])\cb1 \
\cb3    \cb1 \
\cb3     \cf2 \strokec2 #draw the triangle edges\cf4 \cb1 \strokec4 \
\cb3     \cf9 \strokec9 triLines\cf4 \strokec4  = \cf9 \strokec9 Triangle\cf4 \strokec4 .sketchCurves.sketchLines\cb1 \
\cb3     \cf9 \strokec9 lVLine\cf4 \strokec4  = \cf9 \strokec9 triLines\cf4 \strokec4 .addByTwoPoints(\cf9 \strokec9 dP0\cf4 \strokec4 ,\cf9 \strokec9 dP1\cf4 \strokec4 )\cb1 \
\cb3     \cf9 \strokec9 lULine\cf4 \strokec4  = \cf9 \strokec9 triLines\cf4 \strokec4 .addByTwoPoints(\cf9 \strokec9 dP1\cf4 \strokec4 ,\cf9 \strokec9 dP2\cf4 \strokec4 )\cb1 \
\cb3     \cf9 \strokec9 rULine\cf4 \strokec4  = \cf9 \strokec9 triLines\cf4 \strokec4 .addByTwoPoints(\cf9 \strokec9 dP2\cf4 \strokec4 ,\cf9 \strokec9 dP0\cf4 \strokec4 )\cb1 \
\cb3     \cb1 \
\cb3     \cf9 \strokec9 profile\cf4 \strokec4  = \cf9 \strokec9 Triangle\cf4 \strokec4 .profiles.item(\cf8 \strokec8 0\cf4 \strokec4 )\cb1 \
\
\cb3     \cf5 \strokec5 return\cf4 \strokec4  \cf9 \strokec9 profile\cf4 \strokec4   \cb1 \
\
\pard\pardeftab720\sl360\partightenfactor0
\cf11 \cb3 \strokec11 def\cf4 \strokec4  \cf10 \strokec10 KreslingPolygonSketch\cf4 \strokec4 (\cf9 \strokec9 cPlanes\cf4 \strokec4 ,\cf9 \strokec9 pX\cf4 \strokec4 ,\cf9 \strokec9 pY\cf4 \strokec4 ,\cf9 \strokec9 pZ\cf4 \strokec4 ):\cb1 \
\pard\pardeftab720\sl360\partightenfactor0
\cf4 \cb3     \cf9 \strokec9 TriPlane\cf4 \strokec4  = \cf10 \strokec10 CreateOffsetPlane\cf4 \strokec4 (\cf9 \strokec9 cPlanes\cf4 \strokec4 ,\cf8 \strokec8 0\cf4 \strokec4 )\cb1 \
\cb3     \cf9 \strokec9 Triangle\cf4 \strokec4  = \cf9 \strokec9 sketchObjs\cf4 \strokec4 .add(\cf9 \strokec9 TriPlane\cf4 \strokec4 )\cb1 \
\
\cb3     \cf7 \strokec7 N\cf4 \strokec4  = \cf10 \strokec10 len\cf4 \strokec4 (\cf9 \strokec9 pX\cf4 \strokec4 )\cb1 \
\cb3     \cb1 \
\cb3     \cf2 \strokec2 #define the Kresling polygon\cf4 \cb1 \strokec4 \
\cb3     \cf9 \strokec9 KresLines\cf4 \strokec4  = \cf9 \strokec9 Triangle\cf4 \strokec4 .sketchCurves.sketchLines\cb1 \
\cb3     \cf5 \strokec5 for\cf4 \strokec4  \cf9 \strokec9 k\cf4 \strokec4  \cf5 \strokec5 in\cf4 \strokec4  \cf6 \strokec6 range\cf4 \strokec4 (\cf7 \strokec7 N\cf4 \strokec4 ):\cb1 \
\cb3         \cf9 \strokec9 dP0\cf4 \strokec4  = \cf6 \strokec6 adsk\cf4 \strokec4 .\cf6 \strokec6 core\cf4 \strokec4 .\cf6 \strokec6 Point3D\cf4 \strokec4 .\cf10 \strokec10 create\cf4 \strokec4 (\cf9 \strokec9 pX\cf4 \strokec4 [\cf9 \strokec9 k\cf4 \strokec4 ], \cf9 \strokec9 pY\cf4 \strokec4 [\cf9 \strokec9 k\cf4 \strokec4 ], \cf9 \strokec9 pZ\cf4 \strokec4 )\cb1 \
\cb3         \cf9 \strokec9 dP1\cf4 \strokec4  = \cf6 \strokec6 adsk\cf4 \strokec4 .\cf6 \strokec6 core\cf4 \strokec4 .\cf6 \strokec6 Point3D\cf4 \strokec4 .\cf10 \strokec10 create\cf4 \strokec4 (\cf9 \strokec9 pX\cf4 \strokec4 [((\cf9 \strokec9 k\cf4 \strokec4 +\cf8 \strokec8 1\cf4 \strokec4 )%\cf7 \strokec7 N\cf4 \strokec4 )], \cf9 \strokec9 pY\cf4 \strokec4 [((\cf9 \strokec9 k\cf4 \strokec4 +\cf8 \strokec8 1\cf4 \strokec4 )%\cf7 \strokec7 N\cf4 \strokec4 )], \cf9 \strokec9 pZ\cf4 \strokec4 )\cb1 \
\cb3     \cb1 \
\cb3         \cf2 \strokec2 #draw the Kresling polygon by adding the line\cf4 \cb1 \strokec4 \
\cb3         \cf9 \strokec9 KresPLine\cf4 \strokec4  = \cf9 \strokec9 KresLines\cf4 \strokec4 .addByTwoPoints(\cf9 \strokec9 dP0\cf4 \strokec4 ,\cf9 \strokec9 dP1\cf4 \strokec4 )\cb1 \
\cb3     \cb1 \
\cb3     \cf9 \strokec9 profile\cf4 \strokec4  = \cf9 \strokec9 Triangle\cf4 \strokec4 .profiles.item(\cf8 \strokec8 0\cf4 \strokec4 )\cb1 \
\
\cb3     \cf5 \strokec5 return\cf4 \strokec4  \cf9 \strokec9 profile\cf4 \strokec4      \cb1 \
\
\pard\pardeftab720\sl360\partightenfactor0
\cf11 \cb3 \strokec11 def\cf4 \strokec4  \cf10 \strokec10 AddLoftFeature\cf4 \strokec4 (\cf9 \strokec9 loftFeatures\cf4 \strokec4 ,\cf9 \strokec9 profileObjArray\cf4 \strokec4 ):\cb1 \
\pard\pardeftab720\sl360\partightenfactor0
\cf4 \cb3     \cf9 \strokec9 loftInput\cf4 \strokec4  = \cf9 \strokec9 loftFeatures\cf4 \strokec4 .createInput(\cf6 \strokec6 adsk\cf4 \strokec4 .\cf6 \strokec6 fusion\cf4 \strokec4 .\cf6 \strokec6 FeatureOperations\cf4 \strokec4 .\cf9 \strokec9 NewBodyFeatureOperation\cf4 \strokec4 )\cb1 \
\cb3     \cf9 \strokec9 loft0\cf4 \strokec4  = \cf9 \strokec9 loftInput\cf4 \strokec4 .loftSections\cb1 \
\cb3     \cf5 \strokec5 for\cf4 \strokec4  \cf9 \strokec9 x\cf4 \strokec4  \cf5 \strokec5 in\cf4 \strokec4  \cf9 \strokec9 profileObjArray\cf4 \strokec4 :\cb1 \
\cb3         \cf9 \strokec9 loft0\cf4 \strokec4 .add(\cf9 \strokec9 x\cf4 \strokec4 )\cb1 \
\cb3     \cf9 \strokec9 loftInput\cf4 \strokec4 .isSolid = \cf11 \strokec11 True\cf4 \strokec4  \cf2 \strokec2 #True for solid, False for hollow shape\cf4 \cb1 \strokec4 \
\cb3     \cf9 \strokec9 loftOutput\cf4 \strokec4  = \cf9 \strokec9 loftFeatures\cf4 \strokec4 .add(\cf9 \strokec9 loftInput\cf4 \strokec4 )\cb1 \
\cb3     \cf5 \strokec5 return\cf4 \strokec4  \cf9 \strokec9 loftOutput\cf4 \cb1 \strokec4 \
\
\pard\pardeftab720\sl360\partightenfactor0
\cf11 \cb3 \strokec11 def\cf4 \strokec4  \cf10 \strokec10 makeKreslingBody\cf4 \strokec4 (\cf9 \strokec9 cPlanes\cf4 \strokec4 ,\cf9 \strokec9 lofts\cf4 \strokec4 ,\cf9 \strokec9 P\cf4 \strokec4 ,\cf9 \strokec9 N\cf4 \strokec4 ,\cf9 \strokec9 t\cf4 \strokec4 ,\cf9 \strokec9 L1\cf4 \strokec4 ,\cf9 \strokec9 alpha\cf4 \strokec4 ,\cf9 \strokec9 makeBase\cf4 \strokec4 ):\cb1 \
\pard\pardeftab720\sl360\partightenfactor0
\cf4 \cb3     \cf2 \strokec2 #Create each Kresling triangle according to specified dimensions\cf4 \cb1 \strokec4 \
\
\cb3     \cf9 \strokec9 bodyList\cf4 \strokec4  = [] \cf2 \strokec2 #Make an empty body list to append new bodies to\cf4 \cb1 \strokec4 \
\
\cb3     \cf2 \strokec2 #Lower and upper external Kresling triangle points\cf4 \cb1 \strokec4 \
\cb3     \cf9 \strokec9 pLEX\cf4 \strokec4  = \cf10 \strokec10 PolygonPoints\cf4 \strokec4 (\cf9 \strokec9 P\cf4 \strokec4 ,\cf9 \strokec9 N\cf4 \strokec4 ,\cf8 \strokec8 0\cf4 \strokec4 ,\cf8 \strokec8 1\cf4 \strokec4 )\cb1 \
\cb3     \cf9 \strokec9 pUEX\cf4 \strokec4  = \cf10 \strokec10 PolygonPoints\cf4 \strokec4 (\cf9 \strokec9 P\cf4 \strokec4 ,\cf9 \strokec9 N\cf4 \strokec4 ,\cf9 \strokec9 alpha\cf4 \strokec4 ,\cf8 \strokec8 1\cf4 \strokec4 )\cb1 \
\cb3     \cf9 \strokec9 pLEY\cf4 \strokec4  = \cf10 \strokec10 PolygonPoints\cf4 \strokec4 (\cf9 \strokec9 P\cf4 \strokec4 ,\cf9 \strokec9 N\cf4 \strokec4 ,\cf8 \strokec8 0\cf4 \strokec4 ,\cf8 \strokec8 0\cf4 \strokec4 )\cb1 \
\cb3     \cf9 \strokec9 pUEY\cf4 \strokec4  = \cf10 \strokec10 PolygonPoints\cf4 \strokec4 (\cf9 \strokec9 P\cf4 \strokec4 ,\cf9 \strokec9 N\cf4 \strokec4 ,\cf9 \strokec9 alpha\cf4 \strokec4 ,\cf8 \strokec8 0\cf4 \strokec4 )\cb1 \
\
\cb3     \cf2 \strokec2 #Lower and upper internal Kresling triangle points\cf4 \cb1 \strokec4 \
\cb3     \cf9 \strokec9 pLIX\cf4 \strokec4  = \cf10 \strokec10 PolygonPoints\cf4 \strokec4 ((\cf9 \strokec9 P\cf4 \strokec4 -\cf9 \strokec9 t\cf4 \strokec4 ),\cf9 \strokec9 N\cf4 \strokec4 ,\cf8 \strokec8 0\cf4 \strokec4 ,\cf8 \strokec8 1\cf4 \strokec4 )\cb1 \
\cb3     \cf9 \strokec9 pUIX\cf4 \strokec4  = \cf10 \strokec10 PolygonPoints\cf4 \strokec4 ((\cf9 \strokec9 P\cf4 \strokec4 -\cf9 \strokec9 t\cf4 \strokec4 ),\cf9 \strokec9 N\cf4 \strokec4 ,\cf9 \strokec9 alpha\cf4 \strokec4 ,\cf8 \strokec8 1\cf4 \strokec4 )\cb1 \
\cb3     \cf9 \strokec9 pLIY\cf4 \strokec4  = \cf10 \strokec10 PolygonPoints\cf4 \strokec4 ((\cf9 \strokec9 P\cf4 \strokec4 -\cf9 \strokec9 t\cf4 \strokec4 ),\cf9 \strokec9 N\cf4 \strokec4 ,\cf8 \strokec8 0\cf4 \strokec4 ,\cf8 \strokec8 0\cf4 \strokec4 )\cb1 \
\cb3     \cf9 \strokec9 pUIY\cf4 \strokec4  = \cf10 \strokec10 PolygonPoints\cf4 \strokec4 ((\cf9 \strokec9 P\cf4 \strokec4 -\cf9 \strokec9 t\cf4 \strokec4 ),\cf9 \strokec9 N\cf4 \strokec4 ,\cf9 \strokec9 alpha\cf4 \strokec4 ,\cf8 \strokec8 0\cf4 \strokec4 )\cb1 \
\
\cb3     \cf2 \strokec2 #Make upper and lower Kresling triangles\cf4 \cb1 \strokec4 \
\cb3     \cf5 \strokec5 for\cf4 \strokec4  \cf9 \strokec9 m\cf4 \strokec4  \cf5 \strokec5 in\cf4 \strokec4  \cf6 \strokec6 range\cf4 \strokec4 (\cf8 \strokec8 2\cf4 \strokec4 ):    \cb1 \
\cb3         \cf5 \strokec5 for\cf4 \strokec4  \cf9 \strokec9 k\cf4 \strokec4  \cf5 \strokec5 in\cf4 \strokec4  \cf6 \strokec6 range\cf4 \strokec4 (\cf9 \strokec9 N\cf4 \strokec4 ):\cb1 \
\cb3             \cf5 \strokec5 if\cf4 \strokec4  \cf9 \strokec9 m\cf4 \strokec4  == \cf8 \strokec8 1\cf4 \strokec4 : \cf2 \strokec2 #determine upper or lower triangle\cf4 \cb1 \strokec4 \
\cb3                 \cf9 \strokec9 pE0\cf4 \strokec4  = (\cf9 \strokec9 pLEX\cf4 \strokec4 [\cf9 \strokec9 k\cf4 \strokec4 ],\cf9 \strokec9 pLEY\cf4 \strokec4 [\cf9 \strokec9 k\cf4 \strokec4 ],\cf8 \strokec8 0\cf4 \strokec4 )\cb1 \
\cb3                 \cf9 \strokec9 pE1\cf4 \strokec4  = (\cf9 \strokec9 pUEX\cf4 \strokec4 [\cf9 \strokec9 k\cf4 \strokec4 ],\cf9 \strokec9 pUEY\cf4 \strokec4 [\cf9 \strokec9 k\cf4 \strokec4 ],\cf9 \strokec9 L1\cf4 \strokec4 )\cb1 \
\cb3                 \cf9 \strokec9 pE2\cf4 \strokec4  = (\cf9 \strokec9 pLEX\cf4 \strokec4 [(\cf9 \strokec9 k\cf4 \strokec4 +\cf8 \strokec8 1\cf4 \strokec4 )%\cf9 \strokec9 N\cf4 \strokec4 ],\cf9 \strokec9 pLEY\cf4 \strokec4 [(\cf9 \strokec9 k\cf4 \strokec4 +\cf8 \strokec8 1\cf4 \strokec4 )%\cf9 \strokec9 N\cf4 \strokec4 ],\cf8 \strokec8 0\cf4 \strokec4 )\cb1 \
\
\cb3                 \cf9 \strokec9 pI0\cf4 \strokec4  = (\cf9 \strokec9 pLIX\cf4 \strokec4 [\cf9 \strokec9 k\cf4 \strokec4 ],\cf9 \strokec9 pLIY\cf4 \strokec4 [\cf9 \strokec9 k\cf4 \strokec4 ],\cf8 \strokec8 0\cf4 \strokec4 ) \cb1 \
\cb3                 \cf9 \strokec9 pI1\cf4 \strokec4  = (\cf9 \strokec9 pUIX\cf4 \strokec4 [\cf9 \strokec9 k\cf4 \strokec4 ],\cf9 \strokec9 pUIY\cf4 \strokec4 [\cf9 \strokec9 k\cf4 \strokec4 ],\cf9 \strokec9 L1\cf4 \strokec4 )\cb1 \
\cb3                 \cf9 \strokec9 pI2\cf4 \strokec4  = (\cf9 \strokec9 pLIX\cf4 \strokec4 [(\cf9 \strokec9 k\cf4 \strokec4 +\cf8 \strokec8 1\cf4 \strokec4 )%\cf9 \strokec9 N\cf4 \strokec4 ],\cf9 \strokec9 pLIY\cf4 \strokec4 [(\cf9 \strokec9 k\cf4 \strokec4 +\cf8 \strokec8 1\cf4 \strokec4 )%\cf9 \strokec9 N\cf4 \strokec4 ],\cf8 \strokec8 0\cf4 \strokec4 )\cb1 \
\cb3             \cf5 \strokec5 else\cf4 \strokec4 :\cb1 \
\cb3                 \cf9 \strokec9 pE0\cf4 \strokec4  = (\cf9 \strokec9 pUEX\cf4 \strokec4 [\cf9 \strokec9 k\cf4 \strokec4 ],\cf9 \strokec9 pUEY\cf4 \strokec4 [\cf9 \strokec9 k\cf4 \strokec4 ],\cf9 \strokec9 L1\cf4 \strokec4 )\cb1 \
\cb3                 \cf9 \strokec9 pE1\cf4 \strokec4  = (\cf9 \strokec9 pLEX\cf4 \strokec4 [(\cf9 \strokec9 k\cf4 \strokec4 +\cf8 \strokec8 1\cf4 \strokec4 )%\cf9 \strokec9 N\cf4 \strokec4 ],\cf9 \strokec9 pLEY\cf4 \strokec4 [(\cf9 \strokec9 k\cf4 \strokec4 +\cf8 \strokec8 1\cf4 \strokec4 )%\cf9 \strokec9 N\cf4 \strokec4 ],\cf8 \strokec8 0\cf4 \strokec4 )\cb1 \
\cb3                 \cf9 \strokec9 pE2\cf4 \strokec4  = (\cf9 \strokec9 pUEX\cf4 \strokec4 [(\cf9 \strokec9 k\cf4 \strokec4 +\cf8 \strokec8 1\cf4 \strokec4 )%\cf9 \strokec9 N\cf4 \strokec4 ],\cf9 \strokec9 pUEY\cf4 \strokec4 [(\cf9 \strokec9 k\cf4 \strokec4 +\cf8 \strokec8 1\cf4 \strokec4 )%\cf9 \strokec9 N\cf4 \strokec4 ],\cf9 \strokec9 L1\cf4 \strokec4 )\cb1 \
\
\cb3                 \cf9 \strokec9 pI0\cf4 \strokec4  = (\cf9 \strokec9 pUIX\cf4 \strokec4 [\cf9 \strokec9 k\cf4 \strokec4 ],\cf9 \strokec9 pUIY\cf4 \strokec4 [\cf9 \strokec9 k\cf4 \strokec4 ],\cf9 \strokec9 L1\cf4 \strokec4 )\cb1 \
\cb3                 \cf9 \strokec9 pI1\cf4 \strokec4  = (\cf9 \strokec9 pLIX\cf4 \strokec4 [(\cf9 \strokec9 k\cf4 \strokec4 +\cf8 \strokec8 1\cf4 \strokec4 )%\cf9 \strokec9 N\cf4 \strokec4 ],\cf9 \strokec9 pLIY\cf4 \strokec4 [(\cf9 \strokec9 k\cf4 \strokec4 +\cf8 \strokec8 1\cf4 \strokec4 )%\cf9 \strokec9 N\cf4 \strokec4 ],\cf8 \strokec8 0\cf4 \strokec4 )\cb1 \
\cb3                 \cf9 \strokec9 pI2\cf4 \strokec4  = (\cf9 \strokec9 pUIX\cf4 \strokec4 [(\cf9 \strokec9 k\cf4 \strokec4 +\cf8 \strokec8 1\cf4 \strokec4 )%\cf9 \strokec9 N\cf4 \strokec4 ],\cf9 \strokec9 pUIY\cf4 \strokec4 [(\cf9 \strokec9 k\cf4 \strokec4 +\cf8 \strokec8 1\cf4 \strokec4 )%\cf9 \strokec9 N\cf4 \strokec4 ],\cf9 \strokec9 L1\cf4 \strokec4 )\cb1 \
\
\cb3             \cf2 \strokec2 #Make the exterior Kresling triangle\cf4 \cb1 \strokec4 \
\cb3             \cf9 \strokec9 KreslingProfile0\cf4 \strokec4  = \cf10 \strokec10 CreateKTriangle\cf4 \strokec4 (\cf9 \strokec9 cPlanes\cf4 \strokec4 ,\cf8 \strokec8 0\cf4 \strokec4 ,\cf9 \strokec9 pE0\cf4 \strokec4 ,\cf9 \strokec9 pE1\cf4 \strokec4 ,\cf9 \strokec9 pE2\cf4 \strokec4 )\cb1 \
\cb3             \cb1 \
\cb3             \cf2 \strokec2 #Make the interior Kresling triangle\cf4 \cb1 \strokec4 \
\cb3             \cf9 \strokec9 KreslingProfile1\cf4 \strokec4 = \cf10 \strokec10 CreateKTriangle\cf4 \strokec4 (\cf9 \strokec9 cPlanes\cf4 \strokec4 ,\cf8 \strokec8 0\cf4 \strokec4 ,\cf9 \strokec9 pI0\cf4 \strokec4 ,\cf9 \strokec9 pI1\cf4 \strokec4 ,\cf9 \strokec9 pI2\cf4 \strokec4 )\cb1 \
\cb3             \cb1 \
\cb3             \cf2 \strokec2 #Create lofts to form Kresling face with specified thickness\cf4 \cb1 \strokec4 \
\cb3             \cf9 \strokec9 loftK\cf4 \strokec4  = \cf10 \strokec10 AddLoftFeature\cf4 \strokec4 (\cf9 \strokec9 lofts\cf4 \strokec4 ,[\cf9 \strokec9 KreslingProfile0\cf4 \strokec4 ,\cf9 \strokec9 KreslingProfile1\cf4 \strokec4 ])\cb1 \
\cb3         \cb1 \
\cb3                     \cf2 \strokec2 #Create bodies from loft features\cf4 \cb1 \strokec4 \
\cb3             \cf9 \strokec9 bodyK\cf4 \strokec4  = \cf9 \strokec9 loftK\cf4 \strokec4 .bodies.item(\cf8 \strokec8 0\cf4 \strokec4 )\cb1 \
\cb3             \cf9 \strokec9 bodyList\cf4 \strokec4 .\cf10 \strokec10 append\cf4 \strokec4 (\cf9 \strokec9 bodyK\cf4 \strokec4 )\cb1 \
\
\cb3     \cf2 \strokec2 #Make Kresling base\cf4 \cb1 \strokec4 \
\cb3     \cf5 \strokec5 if\cf4 \strokec4  \cf9 \strokec9 makeBase\cf4 \strokec4  == \cf8 \strokec8 1\cf4 \strokec4 :\cb1 \
\cb3         \cf9 \strokec9 KLid0\cf4 \strokec4  = \cf10 \strokec10 KreslingPolygonSketch\cf4 \strokec4 (\cf9 \strokec9 cPlanes\cf4 \strokec4 ,\cf9 \strokec9 pLEX\cf4 \strokec4 ,\cf9 \strokec9 pLEY\cf4 \strokec4 ,-\cf9 \strokec9 t\cf4 \strokec4 )\cb1 \
\cb3         \cf9 \strokec9 KLid1\cf4 \strokec4  = \cf10 \strokec10 KreslingPolygonSketch\cf4 \strokec4 (\cf9 \strokec9 cPlanes\cf4 \strokec4 ,\cf9 \strokec9 pLEX\cf4 \strokec4 ,\cf9 \strokec9 pLEY\cf4 \strokec4 ,\cf8 \strokec8 0\cf4 \strokec4 )\cb1 \
\cb3         \cf9 \strokec9 loftLid\cf4 \strokec4  = \cf10 \strokec10 AddLoftFeature\cf4 \strokec4 (\cf9 \strokec9 lofts\cf4 \strokec4 ,[\cf9 \strokec9 KLid0\cf4 \strokec4 ,\cf9 \strokec9 KLid1\cf4 \strokec4 ])\cb1 \
\cb3     \cb1 \
\cb3         \cf9 \strokec9 bodyKLid\cf4 \strokec4  = \cf9 \strokec9 loftLid\cf4 \strokec4 .bodies.item(\cf8 \strokec8 0\cf4 \strokec4 )\cb1 \
\cb3         \cf9 \strokec9 bodyList\cf4 \strokec4 .\cf10 \strokec10 append\cf4 \strokec4 (\cf9 \strokec9 bodyKLid\cf4 \strokec4 )    \cb1 \
\
\cb3     \cf5 \strokec5 return\cf4 \strokec4  \cf9 \strokec9 bodyList\cf4 \cb1 \strokec4 \
\
\
\pard\pardeftab720\sl360\partightenfactor0
\cf2 \cb3 \strokec2 ##### Main code #####\cf4 \cb1 \strokec4 \
\
\cf2 \cb3 \strokec2 # Create Fusion document \cf4 \cb1 \strokec4 \
\pard\pardeftab720\sl360\partightenfactor0
\cf9 \cb3 \strokec9 app\cf4 \strokec4  = \cf6 \strokec6 adsk\cf4 \strokec4 .\cf6 \strokec6 core\cf4 \strokec4 .\cf6 \strokec6 Application\cf4 \strokec4 .\cf10 \strokec10 get\cf4 \strokec4 ()\cb1 \
\cf9 \cb3 \strokec9 ui\cf4 \strokec4  = \cf9 \strokec9 app\cf4 \strokec4 .\cf9 \strokec9 userInterface\cf4 \cb1 \strokec4 \
\cf9 \cb3 \strokec9 doc\cf4 \strokec4  = \cf9 \strokec9 app\cf4 \strokec4 .\cf9 \strokec9 documents\cf4 \strokec4 .\cf10 \strokec10 add\cf4 \strokec4 (\cf6 \strokec6 adsk\cf4 \strokec4 .\cf6 \strokec6 core\cf4 \strokec4 .\cf6 \strokec6 DocumentTypes\cf4 \strokec4 .\cf9 \strokec9 FusionDesignDocumentType\cf4 \strokec4 )\cb1 \
\cf9 \cb3 \strokec9 design\cf4 \strokec4  = \cf9 \strokec9 app\cf4 \strokec4 .\cf9 \strokec9 activeProduct\cf4 \cb1 \strokec4 \
\
\pard\pardeftab720\sl360\partightenfactor0
\cf2 \cb3 \strokec2 # Create sketch, construction plane, loft, and pattern objects\cf4 \cb1 \strokec4 \
\pard\pardeftab720\sl360\partightenfactor0
\cf9 \cb3 \strokec9 rootComp\cf4 \strokec4  = \cf9 \strokec9 design\cf4 \strokec4 .rootComponent\cb1 \
\cf9 \cb3 \strokec9 sketchObjs\cf4 \strokec4  = \cf9 \strokec9 rootComp\cf4 \strokec4 .sketches\cb1 \
\cf9 \cb3 \strokec9 cPlaneObjs\cf4 \strokec4  = \cf9 \strokec9 rootComp\cf4 \strokec4 .constructionPlanes\cb1 \
\cf9 \cb3 \strokec9 loftFeats\cf4 \strokec4  = \cf9 \strokec9 rootComp\cf4 \strokec4 .features.loftFeatures\cb1 \
\
\pard\pardeftab720\sl360\partightenfactor0
\cf2 \cb3 \strokec2 ##Make Kresling structure\cf4 \cb1 \strokec4 \
\pard\pardeftab720\sl360\partightenfactor0
\cf9 \cb3 \strokec9 Kresling\cf4 \strokec4  = \cf10 \strokec10 makeKreslingBody\cf4 \strokec4 (\cf9 \strokec9 cPlaneObjs\cf4 \strokec4 ,\cf9 \strokec9 loftFeats\cf4 \strokec4 ,\cf7 \strokec7 P\cf4 \strokec4 ,\cf7 \strokec7 N\cf4 \strokec4 ,\cf9 \strokec9 t\cf4 \strokec4 ,\cf7 \strokec7 L1\cf4 \strokec4 ,\cf9 \strokec9 alpha\cf4 \strokec4 ,\cf9 \strokec9 makeBase\cf4 \strokec4 )\cb1 \
\
\
}