
<div align="center"><img src="icon/newicon.png"></div> <br>

<div align="center">
  <strong>M-Tee-Tee: Multi-Tissue-Tracker</strong>
</div>
<br>
<div align="center">
  This is a program designed to track n sets of defecting posts and perform a series of calculations to understand that motion. It is written in python and reies on opencv trackers. 
  <br>
  <br>
  Instructions below are for MacOS. <br>
  For linux the use source file and run python scripts from Terminal.  
  <br>
  For Windows I have no idea. 
</div> <br>

___
> [Setup](#setup) - [Updates](#updates) - [Usage](#usage) - [Tracking](#tracking) - [Analysis](#analysis)  

___

# Setup:

1. Make sure to have python 3 installed. Open terminal and type "python3". If you see this it is installed. 
![trackingGUI](icon/python3.png) 
If not, install python 3.7.4 from this link. [https://www.python.org/downloads/](https://www.python.org/downloads/)

2. Download the .dmg installer from the link below or from my github [releases page](https://github.com/Jack-alope/MTeeTee/releases)
- [Mac OS 10.12 or higher](https://github.com/Jack-alope/MTeeTee/releases/download/v0.0.3/MTeeTeeMacOS-10-12.dmg)
  - Uses the latest version of opencv
- Will add link for Mac OS 10.11
  - Uses opencv 3.4.2.16

4. Double click the dmg file and open the disk image. You should see something like this. 
![trackingGUI](icon/installer.png)

5. Drag the 'M-Tee-Tee' into the Applications folder. 

6. Double click 'SetupScript'. Let it run until you see [Process Completed]. 
- If it does not let you because of 'unidentified developer'.
  - Go to System Preferences --> Security and Privacy --> General. Click open anyway near bottom. 

7. Close all terminal windows and Eject MTeeTeeInstaller. You can also delete the dmg file.

8. You are now ready to launch M-Tee-Tee from the applications window. 

# Updates:

1. Download the latest release. Same as Setup except when you drag M-Tee-Tee to applications it will give you a warning, Click replace. 


# Usage:

1. Double click "M-Tee-Tee" to launch the program. 

2. The first screen will be the startupGUI. 
You have two choices.
- Choose "track" to launch the tracking part of this program and generate data.  
- Choose "analyze" if you have already produced data for the deflections you want and are ready to analyze. 
![startupGUI](icon/startupgui2.png)  

## Tracking:

Upon selecting "track" from the startupGUI this screen will appear. 
- Video path: Select browse and navigate to the video file you want to track.
- Save to: Select or create a folder in which you want the generated data to be saved to.
- First Tissue: The first tissue number you are going to track in this video. 
- Last Tissue: The last tissue you will select. Note, tissue in video must be in consecutive order. Or files renamed after. 
- Pacing Frequency: The frequency at which the tissues were paced. Note, for spontaneous the standard is 0.1
- Electrode Spacing**: Not Currently Used
- Excitation Threshold**: Not Currently Used
- Calibration Distance: The distance of the object you are going to calibrate too. 
- Frame Width: The size of the video frame to be displayed.
- Group Name**: Currently being worked on. 
- Group Number**: Currently being worked on. 
- Tracker: Which type of opencv tracker would you like to use. csrt gives best results while kcf is the fastest. 
![trackingGUI](icon/trackinggui.png)  
1. Once you submit a frame will pop, this is a 6 tissue example. 
![trackingGUI](icon/trackstart.png) 
2. Immediately press 'c' and draw a calibration line the length that you inputted in the GUI. Press enter. 
![trackingGUI](icon/calib.png) 
3. Press 'l'. Draw cross section for first tissue. 
![trackingGUI](icon/crosssect.png) 
Press enter. Repeat for each tissue (Don't press 'l' again, just draw line and enter.)    
4. Press 's'. Draw a box around the first post. 
![trackingGUI](icon/post1.png) 
Press enter. 
5. Draw a box around the second post.
![trackingGUI](icon/post2.png) 
Press enter. Repeat steps 4 and 5 for each tissue (Don't press 's' again, just draw boxes and hit enter.)  
6. This is what it should look like when posts are being tracked. If no green boxes are displayed you didnt select the posts. 
![trackingGUI](icon/tracking.png) 
7. The data will be saved to the folder you specified. A csv and txt file are being produced for each tissue. 

## Analysis:

Upon selecting "analyze" this screen will appear. 
- Bioreactor Type: Determines what information is needed for post and tissue height
  - If "eht" no height file is required as post and tissue heights are constant and already known. 
  - If "multitissue" a Heights.csv file will need to be provided, an example will be in this repository. 
- Folder: The folder that you previously generated is. This is also where the heightfile would be saved to. 
- Percentage Threshold**: Increase this if basepoint or endpoint is too high (Between 0-1)
- Post Radius: Will Be deleted, based on bioreactor type. 
- Youngs modulus: For the mold material, standard 1.33 MPa.
- Distance between posts**: How far away are the posts from each other. 
- Peak Setection Sens: The lower the number the more sensitive (Between 0-1).
- Peak Detection Diff: Minimum distance peaks can be from each other. 
- Peak Smoothing Poly: What degree polynomial should it use to smooth the data, higher is smoother but can lose accuracy. 
- Peak Smoothing window: What size window should it use for the smoothing function. Larger is smoother. 
- Time min: Start time. Use 0 to start from beginning. 
- Time max: End Time. Use 0 to continue to end. 
![analyzeGUI](icon/analyzegui.png) 
When submitted it should produce a graph like this for each tissue. (Zoom will vary depending on number of points).
![analyzegraph](icon/analyzegraph.png) 
If you do not agree with the graph edit the settings in the GUI until you get it to capture the points to your liking.  
In the selected folder a summary.csv file is added with all of the calulcations. 

** Will be modified or deleted. 


