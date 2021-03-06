#!/bin/python
# -*- coding: utf-8 -*-

# Fenrir TTY screen reader
# By Chrys, Storm Dragon, and contributers.

from core import debug

class command():
    def __init__(self):
        pass
    def initialize(self, environment):
        self.env = environment
    def shutdown(self):
        pass
    def getDescription(self):
        return _('presents the current column number for review cursor in review mode or the text cursor if not. Starts with 1')       
    def run(self):
        cursorPos = self.env['runtime']['cursorManager'].getReviewOrTextCursor()
        self.env['runtime']['outputManager'].presentText(str(cursorPos['x'] + 1) , interrupt=True)
        self.env['runtime']['outputManager'].announceActiveCursor()
        self.env['runtime']['outputManager'].presentText(' column number' , interrupt=False)
        
    def setCallback(self, callback):
        pass
