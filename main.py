import base64
from bs4 import BeautifulSoup
import datetime
import json
import PySimpleGUI
import os
import shutil
import sqlite3
import urllib.request
import zlib

# Settings
# Edition, Version, Revision
setting_edition = 20220201
setting_revision = 4
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
# Setting HTML Agent Header
setting_html_agent_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}

# TODO List
'''
[1]
compare mod version.

[2]
Switch mod profiles using sqlite or other means.
Only by switching all to False then those to True.
'''

# Create Database if inital launch.
with sqlite3.connect(setting_app_database) as setting_app_database_connection:
    setting_app_database_cursor = setting_app_database_connection.cursor()

    try:
        setting_app_database_cursor.execute('CREATE TABLE profile (id INTEGER, data TEXT)')
    except sqlite3.OperationalError:
        pass

    setting_app_database_connection.commit()

address_default = os.path.expanduser('~')
address_default = address_default.replace('\\', '/')
address_mod_source = address_default + '/AppData/Roaming/Factorio/mods/'
address_destination = address_default + '/Desktop/Factorio/'

# Main Application
def interface_event_pack_mod_list(graphical_window_1, address_mod_source, address_destination):
    if not os.path.exists(address_destination):
        os.mkdir(address_destination, 0o666)

    with open(address_mod_source + 'mod-list.json') as json_file:
        mod_list_json = json.load(json_file)
        json_file.close()

    mod_list_json = mod_list_json['mods']
    mod_list_json_len = len(mod_list_json)
    mod_list_result = []
    graphical_window_1['progress_bar'].UpdateBar(0, max=mod_list_json_len)

    for i in range(mod_list_json_len):
        if (mod_list_json[i]['enabled'] == True):
            if not (mod_list_json[i]['name'] == 'base'):
                html_page = urllib.request.Request('https://mods.factorio.com/api/mods/' + str(mod_list_json[i]['name']).replace(' ', '%20'), headers=setting_html_agent_header)
                html_result = urllib.request.urlopen(html_page).read().decode('utf-8')
                html_soup = BeautifulSoup(html_result, 'html.parser')
                html_result = json.loads(html_soup.text)
                mod_list_result.append([html_result['title'], html_result['releases'][-1]['file_name'], html_result['releases'][-1]['download_url'], html_result['releases'][-1]['version'], html_result['releases'][-1]['info_json']['factorio_version']])
        
        graphical_window_1['info'].update(str('Loading (' + str(i + 1) + '/' + str(mod_list_json_len) + ') ' + str(html_result['title'])))
        graphical_window_1['progress_bar'].UpdateBar(i + 1)
    
    mod_list_result_len = len(mod_list_result)
    graphical_window_1['progress_bar'].UpdateBar(0, max=mod_list_result_len)

    for i in range(mod_list_result_len):
        graphical_window_1['info'].update(str('Copying (' + str(i + 1) + '/' + str(mod_list_result_len) + ') ' + str(mod_list_result[i][0])))
        graphical_window_1['progress_bar'].UpdateBar(i + 1)
        shutil.copyfile(str(address_mod_source) + str(mod_list_result[i][1]), str(address_destination) + str(mod_list_result[i][1]))

    PySimpleGUI.popup_ok('Mod copy completed successfully.', title=setting_title, font=(setting_font, setting_font_size))

def interface_event_export_string(graphical_window_1, address_mod_source, address_destination):
    with open(address_mod_source + 'mod-list.json') as json_file:
        mod_list_json = json.load(json_file)
        json_file.close()

    mod_list_json = mod_list_json['mods']
    mod_list_json_len = len(mod_list_json)
    mod_list_result = []
    graphical_window_1['progress_bar'].UpdateBar(0, max=mod_list_json_len)

    for i in range(mod_list_json_len):
        if (mod_list_json[i]['enabled'] == True):
            graphical_window_1['info'].update(str('Loading (' + str(i + 1) + '/' + str(mod_list_json_len) + ') ' + str(mod_list_json[i]['name'])))
            graphical_window_1['progress_bar'].UpdateBar(i + 1)
            mod_list_result.append(mod_list_json[i]['name'])
        
    mod_list_result = "\n".join(mod_list_result)
    mod_list_result = zlib.compress(mod_list_result.encode('UTF-8'), zlib.Z_BEST_COMPRESSION)
    mod_list_result = base64.b64encode(mod_list_result)
    mod_list_result = mod_list_result.decode('UTF-8')
    datetime_now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)

    with open(str(address_destination) + '/exp_mod_string_export_' + str(datetime_now.strftime('%Y%m%d_%H%M%S')) + '.txt', 'w') as file:
        file.write(mod_list_result)

    PySimpleGUI.popup_ok('Mod string exported successfully.', title=setting_title, font=(setting_font, setting_font_size))

