import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import math
import time
import os
import json

def load_config():
    with open("config.json", 'r') as f:
        return json.load(f)

class HandDetector:
    def __init__(self):
        self.config = load_config()
        self.current_volume = 50
        self.last_gesture = "UNKNOWN"
        self.stable_count = 0
        self.last_trigger = {}
        self.triggered = {'OPEN_PALM': False, 'FIST': False, 'TWO_FINGERS': False, 'THREE_FINGERS': False}
        
        # Settings
        c = self.config["cooldowns"]
        self.cooldown = c["gesture_cooldown"]
        self.stable_needed = c["stability_frames"]
        
        p = self.config["pinch"]
        self.min_ratio = p["min_ratio"]
        self.max_ratio = p["max_ratio"]
        self.smoothing = p["smoothing"]
        self.vol_step = p["step_size"]
        self.last_vol_update = 0
        
        # Load model
        model_path = self._get_model()
        options = vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=model_path),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1
        )
        self.detector = vision.HandLandmarker.create_from_options(options)

    def _get_model(self):
        path = "hand_landmarker.task"
        if not os.path.exists(path):
            import urllib.request
            url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            urllib.request.urlretrieve(url, path)
        return path

    def process_frame(self, frame, mirror=True):
        h, w = frame.shape[:2]
        if mirror:
            frame = cv2.flip(frame, 1)
        
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        results = self.detector.detect_for_video(mp_image, int(time.time() * 1000))
        
        for g in self.triggered:
            self.triggered[g] = False
        
        gesture_data = {'gesture': 'UNKNOWN', 'pinch': {'active': False, 'volume': self.current_volume}}
        
        if results and results.hand_landmarks:
            lm = results.hand_landmarks[0]
            pts = [(int(p.x * w), int(p.y * h)) for p in lm]
            
            # Get gesture with improved detection
            gesture = self._get_gesture_fixed(pts)
            
            # Stability check
            if gesture == self.last_gesture:
                self.stable_count += 1
            else:
                self.stable_count = 0
            
            # Trigger if stable and cooldown passed
            if gesture != 'UNKNOWN' and self.stable_count >= self.stable_needed:
                now = time.time()
                if now - self.last_trigger.get(gesture, 0) > self.cooldown:
                    self.triggered[gesture] = True
                    self.last_trigger[gesture] = now
                    # Show friendly names
                    names = {'OPEN_PALM': 'PLAY', 'FIST': 'STOP', 'TWO_FINGERS': 'NEXT', 'THREE_FINGERS': 'PREV'}
                    print(f"👉 {names[gesture]}")
            
            self.last_gesture = gesture
            
            # Get pinch
            pinch = self._get_pinch(pts)
            if pinch['active']:
                self.current_volume = pinch['volume']
                if pinch['direction']:
                    print(f"🔊 Volume {pinch['direction']}")
            
            gesture_data = {'gesture': gesture, 'pinch': pinch}
            
            # Draw minimal landmarks
            for i, p in enumerate(lm):
                x, y = int(p.x * w), int(p.y * h)
                if i in [4, 8]:  # Thumb and index tips
                    color = (0,255,255) if pinch['active'] else (0,255,0)
                    cv2.circle(frame, (x,y), 6, color, -1)
                else:
                    cv2.circle(frame, (x,y), 3, (0,255,0), -1)
            
            # Show gesture name only
            if gesture != "UNKNOWN":
                wrist = (int(lm[0].x * w), int(lm[0].y * h))
                names = {'OPEN_PALM': 'PLAY', 'FIST': 'STOP', 'TWO_FINGERS': 'NEXT', 'THREE_FINGERS': 'PREV'}
                cv2.putText(frame, names[gesture], (wrist[0]-30, wrist[1]-30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
            
            # Draw pinch line
            if pinch['active']:
                x1, y1 = pts[4]
                x2, y2 = pts[8]
                cv2.line(frame, (x1, y1), (x2, y2), (0,255,255), 3)
        
        return frame, gesture_data

    def _get_gesture_fixed(self, pts):
        """Fixed gesture detection with better thresholds"""
        if len(pts) < 21:
            return "UNKNOWN"
        
        # Get key points
        wrist = pts[0]
        index_tip = pts[8]
        middle_tip = pts[12]
        ring_tip = pts[16]
        pinky_tip = pts[20]
        
        index_pip = pts[6]
        middle_pip = pts[10]
        ring_pip = pts[14]
        pinky_pip = pts[18]
        
        index_mcp = pts[5]
        middle_mcp = pts[9]
        
        # Calculate hand size for relative thresholds
        hand_size = math.dist(wrist, middle_mcp)
        threshold = hand_size * 0.15  # 15% of hand size
        
        # Check if each finger is extended (tip above PIP)
        index_up = index_tip[1] < index_pip[1] - threshold
        middle_up = middle_tip[1] < middle_pip[1] - threshold
        ring_up = ring_tip[1] < ring_pip[1] - threshold
        pinky_up = pinky_tip[1] < pinky_pip[1] - threshold
        
        # Check thumb (different logic - thumb is sideways)
        thumb_tip = pts[4]
        thumb_ip = pts[3]
        thumb_mcp = pts[2]
        
        # Thumb is extended if it's far from index MCP
        thumb_to_index = math.dist(thumb_tip, index_mcp)
        thumb_extended = thumb_to_index > hand_size * 0.4
        
        # Count extended fingers
        extended = [index_up, middle_up, ring_up, pinky_up]
        extended_count = sum(extended)
        
        # GESTURE CLASSIFICATION
        
        # OPEN PALM: All fingers up
        if extended_count >= 3 and index_up and middle_up and thumb_extended:
            return "OPEN_PALM"
        
        # FIST: All fingers down
        elif extended_count <= 1 and not thumb_extended:
            return "FIST"
        
        # TWO FINGERS: Index and middle up, others down
        elif index_up and middle_up and not ring_up and not pinky_up:
            # Make sure ring and pinky are actually down
            ring_down = ring_tip[1] > ring_pip[1] + threshold
            pinky_down = pinky_tip[1] > pinky_pip[1] + threshold
            if ring_down and pinky_down:
                return "TWO_FINGERS"
        
        # THREE FINGERS: Index, middle, ring up, pinky down
        elif index_up and middle_up and ring_up and not pinky_up:
            # Make sure pinky is down
            pinky_down = pinky_tip[1] > pinky_pip[1] + threshold
            if pinky_down:
                return "THREE_FINGERS"
        
        return "UNKNOWN"

    def _get_pinch(self, pts):
        if len(pts) < 21:
            return {'active': False, 'volume': self.current_volume, 'direction': ''}
        
        dist = math.dist(pts[4], pts[8])
        hand_size = math.dist(pts[0], pts[9])
        ratio = dist / hand_size if hand_size > 0 else 0
        
        pinching = ratio < 0.8
        direction = ''
        
        if pinching:
            clamped = max(self.min_ratio, min(self.max_ratio, ratio))
            target = ((clamped - self.min_ratio) / (self.max_ratio - self.min_ratio)) * 100
            target = max(0, min(100, target))
            
            now = time.time()
            if now - self.last_vol_update > 0.05:
                old = self.current_volume
                diff = target - old
                if abs(diff) > self.vol_step:
                    step = self.vol_step if diff > 0 else -self.vol_step
                    self.current_volume += step
                    direction = 'HIGHER' if step > 0 else 'LOWER'
                else:
                    self.current_volume = int(target * (1 - self.smoothing) + old * self.smoothing)
                self.last_vol_update = now
        
        return {'active': pinching, 'volume': int(self.current_volume), 'direction': direction}