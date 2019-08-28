import PySimpleGUI as sg
from analysis.analyzeGUI import Analyze as  ag
from tracking.trackingGUI import Track as tg



layout = [
    [sg.Text('What would you like to Do', size=(25, 1)), sg.Drop(key='DO?', values=(
        'track', 'analyze'), size = (25, 1))],
    [sg.Submit(), sg.Cancel()]
]

window = sg.Window('Startup GUI', layout)
event, expar = window.Read()

if expar['DO?'] == 'track':
    tg()
elif expar['DO?'] == 'analyze':
    ag()
