###########################
#			  #
#  LAYOUT CAMERA TOOLKIT  #
#			  #
#  by Michael Tzetzias    #
#  			  #
###########################


1. Intro

LCT is a toolkit to aid the Layout Artists to place the cameras in the scene according to the storyboard and facilitate the process to manage them. 

The toolkit provides:
Create Cameras:
	- Directly input the camera’s name
	- Create camera from the current view
	- Choose lense
	- Create a Focus Target attached to the camera
	- Delete
Manage Cameras:
	- Select them
	- Cycle through them
	- View through selected
	- Enable/Disable Frustum

2. How to install

i. Drag and drop the "layout-camera-toolkit" folder in 'C:\Users\{your username}\Documents\maya\scripts'

ii. Open Maya and in the script editor, paste the following script (replace {your username} here as well):

import sys
sys.path.append(r"C:\Users\{your username}\Documents\maya\scripts\layout-camera-toolkit")

import lct

import importlib

importlib.reload(lct)

iii. Save the script in your shelf. On the script editor, go to File > Save script on shelf.

iv. That's it. Enjoy using it.

v. Very important. Provide feedback with your experience of the tool. It is very important that this tool can aid fellow artists.
Any feedback is welcome and it will help me to improve this tool.

Please send me your feedback using LCT Feedback and send it to michael@lovelymammoth.com

Thank you!






