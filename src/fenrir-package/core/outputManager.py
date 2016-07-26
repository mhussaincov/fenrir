#!/bin/python

class outputManager():
    def __init__(self):
        pass
    def presentText(self, environment, Text, Interrupt=True, soundIconName = ''):
        self.speakText(environment, Text, Interrupt)
        self.brailleText(environment, Text)
        self.playSoundIcon(environment, soundIconName):

    def speakText(self, environment, Text, Interrupt=True):
        if environment['runtime']['speechDriver'] == None:
            return
        if not environment['runtime']['settingsManager'].getSettingAsBool(environment, 'speech', 'enabled'):
            return
        if Interrupt:
            self.interruptOutput(environment)
        environment['runtime']['speechDriver'].setLanguage(environment['runtime']['settingsManager'].getSetting(environment, 'speech', 'language'))            
        environment['runtime']['speechDriver'].setVoice(environment['runtime']['settingsManager'].getSetting(environment, 'speech', 'voice'))
        environment['runtime']['speechDriver'].setPitch(environment['runtime']['settingsManager'].getSettingAsInt(environment, 'speech', 'pitch'))
        environment['runtime']['speechDriver'].setSpeed(environment['runtime']['settingsManager'].getSettingAsInt(environment, 'speech', 'rate'))
        environment['runtime']['speechDriver'].setModule(environment['runtime']['settingsManager'].getSetting(environment, 'speech', 'module'))
        environment['runtime']['speechDriver'].setVolume(environment['runtime']['settingsManager'].getSettingAsInt(environment, 'speech', 'volume'))
         
        environment['runtime']['speechDriver'].speak(Text)

    def brailleText(self, environment, Text, Interrupt=True):
        if not environment['runtime']['settingsManager'].getSettingAsBool(environment, 'braille', 'enabled'):
            return    
        print('braille')
    def interruptOutput(self, environment):
        environment['runtime']['speechDriver'].cancel()
 
    def playSoundIcon(self, environment, IconName, Interrupt=True):
        if soundIconName == '':
            return
        if not environment['runtime']['settingsManager'].getSettingAsBool(environment, 'sound', 'enabled'):
            return    
        print(IconName)
        try:
            print(environment['soundIcons'][IconName])
        except:
            print('no icon there for' + IconName)
