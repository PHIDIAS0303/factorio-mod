import base64
from bs4 import BeautifulSoup
import datetime
import json
import math
import os
import PySimpleGUI
import shutil
import time
import urllib.request

'''
import errno
import hashlib
import socket
import zlib
'''

# Title
setting_app_title = 'APERX MOD COPY'
# Settings
# Edition, Version, Revision
setting_edition = 20221112
setting_revision = 2
setting_version = str(setting_edition) + '.' + str(setting_revision)
setting_app_title = setting_app_title + ' ' + setting_version
# Timezone
setting_app_timezone = 9
# Console Debug Logging
setting_mode_debug = True
# Command Prefix
setting_command_prefix = ['.', '!', '/']
# Font
# BIZ UDPGothic, Microsoft JhengHei
setting_font = ['BIZ UDPGothic', 'Microsoft JhengHei']
# Font Size
setting_font_size = 14
# Factorio Version
setting_factorio_version = '1.1'
# graphical_window Size
setting_window_size = [1440, 810]
# Resolution (Primary Screen)
# If Resolution > Window Size
# Make window center
setting_resolution = (1920, 1080)
# Color
# Background
setting_color = ['#222831', '#14FFEC', '#FF9F1C']

PySimpleGUI.LOOK_AND_FEEL_TABLE['CustomTheme'] = {'BACKGROUND': setting_color[0], 'TEXT': setting_color[2], 'INPUT': setting_color[0], 'TEXT_INPUT': setting_color[2], 'SCROLL': setting_color[1], 'BUTTON': (setting_color[1], setting_color[0]), 'PROGRESS': (setting_color[1], setting_color[0]), 'BORDER': 1, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0, }
PySimpleGUI.theme('CustomTheme')

setting_address_mod_default = os.path.expanduser('~')
setting_address_mod_default = setting_address_mod_default.replace('\\', '/')
setting_address_mod_source = setting_address_mod_default + '/AppData/Roaming/Factorio/mods/'
setting_address_mod_destination = setting_address_mod_default + '/Desktop/Factorio/'

def get_time():
    return str((datetime.datetime.utcnow() + datetime.timedelta(hours=setting_app_timezone)).strftime('%Y-%m-%d %H:%M:%S'))


def pprint(level, debug, message):
    level = level.upper()

    if debug:
        if level == 'DEBUG':
            print('\x1b[38;21m' + str(message) + '\x1b[0m')

        if level == 'INFO':
            print('\x1b[38;21m' + str(message) + '\x1b[0m')

        elif level == 'WARN':
            print('\x1b[33;21m' + str(message) + '\x1b[0m')

        elif level == 'ERROR' or level == 'CRITICAL':
            print('\x1b[31;21m' + str(message) + '\x1b[0m')


def standard_case(string):
    if (string is None) or string == '':
        return string

    else:
        string = string.lower()
        string = string.split(' ')

        for i in range(len(string)):
            string[i] = list(string[i])
            string[i][0] = string[i][0].upper()

            if '-' in string[i]:
                string[i][string[i].index('-') + 1] = string[i][string[i].index('-') + 1].upper()

            string[i] = ''.join(string[i])

        return ' '.join(string)


def factorio_mod_lookup(mod_name: str):
    setting_html_agent_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}
    html_page = urllib.request.Request('https://mods.factorio.com/api/mods/' + mod_name.replace(' ', '%20'), headers=setting_html_agent_header)
    html_result = urllib.request.urlopen(html_page).read().decode('utf-8')
    html_soup = BeautifulSoup(html_result, 'html.parser')
    html_result = json.loads(html_soup.text)
    mod_selection = []

    for i in range(len(html_result['releases'])):
        if html_result['releases'][i]['info_json']['factorio_version'] == setting_factorio_version:
            html_result['releases'][i]['released_at'] = html_result['releases'][i]['released_at'].replace('T', ' ').replace('Z', '')
            mod_selection.append(html_result['releases'][i])

    mod_selection = sorted(mod_selection, key=lambda x: (time.mktime(datetime.datetime.strptime(x['released_at'], '%Y-%m-%d %H:%M:%S.%f').timetuple())), reverse=True)[0]
    mod_selection['title'] = html_result['title']
    mod_selection['summary'] = html_result['summary']
    return mod_selection


