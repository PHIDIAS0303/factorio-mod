import os
import re
import json
import shutil
import PySimpleGUI as gui

# Edition, Version, Revision
setting_edition = 4
setting_revision = 1
setting_version = str(setting_edition) + '.' + str(setting_revision)
# Title
setting_title = 'EXP MOD COPY'
setting_title = setting_title + ' ' + setting_version
# Font
setting_font = 'Arial'
# Font Size
setting_font_size = 14
# graphical_window Size
setting_window_size = [650, 250]

def interface():
    graphical_layout = [[]]
    address_default = os.path.expanduser('~')
    address_default = address_default.replace('\\', '/')
    address_mod_source = address_default + '/AppData/Roaming/Factorio/mods/'
    address_destination = address_default + '/Desktop/Factorio/'

    graphical_layout.append([gui.Text('Mod List Address:', font=(setting_font, setting_font_size))])
    graphical_layout.append([gui.Input(address_mod_source, key='address_mod_source_folder', font=(setting_font, setting_font_size)), gui.FolderBrowse(target='address_mod_source_folder', initial_folder=address_mod_source, font=(setting_font, setting_font_size))])
    graphical_layout.append([gui.Text('Target Address:', font=(setting_font, setting_font_size))])
    graphical_layout.append([gui.Input(address_destination, key='address_destination_folder', font=(setting_font, setting_font_size)), gui.FolderBrowse(target='address_destination_folder', initial_folder=address_destination, font=(setting_font, setting_font_size))])
    graphical_layout.append([gui.Button('Start Copy', font=(setting_font, setting_font_size))])    

    def copy_mod(address_mod_list, address_mod_copy, graphical_window):
        with open(address_mod_list + 'mod-list.json') as json_file:
            mod_list_json = json.load(json_file)
            json_file.close()

        mod_list_json = mod_list_json['mods']

        mod_list = []
        mod_res = []

        for i in range(len(mod_list_json)):
            if mod_list_json[i]['enabled'] == True:
                mod_list.append(re.sub('[-_ ]', '', mod_list_json[i]['name'].lower()))

        if mod_list == ['base']:
            gui.popup_ok('Mods are not selected in game.', title=setting_title, font=(setting_font, setting_font_size))
            return

        mod_file_list = next(os.walk(address_mod_list), (None, None, []))[2]
        mod_file_list_compare = []

        for i in range(len(mod_file_list)):
            mod_file_list_compare.append(re.sub('[-_.\s\d]', '', mod_file_list[i].replace('.zip', '').lower()))

        for i in range(len(mod_list)):
            for j in range(len(mod_file_list_compare)):
                if re.search(str('^.*(' + str(mod_list[i]) + ').*$'), str(mod_file_list_compare[j])):
                    mod_res.append([mod_list[i], mod_file_list[j]])

        if not os.path.exists(address_mod_copy):
            os.mkdir(address_mod_copy, 0o666)

        graphical_layout = [[]]
        graphical_layout.append([gui.Text('Progress:', font=(setting_font, setting_font_size))])
        graphical_layout.append([gui.Text('', key='info', font=(setting_font, setting_font_size))])
        graphical_layout.append([gui.ProgressBar(len(mod_res), orientation='h', size=(100, 20), key='progress_bar')])
        graphical_layout.append([gui.Cancel(font=(setting_font, setting_font_size))])
        graphical_window.hide()
        graphical_window2 = gui.graphical_window(setting_title, graphical_layout=graphical_layout, size=(setting_window_size[0], setting_window_size[1]), resizable=False, finalize=True)

        for i in range(len(mod_res)):
            graphical_window2['info'].update(str('Copying (' + str(i + 1) + '/' + str(len(mod_res)) + ') ' + str(mod_res[i][0])))
            graphical_window2['progress_bar'].UpdateBar(i + 1)
            shutil.copyfile(str(address_mod_list) + str(mod_res[i][1]), str(address_mod_copy) + str(mod_res[i][1]))
            
            event, values = graphical_window2.Read(timeout=10)

            if event in (None, 'Exit', 'Cancel', gui.WIN_CLOSED): 
                graphical_window2.close()
                return

        gui.popup_ok('Tasks have completed successfully.', title=setting_title, font=(setting_font, setting_font_size))
        graphical_window2.close()

    graphical_window = gui.graphical_window(setting_title, graphical_layout=graphical_layout, size=(setting_window_size[0], setting_window_size[1]), resizable=False, finalize=True)

    while True:
        event, values = graphical_window.Read(timeout=100)

        if event in (None, 'Exit', 'Cancel', gui.WIN_CLOSED): 
            graphical_window.close()
            break

        elif event in ('Start Copy'):
            copy_mod(str(values['address_mod_source_folder']) + '/', str(values['address_destination_folder'])+ '/', graphical_window)
            graphical_window.close()
            break

interface()
