#!/bin/python
# -*- coding: utf-8 -*-

# Fenrir TTY screen reader
# By Chrys, Storm Dragon, and contributers.

_evdevAvailable = False
_evdevAvailableError = ''
try:
    import evdev
    from evdev import InputDevice, UInput
    _evdevAvailable = True
except Exception as e:
    _evdevAvailableError = str(e)

import time
from select import select
from core import inputEvent
from core import debug

class driver():
    def __init__(self):
        self.iDevices = {}
        self.uDevices = {}
        self.iDeviceNo = 0
        self._initialized = False        

    def initialize(self, environment):
        self.env = environment
        global _evdevAvailable
        self._initialized = _evdevAvailable
        if not self._initialized:
            global _evdevAvailableError
            self.env['runtime']['debug'].writeDebugOut('InputDriver: ' + _evdevAvailableError,debug.debugLevel.ERROR)         
            return  

    def shutdown(self):
        if not self._initialized:
            return       
    def getInputEvent(self):
        if not self.hasIDevices():
            time.sleep(0.008) # dont flood CPU        
            return None
        event = None
        r, w, x = select(self.iDevices, [], [], self.env['runtime']['settingsManager'].getSettingAsFloat('screen', 'screenUpdateDelay'))
        if r != []:
            for fd in r:
                try:
                    event = self.iDevices[fd].read_one()            
                except:
                    self.removeDevice(fd)
                    return None
                foreward = False
                while(event):
                    self.env['input']['eventBuffer'].append( [self.iDevices[fd], self.uDevices[fd], event])
                    if event.type == evdev.events.EV_KEY:
                        if event.code != 0:
                            currMapEvent = self.mapEvent(event)
                            if not currMapEvent:
                                foreward = True                            
                                event = self.iDevices[fd].read_one()                               
                                continue
                            if not isinstance(currMapEvent['EventName'], str):
                                foreward = True                            
                                event = self.iDevices[fd].read_one()                               
                                continue
                            if not foreward:
                                if currMapEvent['EventState'] in [0,1,2]:
                                    return currMapEvent
                    else:
                        if not event.type in [0,1,4]:
                            foreward = True
                    event = self.iDevices[fd].read_one()   
                if foreward:
                    self.writeEventBuffer()
                    self.clearEventBuffer()                                                                         
        return None

    def writeEventBuffer(self):
        if not self._initialized:
            return    
        for iDevice, uDevice, event in self.env['input']['eventBuffer']:
            self.writeUInput(uDevice, event)

    def clearEventBuffer(self):
        if not self._initialized:
            return    
        del self.env['input']['eventBuffer'][:]
                        
    def writeUInput(self, uDevice, event):
        if not self._initialized:
            return    
        uDevice.write_event(event)
        uDevice.syn()  

    def updateInputDevices(self, force = False, init = False):
        if init:
            self.removeAllDevices()
        deviceFileList = evdev.list_devices()
        if not force:
            if len(deviceFileList) == self.iDeviceNo:
                return
        mode = self.env['runtime']['settingsManager'].getSetting('keyboard', 'device').upper()
        iDevicesFiles = []
        for device in self.iDevices:
            iDevicesFiles.append(self.iDevices[device].fn)
        if len(iDevicesFiles) == len(deviceFileList):
            return
        eventType = evdev.events
        for deviceFile in deviceFileList:
            try:
                if deviceFile in iDevicesFiles:
                    continue        
                try:
                    open(deviceFile)
                except:
                    print("Not readable Inputdevice : " + deviceFile +' ' + str(e))    
                    continue
                # 3 pos absolute
                # 2 pos relative
                # 1 Keys
                currDevice = evdev.InputDevice(deviceFile)
                if currDevice.name.upper() in ['SPEAKUP','PY-EVDEV-UINPUT']:
                    continue
                cap = currDevice.capabilities()
                if mode in ['ALL','NOMICE']:
                    if eventType.EV_KEY in cap:
                        if 116 in cap[eventType.EV_KEY] and len(cap[eventType.EV_KEY]) < 10:
                            print('power')
                            continue
                        if len(cap[eventType.EV_KEY]) < 30:
                            print('Not A useful keyboared')
                            continue                            
                        if mode == 'ALL':
                            self.iDevices[currDevice.fd] = currDevice
                            self.grabDevice(currDevice.fd)
                            print('Device added (ALL):' + self.iDevices[currDevice.fd].name)
                        elif mode == 'NOMICE':
                            if not ((eventType.EV_REL in cap) or (eventType.EV_ABS in cap)):
                                self.iDevices[currDevice.fd] = currDevice
                                self.grabDevice(currDevice.fd)
                                print('Device added (NOMICE):' + self.iDevices[currDevice.fd].name)
                elif currDevice.name.upper() in mode.split(','):
                    self.iDevices[currDevice.fd] = currDevice
                    self.grabDevice(currDevice.fd)                    
                    print('Device added (Name):' + self.iDevices[currDevice.fd].name)
            except Exception as e:
                print("Skip Inputdevice : " + deviceFile +' ' + str(e))                     
        self.iDeviceNo = len(evdev.list_devices())
            
    def mapEvent(self, event):
        if not self._initialized:
            return None    
        if not event:
            return None
        mEvent = inputEvent.inputEvent
        try:
            mEvent['EventName'] = evdev.ecodes.keys[event.code]
            mEvent['EventValue'] = event.code
            mEvent['EventSec'] = event.sec
            mEvent['EventUsec'] = event.usec                
            mEvent['EventState'] = event.value
            return mEvent
        except Exception as e:
            return None
       
    def getLedState(self, led = 0):
        if not self.hasIDevices():
            return False    
        # 0 = Numlock
        # 1 = Capslock
        # 2 = Rollen
        for fd, dev in self.iDevices.items():
            if led in dev.leds():
                return True
        return False          
    def toggleLedState(self, led = 0):
        if not self.hasIDevices():
            return False    
        ledState = self.getLedState(led)
        for i in self.iDevices:
            # 17 LEDs
            if 17 in self.iDevices[i].capabilities():            
                if ledState == 1:
                    self.iDevices[i].set_led(led , 0)
                else:
                    self.iDevices[i].set_led(led , 1)
    def grabAllDevices(self):
        if not self._initialized:
            return
        for fd in self.iDevices:
            self.grabDevice(fd)

    def grabDevice(self, fd):
        try:        
            self.uDevices[fd] = UInput.from_device(self.iDevices[fd].fn)
        except Exception as e:
            try:
                self.env['runtime']['debug'].writeDebugOut('InputDriver evdev: compat fallback:  ' + str(e),debug.debugLevel.ERROR)         
                dev = self.iDevices[fd]
                cap = dev.capabilities()
                del cap[0]
                self.uDevices[fd] = UInput(
                  cap,
                  dev.name,
                )
            except Exception as e:
                self.env['runtime']['debug'].writeDebugOut('InputDriver evdev: init Uinput not possible:  ' + str(e),debug.debugLevel.ERROR)         
                return                  
        try:
            self.iDevices[fd].grab()
        except Exception as e:
            self.env['runtime']['debug'].writeDebugOut('InputDriver evdev: grabing not possible:  ' + str(e),debug.debugLevel.ERROR)         

    def removeDevice(self,fd):
        self.clearEventBuffer()
        try:
            self.iDevices[fd].ungrab()
        except:
            pass
        try:
            self.iDevices[fd].close()
        except:
            pass
        try:
            self.uDevices[fd].close()
        except:
            pass 
        try:
            del(self.iDevices[fd])
        except:
            pass
        try:
            del(self.uDevices[fd])
        except:
            pass                 
    def hasIDevices(self):
        if not self._initialized:
            return False
        if not self.iDevices:
            return False
        if len(self.iDevices) == 0:
            return False
        return True    

    def removeAllDevices(self):
        if not self.hasIDevices():
            return
        devices = self.iDevices.copy()
        for fd in devices:
            self.removeDevice(fd)
        self.iDevices.clear()
        self.uDevices.clear()
        self.iDeviceNo = 0

    def __del__(self):
        if not self._initialized:
            return      


