from bs4 import BeautifulSoup
import json
import PySimpleGUI
import os
import re
import shutil
import sqlite3
import urllib.request
import zlib

# Settings
# Edition, Version, Revision
setting_edition = 5
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
# Database Filename
setting_app_database = 'main.db'
# Setting HTML Agent Header
setting_html_agent_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}

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

address_default = os.path.expanduser('~')
address_default = address_default.replace('\\', '/')
address_mod_source = address_default + '/AppData/Roaming/Factorio/mods/'
address_destination = address_default + '/Desktop/Factorio/'

# Main Application
def mod_list(address_mod_source):
    with open(address_mod_source + 'mod-list.json') as json_file:
        mod_list_json = json.load(json_file)
        json_file.close()

    mod_list_json = mod_list_json['mods']
    mod_list_result = []

    for i in range(len(mod_list_json)):
        if (mod_list_json[i]['enabled'] == True):
            if not (mod_list_json[i]['name'] == 'base'):
                print('Looking up (' + str(i + 1) + '/' + str(len(mod_list_json)) + ') ' + str(mod_list_json[i]['name']))
                html_page = urllib.request.Request('https://mods.factorio.com/api/mods/' + str(mod_list_json[i]['name']).replace(' ', '%20'), headers=setting_html_agent_header)
                html_result = urllib.request.urlopen(html_page).read().decode('utf-8')
            
                html_soup = BeautifulSoup(html_result, 'html.parser')
                html_result = json.loads(html_soup.text)
                mod_list_result.append([html_result['title'], html_result['releases'][-1]['file_name'], html_result['releases'][-1]['download_url'], html_result['releases'][-1]['version'], html_result['releases'][-1]['info_json']['factorio_version']])

    return mod_list_result

def interface_event_pack_mod_list(address_mod_source, address_destination, mod_list_result):
    if not os.path.exists(address_destination):
        os.mkdir(address_destination, 0o666)

    for i in range(len(mod_list_result)):
        print('Copying (' + str(i + 1) + '/' + str(len(mod_list_result)) + ') ' + str(mod_list_result[i][0]))
        shutil.copyfile(str(address_mod_source) + str(mod_list_result[i][1]), str(address_destination) + str(mod_list_result[i][1]))

def graphical_interface():
    PySimpleGUI.set_options(element_padding=(0, 0))
    graphical_layout = [[]]
    menu_layout = [['File', ['Pack Mod List', 'Export String', 'Import String', 'Import JSON']], ['Profile', ['Load Profile', 'Save Profile']]]

    graphical_layout.append([PySimpleGUI.Menu(menu_layout, )])
    graphical_window = PySimpleGUI.Window(setting_title, layout=graphical_layout, size=(setting_window_size[0], setting_window_size[1]), resizable=False, finalize=True)

    while True:
        event, values = graphical_window.Read(timeout=100)

        if event in (None, 'Exit', 'Cancel', PySimpleGUI.WIN_CLOSED): 
            graphical_window.close()
            break
        elif event in ('Pack Mod List'):
            interface_event_pack_mod_list(address_mod_source, address_destination, mod_list(address_mod_source))

graphical_interface()
