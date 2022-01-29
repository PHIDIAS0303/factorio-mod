import json
import PySimpleGUI
import os
import re
import shutil
import sqlite3
import zlib

# Settings
# Edition, Version, Revision
setting_edition = 4
setting_revision = 5
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
# Database Filename
setting_app_database = 'main.db'

# TODO List
'''
[1]
compare mod version.

[2]
import json file.

[3]
Switch mod profiles using sqlite or other means.
Only by switching all to False then those to True.

[4]
Save the current profile.

[5]
Import or Export Strings or files.
'''

'''
string = '1234567890'
compressed_string = zlib.compress(bytes(string, 'utf-8'), zlib.Z_BEST_COMPRESSION)

print(string)
print(compressed_string)
print((zlib.decompress(compressed_string)).decode('utf-8'))

'''

# Create Database if inital launch.
with sqlite3.connect(setting_app_database) as setting_app_database_connection:
    setting_app_database_cursor = setting_app_database_connection.cursor()

    try:
        setting_app_database_cursor.execute('CREATE TABLE profile (id INTEGER, data TEXT)')
    except sqlite3.OperationalError:
        pass

    setting_app_database_connection.commit()

# Main Application
def graphical_interface():
    graphical_layout = [[]]
    address_default = os.path.expanduser('~')
    address_default = address_default.replace('\\', '/')
    address_mod_source = address_default + '/AppData/Roaming/Factorio/mods/'
    address_destination = address_default + '/Desktop/Factorio/'

    graphical_layout.append([PySimpleGUI.Text('Mod List Address:', font=(setting_font, setting_font_size))])
    graphical_layout.append([PySimpleGUI.Input(address_mod_source, key='address_mod_source_folder', font=(setting_font, setting_font_size)), PySimpleGUI.FolderBrowse(target='address_mod_source_folder', initial_folder=address_mod_source, font=(setting_font, setting_font_size))])
    graphical_layout.append([PySimpleGUI.Text('Target Address:', font=(setting_font, setting_font_size))])
    graphical_layout.append([PySimpleGUI.Input(address_destination, key='address_destination_folder', font=(setting_font, setting_font_size)), PySimpleGUI.FolderBrowse(target='address_destination_folder', initial_folder=address_destination, font=(setting_font, setting_font_size))])
    graphical_layout.append([PySimpleGUI.Button('Start Copy', font=(setting_font, setting_font_size))])    

    def copy_mod(address_mod_list, address_mod_copy, graphical_window):
        with open(address_mod_list + 'mod-list.json') as json_file:
            mod_list_json = json.load(json_file)
            json_file.close()

        mod_list_json = mod_list_json['mods']

        mod_list = []
        mod_result = []

        for i in range(len(mod_list_json)):
            if mod_list_json[i]['enabled'] == True:
                mod_list.append(re.sub('[-_ ]', '', mod_list_json[i]['name'].lower()))

        if mod_list == ['base']:
            PySimpleGUI.popup_ok('Mods are not selected in game.', title=setting_title, font=(setting_font, setting_font_size))
            return

        mod_file_list = next(os.walk(address_mod_list), (None, None, []))[2]
        mod_file_list_compare = []

        for i in range(len(mod_file_list)):
            mod_file_list_compare.append(re.sub('[-_.\s\d]', '', mod_file_list[i].replace('.zip', '').lower()))

        for i in range(len(mod_list)):
            for j in range(len(mod_file_list_compare)):
                if re.search(str('^.*(' + str(mod_list[i]) + ').*$'), str(mod_file_list_compare[j])):
                    mod_result.append([mod_list[i], mod_file_list[j]])

        if not os.path.exists(address_mod_copy):
            os.mkdir(address_mod_copy, 0o666)

        graphical_layout = [[]]
        graphical_layout.append([PySimpleGUI.Text('Progress:', font=(setting_font, setting_font_size))])
        graphical_layout.append([PySimpleGUI.Text('', key='info', font=(setting_font, setting_font_size))])
        graphical_layout.append([PySimpleGUI.ProgressBar(len(mod_result), orientation='h', size=(100, 20), key='progress_bar')])
        graphical_layout.append([PySimpleGUI.Cancel(font=(setting_font, setting_font_size))])
        graphical_window.hide()
        graphical_window2 = PySimpleGUI.Window(setting_title, layout=graphical_layout, size=(setting_window_size[0], setting_window_size[1]), resizable=False, finalize=True)

        for i in range(len(mod_result)):
            graphical_window2['info'].update(str('Copying (' + str(i + 1) + '/' + str(len(mod_result)) + ') ' + str(mod_result[i][0])))
            graphical_window2['progress_bar'].UpdateBar(i + 1)
            # shutil.copyfile(str(address_mod_list) + str(mod_result[i][1]), str(address_mod_copy) + str(mod_result[i][1]))
            
            event, values = graphical_window2.Read(timeout=10)

            if event in (None, 'Exit', 'Cancel', PySimpleGUI.WIN_CLOSED): 
                graphical_window2.close()
                return

        PySimpleGUI.popup_ok('Tasks have completed successfully.', title=setting_title, font=(setting_font, setting_font_size))
        graphical_window2.close()

    graphical_window = PySimpleGUI.Window(setting_title, layout=graphical_layout, size=(setting_window_size[0], setting_window_size[1]), resizable=False, finalize=True)

    while True:
        event, values = graphical_window.Read(timeout=100)

        if event in (None, 'Exit', 'Cancel', PySimpleGUI.WIN_CLOSED): 
            graphical_window.close()
            break

        elif event in ('Start Copy'):
            copy_mod(str(values['address_mod_source_folder']) + '/', str(values['address_destination_folder'])+ '/', graphical_window)
            graphical_window.close()
            break

graphical_interface()
