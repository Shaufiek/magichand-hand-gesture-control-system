# Import essential libraries
import time
import os
import json

class MediaController:
    """Sends keyboard commands to  VLC media player based on detected gestures"""
    
    def __init__(self):
        # Load setings
        with open("config.json", 'r') as f:
            config = json.load(f)
        
        # Volume starts at 50 %
        self.current_volume = 50
        
        # Command timing
        self.last_cmd = 0                          #  When last command was sent
        self.cmd_cooldown = config["cooldowns"]["gesture_cooldown"]
        self.last_vol = 0                           # When  volume  last changed
        self.vol_cooldown = config["cooldowns"]["volume_cooldown"]
        
        #  What each gesture does
        self.gesture_map = config["gestures"]
        
        # Setup keyboard control
        try:
            import pyautogui
            self.pyautogui = pyautogui
            self.pyautogui.PAUSE = 0.02  #  Small delay  between  key presses
        except:
            # Auto - install if missing
            import subprocess
            subprocess.check_call(["pip", "install", "pyautogui"])
            import pyautogui
            self.pyautogui = pyautogui
            self.pyautogui.PAUSE = 0.02

    def send_key(self, key, hold=False):
        """ Press a  keyboard key or combination"""
        try:
            time.sleep(0.05)  # Tiny  delay to be safe
            
            if hold:  
                # For volume : press and hold briefly
                if '+' in key:
                    mods = key.split('+')
                    # Press modifier keys ( ctrl , alt, shift )
                    for m in mods[:-1]:
                        self.pyautogui.keyDown(m)
                    # Press and  hold main key
                    self.pyautogui.keyDown(mods[-1])
                    time.sleep(0.1)  # Hold for 100ms
                    #  Release all
                    self.pyautogui.keyUp(mods[-1])
                    for m in mods[:-1]:
                        self.pyautogui.keyUp(m)
                else:
                    self.pyautogui.keyDown(key)
                    time.sleep(0.1)
                    self.pyautogui.keyUp(key)
            else:
                #  For track controls  we do a quick tap
                self.pyautogui.press(key)
            return True
        except:
            return False

    # Command functions 
    def play_pause(self):
        """Toggle play / pause"""
        return self.send_key('space')

    def stop(self):
        """Stop playback """
        return self.send_key('s')

    def next_track(self):
        """Skip  to next track"""
        return self.send_key('n')

    def previous_track(self):
        """Go to previous track"""
        return self.send_key('p')

    def volume_up(self):
        """Increase volume"""
        now = time.time()
        if now - self.last_vol < self.vol_cooldown:
            return False
        self.send_key('ctrl+up', hold=True)
        self.current_volume = min(100, self.current_volume + 2)
        self.last_vol = now
        return True

    def volume_down(self):
        """Decrease  volume"""
        now = time.time()
        if now - self.last_vol < self.vol_cooldown:
            return False
        self.send_key('ctrl+down', hold=True)
        self.current_volume = max(0, self.current_volume - 2)
        self.last_vol = now
        return True

    def handle_gesture(self, data):
        """ Take a gesture  and turn it into  a VLC - command """
        now = time.time()
        
        #  Handle spam commands
        if now - self.last_cmd < self.cmd_cooldown:
            return False
        
        gesture = data.get('gesture', 'UNKNOWN')
        pinch = data.get('pinch', {'active': False, 'volume': 50, 'direction': ''})
        
        # Handle  regular gestures
        if gesture != "UNKNOWN":
            cmd = self.gesture_map.get(gesture.lower())
            self.last_cmd = now
            
            if cmd == "PLAY_PAUSE":
                return self.play_pause()
            elif cmd == "STOP":
                return self.stop()
            elif cmd == "NEXT_TRACK":
                return self.next_track()
            elif cmd == "PREVIOUS_TRACK":
                return self.previous_track()
        
        # Handle pinch for volume
        if pinch['active']:
            if pinch['volume'] > self.current_volume:
                return self.volume_up()
            elif pinch['volume'] < self.current_volume:
                return self.volume_down()
        
        return False