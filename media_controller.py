import time
import os
import json

class MediaController:
    def __init__(self):
        with open("config.json", 'r') as f:
            config = json.load(f)
        
        self.current_volume = 50
        self.last_cmd = 0
        self.cmd_cooldown = config["cooldowns"]["gesture_cooldown"]
        self.last_vol = 0
        self.vol_cooldown = config["cooldowns"]["volume_cooldown"]
        self.gesture_map = config["gestures"]
        
        try:
            import pyautogui
            self.pyautogui = pyautogui
            self.pyautogui.PAUSE = 0.02
        except:
            import subprocess
            subprocess.check_call(["pip", "install", "pyautogui"])
            import pyautogui
            self.pyautogui = pyautogui
            self.pyautogui.PAUSE = 0.02

    def send_key(self, key, hold=False):
        try:
            time.sleep(0.05)
            if hold:
                if '+' in key:
                    mods = key.split('+')
                    for m in mods[:-1]:
                        self.pyautogui.keyDown(m)
                    self.pyautogui.keyDown(mods[-1])
                    time.sleep(0.1)
                    self.pyautogui.keyUp(mods[-1])
                    for m in mods[:-1]:
                        self.pyautogui.keyUp(m)
                else:
                    self.pyautogui.keyDown(key)
                    time.sleep(0.1)
                    self.pyautogui.keyUp(key)
            else:
                self.pyautogui.press(key)
            return True
        except:
            return False

    def play_pause(self):
        return self.send_key('space')

    def stop(self):
        return self.send_key('s')

    def next_track(self):
        return self.send_key('n')

    def previous_track(self):
        return self.send_key('p')

    def volume_up(self):
        now = time.time()
        if now - self.last_vol < self.vol_cooldown:
            return False
        self.send_key('ctrl+up', hold=True)
        self.current_volume = min(100, self.current_volume + 2)
        self.last_vol = now
        return True

    def volume_down(self):
        now = time.time()
        if now - self.last_vol < self.vol_cooldown:
            return False
        self.send_key('ctrl+down', hold=True)
        self.current_volume = max(0, self.current_volume - 2)
        self.last_vol = now
        return True

    def handle_gesture(self, data):
        now = time.time()
        if now - self.last_cmd < self.cmd_cooldown:
            return False
        
        gesture = data.get('gesture', 'UNKNOWN')
        pinch = data.get('pinch', {'active': False, 'volume': 50, 'direction': ''})
        
        if gesture != "UNKNOWN":
            cmd = self.gesture_map.get(gesture.lower())
            if cmd == "PLAY_PAUSE":
                self.last_cmd = now
                return self.play_pause()
            elif cmd == "STOP":
                self.last_cmd = now
                return self.stop()
            elif cmd == "NEXT_TRACK":
                self.last_cmd = now
                return self.next_track()
            elif cmd == "PREVIOUS_TRACK":
                self.last_cmd = now
                return self.previous_track()
        
        if pinch['active']:
            if pinch['volume'] > self.current_volume:
                return self.volume_up()
            elif pinch['volume'] < self.current_volume:
                return self.volume_down()
        
        return False