def interface_event_import_string(graphical_window_1, address_mod_source, address_string_source):
    with open(address_mod_source + 'mod-list.json') as json_file:
        mod_list_json = json.load(json_file)
        json_file.close()

    with open(address_string_source, 'r') as string_file:
        mod_list_string = string_file.read()
    
    mod_list_result = mod_list_string.encode('UTF-8')
    mod_list_result = base64.b64decode(mod_list_result)
    mod_list_result = zlib.decompress(mod_list_result).decode('UTF-8')
    mod_list_result = mod_list_result.split('\n')
    
    mod_list_json = mod_list_json['mods']
    mod_list_json_len = len(mod_list_json)
    mod_list_json_name = [i['name'] for i in mod_list_json]
    mod_list_new_len = len(list(set(mod_list_json_name + mod_list_result)))
    graphical_window_1['progress_bar'].UpdateBar(0, max=mod_list_json_len)

    for i in range(mod_list_json_len):
        if mod_list_json[i]['name'] in mod_list_result:
            mod_list_json[i]['enabled'] = True
        else:
            mod_list_json[i]['enabled'] = False

        graphical_window_1['info'].update(str('Loading (' + str(i + 1) + '/' + str(mod_list_new_len) + ') ' + str(mod_list_json[i]['name'])))
        graphical_window_1['progress_bar'].UpdateBar(i + 1)

    mod_list_json[0]['enabled'] = True
    mod_list_json = {'mods':mod_list_json}

    with open(str(address_mod_source) + '/mod-list.json', 'w') as file:
        json.dump(mod_list_json, file, indent=2)

    PySimpleGUI.popup_ok('Mod list synced with string successfully.', title=setting_title, font=(setting_font, setting_font_size))

