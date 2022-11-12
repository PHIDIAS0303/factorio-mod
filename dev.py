
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
    mod_list_json = {'mods': mod_list_json}

    with open(str(address_mod_source) + '/mod-list.json', 'w') as file:
        json.dump(mod_list_json, file, indent=2)

    PySimpleGUI.popup_ok('Mod list synced with string successfully.', title=setting_title, font=(setting_font, setting_font_size))
