#  Import essential libraries
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import math
import time
import os
import json

# Load settings
def load_config():
    """Read all setings from config.json """
    with open("config.json", 'r') as f:
        return json.load(f)

# Hand detector module
class HandDetector:
    def __init__(self):
        #  Load settings
        self.config = load_config()
        
        # Volume starts at 50 %
        self.current_volume = 50
        
        # Track gestures over time
        self.last_gesture = "UNKNOWN"     #  What gesture was last seen
        self.stable_count = 0              # How many  frames same gesture
        self.last_trigger = {}             # When each gesture last  triggered
        self.triggered = {                  # Which gestures triggered  this frame
            'OPEN_PALM': False, 
            'FIST': False, 
            'TWO_FINGERS': False, 
            'THREE_FINGERS': False
        }
        
        # Cooldown settings
        c = self.config["cooldowns"]
        self.cooldown = c["gesture_cooldown"]        # Time between triggers
        self.stable_needed = c["stability_frames"]    # Frames  to hold gesture
        
        #  Pinch settings for volume
        p = self.config["pinch"]
        self.min_ratio = p["min_ratio"]      # Your fully pinched value
        self.max_ratio = p["max_ratio"]      #  Your fully open value
        self.smoothing = p["smoothing"]       # How  smooth volume changes
        self.vol_step = p["step_size"]        # Volume change per step
        self.last_vol_update = 0               #  When volume last changed
        
        # Load  Media Pipe hand model
        model_path = self._get_model()
        options = vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=model_path),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1
        )
        self.detector = vision.HandLandmarker.create_from_options(options)

    def _get_model(self):
        """Download the hand m odel if not already there """
        path = "hand_landmarker.task"
        if not os.path.exists(path):
            import urllib.request
            url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            urllib.request.urlretrieve(url, path)
        return path

    def process_frame(self, frame, mirror=True):
        """Main function that detect hands and gestures in each camera frame"""
        h, w = frame.shape[:2]
        
         # Flip  like a mirror for a more natural feeling
        if mirror:
            frame = cv2.flip(frame, 1)
        
        # Convert to RGB for MediaPipe
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        
        #  Detect hands in this frame
        results = self.detector.detect_for_video(mp_image, int(time.time() * 1000))
        
        # Reset triggers for  new frame
        for g in self.triggered:
            self.triggered[g] = False
        
         # Prepare  data to send back
        gesture_data = {'gesture': 'UNKNOWN', 'pinch': {'active': False, 'volume': self.current_volume}}
        
        # If  hands  found then process them
        if results and results.hand_landmarks:
            # Get first hand because only 1 is tracked
            lm = results.hand_landmarks[0]
            pts = [(int(p.x * w), int(p.y * h)) for p in lm]
            
             # Figure out  what gesture this is
            gesture = self._get_gesture_fixed(pts)
            
            # Check if same  gesture held  for multiple frames
            if gesture == self.last_gesture:
                self.stable_count += 1
            else:
                self.stable_count = 0
            
            #  If held long enough and cooldown passed then trigger it
            if gesture != 'UNKNOWN' and self.stable_count >= self.stable_needed:
                now = time.time()
                if now - self.last_trigger.get(gesture, 0) > self.cooldown:
                    self.triggered[gesture] = True
                    self.last_trigger[gesture] = now
            
            self.last_gesture = gesture
            
            # Check for pinch gesture for volume control
            pinch = self._get_pinch(pts)
            if pinch['active']:
                self.current_volume = pinch['volume']
                if pinch['direction']:
                    print(f"Volume {pinch['direction']}")
            
            gesture_data = {'gesture': gesture, 'pinch': pinch}
            
            #  Draw dots on hand
            for i, p in enumerate(lm):
                x, y = int(p.x * w), int(p.y * h)
                if i in [4, 8]:  # Highlight thumb and index tips
                    color = (0,255,255) if pinch['active'] else (0,255,0)
                    cv2.circle(frame, (x,y), 6, color, -1)
                else:
                    cv2.circle(frame, (x,y), 3, (0,255,0), -1)
            
            # Draw a line between thumb and index when pinching
            if pinch['active']:
                x1, y1 = pts[4]
                x2, y2 = pts[8]
                cv2.line(frame, (x1, y1), (x2, y2), (0,255,255), 3)
        
        return frame, gesture_data

    def _get_gesture_fixed(self, pts):
        """Figure  out which gesture the hand is making"""
        if len(pts) < 21:
            return "UNKNOWN"
        
        # Key  points on hand
        wrist = pts[0]
        index_tip = pts[8]
        middle_tip = pts[12]
        ring_tip = pts[16]
        pinky_tip = pts[20]
        
        index_pip = pts[6]   # Middle joint of index
        middle_pip = pts[10]  # Middle  joint of middle
        ring_pip = pts[14]    # Middle joint of  ring
        pinky_pip = pts[18]   # Middle  joint of pinky
        
        index_mcp = pts[5]    #  Base of index
        middle_mcp = pts[9]   # Base  of middle
        
        # Hand size helps make detection work at any distance
        hand_size = math.dist(wrist, middle_mcp)
        threshold = hand_size * 0.15  # 15 % of hand size
        
        # Check if each finger is extended
        index_up = index_tip[1] < index_pip[1] - threshold
        middle_up = middle_tip[1] < middle_pip[1] - threshold
        ring_up = ring_tip[1] < ring_pip[1] - threshold
        pinky_up = pinky_tip[1] < pinky_pip[1] - threshold
        
        # Check if  thumb is away from hand
        thumb_tip = pts[4]
        thumb_to_index = math.dist(thumb_tip, index_mcp)
        thumb_extended = thumb_to_index > hand_size * 0.4
        
         # Detect total fingers up
        extended = [index_up, middle_up, ring_up, pinky_up]
        extended_count = sum(extended)
        
        #  Decide which gesture
        
        # Open palm: most fingers up and thumb out
        if extended_count >= 3 and index_up and middle_up and thumb_extended:
            return "OPEN_PALM"
        
        # Fist : most fingers  down and thumb in
        elif extended_count <= 1 and not thumb_extended:
            return "FIST"
        
        # Peace sign : index and middle up  and the others down
        elif index_up and middle_up and not ring_up and not pinky_up:
            # Check again if ring and pinky  are really down
            ring_down = ring_tip[1] > ring_pip[1] + threshold
            pinky_down = pinky_tip[1] > pinky_pip[1] + threshold
            if ring_down and pinky_down:
                return "TWO_FINGERS"
        
        # Three fingers: index up , middle up , ring up , pinky down
        elif index_up and middle_up and ring_up and not pinky_up:
            # Check pinky is down
            pinky_down = pinky_tip[1] > pinky_pip[1] + threshold
            if pinky_down:
                return "THREE_FINGERS"
        
        return "UNKNOWN"

    def _get_pinch(self, pts):
        """Measure thumb to  index pinch for volume control """
        if len(pts) < 21:
            return {'active': False, 'volume': self.current_volume, 'direction': ''}
        
         # Distance between thumb tip and index tip
        dist = math.dist(pts[4], pts[8])
        
        # Hand  size normalized to make it work at any distance
        hand_size = math.dist(pts[0], pts[9])
        ratio = dist / hand_size if hand_size > 0 else 0
        
        # Detect if pinch gesture is made
        pinching = ratio < 0.8
        direction = ''
        
        if pinching:
            # Attach  to your personal range
            clamped = max(self.min_ratio, min(self.max_ratio, ratio))
            
            #  Convert to volume percentage range of 0 - 100
            target = ((clamped - self.min_ratio) / (self.max_ratio - self.min_ratio)) * 100
            target = max(0, min(100, target))
            
            # Smoothly move towards target volume
            now = time.time()
            if now - self.last_vol_update > 0.05:
                old = self.current_volume
                diff = target - old
                if abs(diff) > self.vol_step:
                    step = self.vol_step if diff > 0 else -self.vol_step
                    self.current_volume += step
                    direction = 'Higher' if step > 0 else 'Lower'
                else:
                     # Apply smoothing
                    self.current_volume = int(target * (1 - self.smoothing) + old * self.smoothing)
                self.last_vol_update = now
        
        return {'active': pinching, 'volume': int(self.current_volume), 'direction': direction}
