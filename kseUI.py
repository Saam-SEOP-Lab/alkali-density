import PySimpleGUI as sg
import pyvisa as visa
import kseDataCollection as dc
import time


sg.theme('Light Blue 2')

#rm = visa.ResourceManager()
#resources = []
#for r in rm.list_resources():
#    resources.append(r)

#keysight_select = sg.Combo(resources, expand_x=True, enable_events=False, readonly=True, key='KeysightLocation')
#dmm_select = sg.Combo(resources, expand_x=True, enable_events=False, readonly=True, key='DMMLocation')


#layout = [
#    [sg.Text('Select your experimental parameters')],
#    [sg.Text('Trigger Count'), sg.InputText(key='TriggerCount')],
#    [sg.Text('Collection Time (s)'), sg.InputText(key='CollectionTime')],
#    [sg.Text('Raw Data Filepath'), sg.FolderBrowse(key='RawDataPath')],
#    [sg.Submit(), sg.Cancel()]
#]

#window = sg.Window('Testing things', layout)


#while True:
#    event, values = window.read()
#    print(event, values)

#    if (event == 'Submit'):
#        dc.collectKSEData(float(values['TriggerCount']), float(values['CollectionTime']), values['RawDataPath'])

#    if event in(sg.WINDOW_CLOSED, 'Exit', 'Cancel'):
#        break

#window.close()

# My function that takes a long time to do...
def my_long_operation(vals):
    dc.collectKSEData(float(vals['TriggerCount']), float(vals['CollectionTime']), vals['RawDataPath'])
    return 'My return value'


def main():
    layout = [
    [sg.Text('Select your experimental parameters')],
    [sg.Text('Trigger Count'), sg.InputText(key='TriggerCount')],
    [sg.Text('Collection Time (s)'), sg.InputText(key='CollectionTime')],
    [sg.Text('Raw Data Filepath'), sg.FolderBrowse(key='RawDataPath')],
    [sg.Submit(), sg.Cancel()],
    [sg.Text('Output: '), sg.Multiline(key='-OUTPUT-', write_only=True, size=(60,10), reroute_stdout=True)]
]

    window = sg.Window('Threading?', layout, keep_on_top=True)

    while True:             # Event Loop
        event, values = window.read()
        if event in(sg.WINDOW_CLOSED, 'Exit', 'Cancel'):
            break

        window['-OUTPUT-'].update(f'{event, values}')  # show the event and values in the window
        window.refresh()                            # make sure it's shown immediately

        if event  == 'Submit':
            # Let PySimpleGUI do the threading for you...
            window.perform_long_operation(my_long_operation(values), '-OPERATION DONE-')
        elif event  == '-OPERATION DONE-':
            window['-OUTPUT-'].update(f'DONE')
            window.refresh()                            # make sure it's shown immediately



    window.close()

if __name__ == '__main__':
    main()