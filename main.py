import os
import re
import json
import shutil
import PySimpleGUI as gui

# Edition, Version, Revision
setting_edition = 3
setting_revision = 6
setting_version = str(setting_edition) + '.' + str(setting_revision)
# Title
setting_title = 'EXP MOD COPY'
setting_title = setting_title + ' ' + setting_version
# Font
setting_font = 'Arial'
# Font Size
setting_font_size = 14
# Window Size
setting_window_size = [650, 250]

def interface():
    layout = [[]]
    default_addr = os.path.expanduser('~')
    default_addr = default_addr.replace('\\', '/')
    addr_mod_def = default_addr + '/AppData/Roaming/Factorio/mods/'
    addr_copy_def = default_addr + '/Desktop/Factorio/'

    layout.append([gui.Text('Mod List Address:', font=(setting_font, setting_font_size))])
    layout.append([gui.Input(addr_mod_def, key='addr_mod', font=(setting_font, setting_font_size)), gui.FolderBrowse(target='addr_mod', initial_folder=addr_mod_def, font=(setting_font, setting_font_size))])
    layout.append([gui.Text('Target Address:', font=(setting_font, setting_font_size))])
    layout.append([gui.Input(addr_copy_def, key='addr_copy', font=(setting_font, setting_font_size)), gui.FolderBrowse(target='addr_copy', initial_folder=addr_copy_def, font=(setting_font, setting_font_size))])
    layout.append([gui.Button('Start Copy', font=(setting_font, setting_font_size))])    

    def copy_mod(mod_list_addr, mod_copy_addr, window):
        with open(mod_list_addr + 'mod-list.json') as json_file:
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

        mod_file_list = next(os.walk(mod_list_addr), (None, None, []))[2]
        mod_file_list_compare = []

        for i in range(len(mod_file_list)):
            mod_file_list_compare.append(re.sub('[-_.\s\d]', '', mod_file_list[i].replace('.zip', '').lower()))

        for i in range(len(mod_list)):
            for j in range(len(mod_file_list_compare)):
                if re.search(str('^.*(' + str(mod_list[i]) + ').*$'), str(mod_file_list_compare[j])):
                    mod_res.append([mod_list[i], mod_file_list[j]])

        if not os.path.exists(mod_copy_addr):
            os.mkdir(mod_copy_addr, 0o666)

        layout = [[]]
        layout.append([gui.Text('Progress:', font=(setting_font, setting_font_size))])
        layout.append([gui.Text('', key='info', font=(setting_font, setting_font_size))])
        layout.append([gui.ProgressBar(len(mod_res), orientation='h', size=(100, 20), key='progress_bar')])
        layout.append([gui.Cancel(font=(setting_font, setting_font_size))])
        window.hide()
        window2 = gui.Window(setting_title, layout=layout, size=(setting_window_size[0], setting_window_size[1]), resizable=False, finalize=True)

        for i in range(len(mod_res)):
            window2['info'].update(str('Copying (' + str(i + 1) + '/' + str(len(mod_res)) + ') ' + str(mod_res[i][0])))
            window2['progress_bar'].UpdateBar(i + 1)
            shutil.copyfile(str(mod_list_addr) + str(mod_res[i][1]), str(mod_copy_addr) + str(mod_res[i][1]))
            
            event, values = window2.Read(timeout=10)

            if event in (None, 'Exit', 'Cancel', gui.WIN_CLOSED): 
                window2.close()
                return

        gui.popup_ok('Tasks have completed successfully.', title=setting_title, font=(setting_font, setting_font_size))
        window2.close()

    window = gui.Window(setting_title, layout=layout, size=(setting_window_size[0], setting_window_size[1]), resizable=False, finalize=True)

    while True:
        event, values = window.Read(timeout=100)

        if event in (None, 'Exit', 'Cancel', gui.WIN_CLOSED): 
            window.close()
            break

        elif event in ('Start Copy'):
            copy_mod(str(values['addr_mod']) + '/', str(values['addr_copy'])+ '/', window)
            window.close()
            break

interface()