def graphical_interface():
    PySimpleGUI.set_options(element_padding=(0, 0))
    graphical_layout = [[]]
    menu_layout = [['File', ['Pack Mod List', 'String', ['Export String', 'Import String'], 'JSON', ['Import JSON']]], ['Profile', ['Load Profile', 'Save Profile']]]

    graphical_layout.append([PySimpleGUI.Menu(menu_layout)])
    graphical_layout.append([PySimpleGUI.Text('EXP Mod Management', font=(setting_font, setting_font_size))])
    graphical_window = PySimpleGUI.Window(setting_title, layout=graphical_layout, size=(setting_window_size[0], setting_window_size[1]), resizable=False, finalize=True)

    while True:
        event, values = graphical_window.Read(timeout=100)

        if event in (None, 'Exit', 'Cancel', PySimpleGUI.WIN_CLOSED): 
            graphical_window.close()
            break

        elif event in ('Pack Mod List'):
            graphical_layout_2 = [[]]
            graphical_layout_2.append([PySimpleGUI.Menu(menu_layout)])
            graphical_layout_2.append([PySimpleGUI.Text('Mod List Address:', font=(setting_font, setting_font_size))])
            graphical_layout_2.append([PySimpleGUI.Input(address_mod_source, key='address_mod_source_folder', font=(setting_font, setting_font_size)), PySimpleGUI.FolderBrowse(target='address_mod_source_folder', initial_folder=address_mod_source, font=(setting_font, setting_font_size))])
            graphical_layout_2.append([PySimpleGUI.Text('Target Address:', font=(setting_font, setting_font_size))])
            graphical_layout_2.append([PySimpleGUI.Input(address_destination, key='address_destination_folder', font=(setting_font, setting_font_size)), PySimpleGUI.FolderBrowse(target='address_destination_folder', initial_folder=address_destination, font=(setting_font, setting_font_size))])
            graphical_layout_2.append([PySimpleGUI.Button('Start Copy', font=(setting_font, setting_font_size), key='interface_button_event_pack_mod_list')])
            graphical_window.Hide()
            graphical_window_2 = PySimpleGUI.Window(setting_title, layout=graphical_layout_2, size=(setting_window_size[0], setting_window_size[1]), resizable=False, finalize=True)
            
            while True:
                event, values = graphical_window_2.Read(timeout=100)
                
                if event in (None, 'Exit', 'Cancel', PySimpleGUI.WIN_CLOSED): 
                    graphical_window_2.close()
                    graphical_window.UnHide()
                    break

                elif event in ('interface_button_event_pack_mod_list'):
                    graphical_layout_3 = [[]]
                    graphical_layout_3.append([PySimpleGUI.Text('Progress:', font=(setting_font, setting_font_size))])
                    graphical_layout_3.append([PySimpleGUI.Text('', key='info', font=(setting_font, setting_font_size))])
                    graphical_layout_3.append([PySimpleGUI.ProgressBar(1, orientation='h', size=(100, 20), key='progress_bar')])
                    graphical_window_2.close()
                    graphical_window_3 = PySimpleGUI.Window(setting_title, layout=graphical_layout_3, size=(setting_window_size[0], setting_window_size[1]), resizable=False, finalize=True)
                    interface_event_pack_mod_list(graphical_window_3, str(values['address_mod_source_folder']) + '/', str(values['address_destination_folder']) + '/')
                    graphical_window_3.close()
                    graphical_window.UnHide()
                    break

        elif event in ('Export String'):
            graphical_layout_2 = [[]]
            graphical_layout_2.append([PySimpleGUI.Menu(menu_layout)])
            graphical_layout_2.append([PySimpleGUI.Text('Mod List Address:', font=(setting_font, setting_font_size))])
            graphical_layout_2.append([PySimpleGUI.Input(address_mod_source, key='address_mod_source_folder', font=(setting_font, setting_font_size)), PySimpleGUI.FolderBrowse(target='address_mod_source_folder', initial_folder=address_mod_source, font=(setting_font, setting_font_size))])
            graphical_layout_2.append([PySimpleGUI.Text('Target Address:', font=(setting_font, setting_font_size))])
            graphical_layout_2.append([PySimpleGUI.Input(address_destination, key='address_destination_folder', font=(setting_font, setting_font_size)), PySimpleGUI.FolderBrowse(target='address_destination_folder', initial_folder=address_destination, font=(setting_font, setting_font_size))])
            graphical_layout_2.append([PySimpleGUI.Button('Export String', font=(setting_font, setting_font_size), key='interface_button_event_export_string')])
            graphical_window.Hide()
            graphical_window_2 = PySimpleGUI.Window(setting_title, layout=graphical_layout_2, size=(setting_window_size[0], setting_window_size[1]), resizable=False, finalize=True)
            
            while True:
                event, values = graphical_window_2.Read(timeout=100)
                
                if event in (None, 'Exit', 'Cancel', PySimpleGUI.WIN_CLOSED): 
                    graphical_window_2.close()
                    graphical_window.UnHide()
                    break

                elif event in ('interface_button_event_export_string'):
                    graphical_layout_3 = [[]]
                    graphical_layout_3.append([PySimpleGUI.Text('Progress:', font=(setting_font, setting_font_size))])
                    graphical_layout_3.append([PySimpleGUI.Text('', key='info', font=(setting_font, setting_font_size))])
                    graphical_layout_3.append([PySimpleGUI.ProgressBar(1, orientation='h', size=(100, 20), key='progress_bar')])
                    graphical_window_2.close()
                    graphical_window_3 = PySimpleGUI.Window(setting_title, layout=graphical_layout_3, size=(setting_window_size[0], setting_window_size[1]), resizable=False, finalize=True)
                    interface_event_export_string(graphical_window_3, str(values['address_mod_source_folder']) + '/',  str(values['address_destination_folder']) + '/')
                    graphical_window_3.close()
                    graphical_window.UnHide()
                    break

        elif event in ('Import String'):
            graphical_layout_2 = [[]]
            graphical_layout_2.append([PySimpleGUI.Menu(menu_layout)])
            graphical_layout_2.append([PySimpleGUI.Text('Mod List Address:', font=(setting_font, setting_font_size))])
            graphical_layout_2.append([PySimpleGUI.Input(address_mod_source, key='address_mod_source_folder', font=(setting_font, setting_font_size)), PySimpleGUI.FolderBrowse(target='address_mod_source_folder', initial_folder=address_mod_source, font=(setting_font, setting_font_size))])
            graphical_layout_2.append([PySimpleGUI.Text('String Address:', font=(setting_font, setting_font_size))])
            graphical_layout_2.append([PySimpleGUI.Input(address_destination, key='address_destination_file', font=(setting_font, setting_font_size)), PySimpleGUI.FileBrowse(target='address_destination_file', initial_folder=address_destination, font=(setting_font, setting_font_size), file_types=(("Text Files", "*.txt"), ))])
            graphical_layout_2.append([PySimpleGUI.Button('Import String', font=(setting_font, setting_font_size), key='interface_button_event_import_string')])
            graphical_window.Hide()
            graphical_window_2 = PySimpleGUI.Window(setting_title, layout=graphical_layout_2, size=(setting_window_size[0], setting_window_size[1]), resizable=False, finalize=True)
            
            while True:
                event, values = graphical_window_2.Read(timeout=100)
                
                if event in (None, 'Exit', 'Cancel', PySimpleGUI.WIN_CLOSED): 
                    graphical_window_2.close()
                    graphical_window.UnHide()
                    break

                elif event in ('interface_button_event_import_string'):
                    graphical_layout_3 = [[]]
                    graphical_layout_3.append([PySimpleGUI.Text('Progress:', font=(setting_font, setting_font_size))])
                    graphical_layout_3.append([PySimpleGUI.Text('', key='info', font=(setting_font, setting_font_size))])
                    graphical_layout_3.append([PySimpleGUI.ProgressBar(1, orientation='h', size=(100, 20), key='progress_bar')])
                    graphical_window_2.close()
                    graphical_window_3 = PySimpleGUI.Window(setting_title, layout=graphical_layout_3, size=(setting_window_size[0], setting_window_size[1]), resizable=False, finalize=True)
                    interface_event_import_string(graphical_window_3, str(values['address_mod_source_folder']) + '/',  str(values['address_destination_file']))
                    graphical_window_3.close()
                    graphical_window.UnHide()
                    break

graphical_interface()
