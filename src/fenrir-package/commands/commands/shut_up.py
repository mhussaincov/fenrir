#!/bin/python

class command():
    def __init__(self):
        pass
    def run(self, environment):
        environment['runtime']['speechDriver'].cancel()
    def setCallback(self, callback):
        pass
    def shutdown(self):
        pass