def graphical_interface_main():
    graphical_layout = []
    graphical_layout.append([PySimpleGUI.Text(text=get_time(), key='text_clock', relief=PySimpleGUI.RELIEF_RIDGE, size=(18, 1), pad=(0, 0), font=(setting_font[0], setting_font_size))])
    graphical_layout.append([PySimpleGUI.Text(text='', size=(20, 1), pad=(0, 0), font=(setting_font[0], setting_font_size))])
    graphical_layout.append([PySimpleGUI.Text('Mod List Address:', font=(setting_font[0], setting_font_size))])
    graphical_layout.append([PySimpleGUI.Input(setting_address_mod_source, key='address_mod_source_folder', font=(setting_font[0], setting_font_size)), PySimpleGUI.FolderBrowse(target='address_mod_source_folder', initial_folder=setting_address_mod_source, font=(setting_font[0], setting_font_size))])
    graphical_layout.append([PySimpleGUI.Text('Target Address:', font=(setting_font[0], setting_font_size))])
    graphical_layout.append([PySimpleGUI.Input(setting_address_mod_destination, key='address_mod_destination_folder', font=(setting_font[0], setting_font_size)), PySimpleGUI.FolderBrowse(target='address_mod_destination_folder', initial_folder=setting_address_mod_destination, font=(setting_font[0], setting_font_size))])
    graphical_layout.append([PySimpleGUI.Button('Start Copy', font=(setting_font[0], setting_font_size), key='interface_event_copy_mod_list')])
    graphical_layout.append([PySimpleGUI.Text(text='', size=(20, 1), pad=(0, 0), font=(setting_font[0], setting_font_size))])
    graphical_layout.append([PySimpleGUI.Text(text='Progress', size=(40, 1), pad=(0, 0), font=(setting_font[0], setting_font_size))])
    graphical_layout.append([PySimpleGUI.Text(text='', size=(20, 1), pad=(0, 0), font=(setting_font[0], setting_font_size))])
    graphical_layout.append([PySimpleGUI.Text(text='', size=(60, 1), key='interface_text_progress_info', pad=(0, 0), font=(setting_font[0], setting_font_size))])
    graphical_layout.append([PySimpleGUI.ProgressBar(max_value=1, orientation='h', size=(60, 20), key='interface_progress_bar')])
    graphical_layout.append([PySimpleGUI.Text(text='', size=(20, 1), pad=(0, 0), font=(setting_font[0], setting_font_size))])
    graphical_window = PySimpleGUI.Window(title=setting_app_title, layout=graphical_layout, size=(setting_window_size[0], setting_window_size[1]), location=(int((setting_resolution[0] - setting_window_size[0]) / 2), int((setting_resolution[1] - setting_window_size[1] - 80) / 2)), resizable=False, finalize=True)

    while True:
        event, values = graphical_window.Read(timeout=100)
        graphical_window['text_clock'].update(value=get_time())

        if event in (None, 'Exit', 'Cancel', PySimpleGUI.WIN_CLOSED):
            graphical_window.close()
            break

        elif event in 'interface_event_copy_mod_list':
            if not os.path.exists(values['address_mod_destination_folder']):
                os.mkdir(values['address_mod_destination_folder'], 0o666)

            with open(values['address_mod_source_folder'] + 'mod-list.json') as json_file:
                mod_list_json = json.load(json_file)
                json_file.close()

            mod_list_json = mod_list_json['mods']
            mod_list_len = len(mod_list_json)
            mod_list_en = []

            for i in range(mod_list_len):
                if mod_list_json[i]['enabled']:
                    if not (mod_list_json[i]['name'] == 'base'):
                        mod_list_en.append(mod_list_json[i])

            graphical_window['interface_progress_bar'].UpdateBar(0, max=len(mod_list_en))

            for i in range(len(mod_list_en)):
                mod_selection = factorio_mod_lookup(mod_list_en[i]['name'])
                shutil.copyfile(str(values['address_mod_source_folder']) + str(mod_selection['file_name']), str(values['address_mod_destination_folder']) + str(mod_selection['file_name']))

                graphical_window['interface_text_progress_info'].update(str(i) + ' / ' + str(len(mod_list_en)) + ' - ' + str(mod_selection['title']))
                graphical_window['interface_progress_bar'].UpdateBar(i)

            graphical_window['interface_text_progress_info'].update('COMPLETED')


graphical_interface_main()
