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

# Title
setting_app_title = 'APERX MOD COPY'
# Settings
# Edition, Version, Revision
setting_edition = 20221110
setting_revision = 1
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
# graphical_window Size
setting_window_size = [1440, 810]
# Resolution (Primary Screen)
# If Resolution > Window Size
# Make window center
setting_resolution = (1920, 1080)
# Color
# Background
setting_color = ['#222831', '#14FFEC', '#FF9F1C']
# Setting HTML Agent Header
setting_html_agent_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}

PySimpleGUI.LOOK_AND_FEEL_TABLE['CustomTheme'] = {'BACKGROUND': setting_color[0], 'TEXT': setting_color[2], 'INPUT': setting_color[0], 'TEXT_INPUT': setting_color[2], 'SCROLL': setting_color[1], 'BUTTON': (setting_color[1], setting_color[0]), 'PROGRESS': (setting_color[1], setting_color[0]), 'BORDER': 1, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0, }
PySimpleGUI.theme('CustomTheme')

