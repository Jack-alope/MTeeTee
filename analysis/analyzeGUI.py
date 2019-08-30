from analysis.graphanalysis import GraphAnalyze
import PySimpleGUI as sg


class Analyze():
    def __init__(self):

        layout = [
            [sg.Text('Please enter the following parameters')],
            [sg.Text('Bioreactor Type', size=(25, 1)), sg.Drop(key='BIO', values=(
                'multitissue', 'eht'),
                size=(25, 1))],
            [sg.Text('Folder:', size=(25, 1)), sg.InputText(
                key='FOLDER'), sg.FolderBrowse()],
            [sg.Text('Percentage Threshold', size=(25, 1)),
             sg.InputText('.8', key='THRESWIDTH')],
            [sg.Text('Youngs Modulus', size=(25, 1)),
             sg.InputText('1.33', key='YOUNGS')],
            [sg.Text('Distance between posts', size=(25, 1)),
             sg.InputText('10', key='MAXDISP')],
            [sg.Text('Peak Detection Sensitivity', size=(25, 1)),
             sg.InputText('.5', key='PEAKSENS')],
            [sg.Text('Peak Detection Difference', size=(25, 1)),
             sg.InputText('15', key='PEAKDIST')],
            [sg.Text('Peak Smoothing Polynomial', size=(25, 1)),
             sg.InputText('4', key='PEAKPOLY')],
            [sg.Text('Peak Smoothing Window Size', size=(25, 1)),
             sg.InputText('13', key='PEAKWIND')],
            [sg.Text('Time Min', size=(25, 1)),
             sg.InputText('0', key='TIMEMIN')],
            [sg.Text('Time Max', size=(25, 1)),
             sg.InputText('0', key='TIMEMAX')],
            [sg.Submit(), sg.Cancel()]
        ]

        window = sg.Window('Analyze GUI', layout)
        event, expar = window.Read()

        floaterizer = ['THRESWIDTH',
                       'YOUNGS', 'MAXDISP', 'PEAKSENS', 'PEAKDIST', 'TIMEMIN', 'TIMEMAX']
        intergerizer = ['PEAKPOLY', 'PEAKWIND']

        for item in floaterizer:
            expar[item] = float(expar[item])
        for item in intergerizer:
            expar[item] = int(expar[item])

        analyze = GraphAnalyze(expar)
