#!/bin/python
# -*- coding: utf-8 -*-

# Fenrir TTY screen reader
# By Chrys, Storm Dragon, and contributers.

from core import debug

generalInformation = {
'running': True,
'tutorialMode': False,
'currUser':'',
'prevUser':'',
'managerList':['inputManager','screenManager','commandManager','outputManager'
  ,'punctuationManager','cursorManager','applicationManager','debug'],
'commandFolderList':['commands','onInput','onScreenUpdate','onScreenChanged'
  ,'onApplicationChange','onSwitchApplicationProfile',],
}
