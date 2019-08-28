# USAGE
# python trackingscript.py --video videos/crop.mov --tracker csrt

# import the necessary packages
from imutils.video import VideoStream
import numpy as np
import imutils
import time
import cv2
import datetime
import os.path
import PySimpleGUI as sg
from tracking.trackingmod import MultiTissueTracker


class Track():
    def __init__(self):
        # GUI Interface Start
        print('Startup up...')

        layout = [
            [sg.Text('Please enter the following parameters')],
            [sg.Text('Video Path', size=(25, 1)), sg.InputText(
                key='VIDEOPATH'), sg.FileBrowse()],
            [sg.Text('Save to:', size=(25, 1)), sg.InputText(
                key='SAVE'), sg.FolderBrowse()],
            [sg.Text('First Tissue', size=(25, 1)),
             sg.InputText(key='FIRSTTISSUE')],
            [sg.Text('Last Tissue', size=(25, 1)),
             sg.InputText(key='LASTTISSUE')],
            [sg.Text('Pacing Frequency', size=(25, 1)),
             sg.InputText(key='PACINGFREQ')],
            [sg.Text('Electrode Spacing', size=(25, 1)),
             sg.InputText('0', key='ELECTRODESPACING')],
            [sg.Text('Pacing Voltage', size=(25, 1)),
             sg.InputText('12', key='PACINGVOLT')],
            [sg.Text('Excitation Threshold', size=(25, 1)),
             sg.InputText('12', key='EXCITTHRESH')],
            [sg.Text('Calibration Distance (mm)', size=(25, 1)),
             sg.InputText('18', key='CALIBDIST')],
            [sg.Text('Frame Width', size=(25, 1)), sg.InputText(
                '2000', key='FRAMEWIDTH')],
            [sg.Text('Group Name', size=(25, 1)), sg.InputText(
                'need to work on this', key='GROUPNAME')],
            [sg.Text('Group Number', size=(25, 1)),
             sg.InputText('this too', key='GROUPNUMBER')],
            [sg.Text('Tracker', size=(25, 1)), sg.Drop(key='TRACKER', values=(
                'csrt', 'kcf', 'mil', 'boosting', 'tld', 'medianflow', 'mosse'),
                size=(25, 1))],
            [sg.Submit(), sg.Cancel()]
        ]
        # Show to GUI window
        window = sg.Window('Tracking GUI', layout)
        # Read the window, values is a dictionary with the values
        event, values = window.Read()
        window.Close()

        # Turn the numebrs into numbers instead of text
        intergerize = ['FIRSTTISSUE', 'LASTTISSUE', 'FRAMEWIDTH']
        floaterize = ['PACINGFREQ', 'ELECTRODESPACING',
                      'PACINGVOLT', 'EXCITTHRESH', 'CALIBDIST']

        for item in intergerize:
            values[item] = int(values[item])
        for item in floaterize:
            values[item] = float(values[item])

        # Call the tracker. From trackingmod
        MultiTissueTracker(values)
