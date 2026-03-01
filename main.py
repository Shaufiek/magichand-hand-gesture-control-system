import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import math
import time
import os

class HandDetector:
    """Hand detection with gesture recognition"""
    
    def __init__(self, max_hands=2):
        self.max_hands = max_hands
        self.frame_height = 0
        self.frame_width = 0
        
        # Volume control
        self.current_volume = 50
        self.pinch_active = False
        
        # Pinch calibration
        self.min_pinch = 1.0
        self.max_pinch = 0.0
        self.calibration_frames = 0
        self.calibrated = False
        
        # Gesture state tracking
        self.last_gesture = {}
        self.last_trigger_time = {}
        self.cooldown = 0.5
        self.triggered = {'OPEN_PALM': False, 'FIST': False, 
                         'THUMBS_UP': False, 'THUMBS_DOWN': False}
        
        # Load model
        model_path = self._get_model()
        options = vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=model_path),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=max_hands
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        print("✓ Hand detector ready")

    def _get_model(self):
        path = os.path.join(os.path.dirname(__file__), "hand_landmarker.task")
        if not os.path.exists(path):
            print("Downloading hand model...")
            import urllib.request
            url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            urllib.request.urlretrieve(url, path)
        return path

    def process_frame(self, frame, mirror=True):
        """Main function - detect hands and gestures"""
        h, w = frame.shape[:2]
        self.frame_height, self.frame_width = h, w
        
        if mirror:
            frame = cv2.flip(frame, 1)
        
        # Detect hands
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        results = self.detector.detect_for_video(mp_image, int(time.time() * 1000))
        
        # Reset triggers
        for g in self.triggered:
            self.triggered[g] = False
        
        hands = []
        if results and results.hand_landmarks:
            for idx, landmarks in enumerate(results.hand_landmarks):
                # Get hand side
                side = "Unknown"
                if results.handedness and idx < len(results.handedness):
                    side = results.handedness[idx][0].category_name
                
                # Convert to pixel coordinates
                points = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
                
                # Recognize gestures
                gesture = self._get_gesture(points)
                hand_id = f"{side}_{idx}"
                
                # Check if gesture triggered
                if gesture != "UNKNOWN":
                    self._check_trigger(hand_id, gesture)
                
                # Get pinch data
                pinch = self._get_pinch(points)
                
                hands.append({
                    'id': hand_id,
                    'side': side,
                    'gesture': gesture,
                    'pinch': pinch
                })
                
                # Draw on frame
                self._draw_hand(frame, landmarks, gesture, pinch)
        
        return frame, hands

    def _get_gesture(self, pts):
        """Recognize open palm, fist, thumbs up/down"""
        if len(pts) < 21:
            return "UNKNOWN"
        
        def angle_between(p1, p2, p3):
            """Calculate angle at p2 between p1-p2-p3"""
            v1 = (p1[0] - p2[0], p1[1] - p2[1])
            v2 = (p3[0] - p2[0], p3[1] - p2[1])
            
            dot = v1[0]*v2[0] + v1[1]*v2[1]
            mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
            mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
            
            if mag1 * mag2 == 0:
                return 180
            
            # Clamp to avoid math domain error
            cos = dot / (mag1 * mag2)
            cos = max(-1, min(1, cos))
            return math.degrees(math.acos(cos))
        
        def is_curled(tip, pip, mcp):
            """Check if finger is curled using angle at PIP"""
            angle = angle_between(pts[mcp], pts[pip], pts[tip])
            return angle < 140
        
        # Check fingers
        curled = [
            is_curled(8, 6, 5),    # Index
            is_curled(12, 10, 9),  # Middle
            is_curled(16, 14, 13), # Ring
            is_curled(20, 18, 17)  # Pinky
        ]
        curled_count = sum(curled)
        
        # Check thumb
        hand_size = math.dist(pts[0], pts[9])
        thumb_out = math.dist(pts[4], pts[5]) / hand_size > 0.7 if hand_size > 0 else False
        thumb_up = pts[4][1] < pts[0][1] - 30
        thumb_down = pts[4][1] > pts[0][1] + 30
        
        # Classify
        if curled_count <= 1 and thumb_out:
            return "OPEN_PALM"
        elif curled_count >= 3 and not thumb_out:
            return "FIST"
        elif curled_count >= 3 and thumb_out and thumb_up:
            return "THUMBS_UP"
        elif curled_count >= 3 and thumb_out and thumb_down:
            return "THUMBS_DOWN"
        
        return "UNKNOWN"

    def _check_trigger(self, hand_id, gesture):
        """Trigger only on gesture change"""
        last = self.last_gesture.get(hand_id, "UNKNOWN")
        now = time.time()
        
        if gesture != last and gesture in self.triggered:
            last_time = self.last_trigger_time.get(gesture, 0)
            if now - last_time > self.cooldown:
                self.triggered[gesture] = True
                self.last_trigger_time[gesture] = now
                print(f"👉 {gesture}")
        
        self.last_gesture[hand_id] = gesture

    def _get_pinch(self, pts):
        """Measure pinch for volume"""
        if len(pts) < 21:
            return {'active': False, 'volume': self.current_volume}
        
        # Distance between thumb tip (4) and index tip (8)
        dist = math.dist(pts[4], pts[8])
        hand_size = math.dist(pts[0], pts[9])
        norm_dist = dist / hand_size if hand_size > 0 else 0
        
        # Is pinching?
        pinching = norm_dist < 0.5 or dist < 70
        
        # Calibration
        if pinching and not self.calibrated:
            self.calibration_frames += 1
            self.min_pinch = min(self.min_pinch, norm_dist)
            self.max_pinch = max(self.max_pinch, norm_dist)
            if self.calibration_frames >= 100:
                self.calibrated = True
                print(f"✓ Calibrated: {self.min_pinch:.2f}-{self.max_pinch:.2f}")
        
        # Map to volume
        if self.calibrated:
            low = max(0.05, self.min_pinch - 0.03)
            high = min(1.5, self.max_pinch + 0.1)
        else:
            low, high = 0.12, 0.9
        
        if high <= low:
            high = low + 0.3
        
        clamped = max(low, min(high, norm_dist))
        percent = ((clamped - low) / (high - low)) * 100
        percent = max(0, min(100, percent))
        
        if pinching:
            self.current_volume = int(percent * 0.6 + self.current_volume * 0.4)
        
        return {
            'active': pinching,
            'percent': percent,
            'volume': self.current_volume,
            'calibrated': self.calibrated,
            'progress': min(100, int(self.calibration_frames/100 * 100))
        }

    def _draw_hand(self, frame, landmarks, gesture, pinch):
        """Draw hand landmarks and info"""
        h, w = frame.shape[:2]
        
        # Hand connections
        connections = [(0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),
                      (0,9),(9,10),(10,11),(11,12),(0,13),(13,14),(14,15),(15,16),
                      (0,17),(17,18),(18,19),(19,20),(5,9),(9,13),(13,17)]
        
        # Draw connections
        for a, b in connections:
            if a < len(landmarks) and b < len(landmarks):
                p1 = (int(landmarks[a].x * w), int(landmarks[a].y * h))
                p2 = (int(landmarks[b].x * w), int(landmarks[b].y * h))
                cv2.line(frame, p1, p2, (255,255,255), 2)
        
        # Draw landmarks
        for i, lm in enumerate(landmarks):
            x, y = int(lm.x * w), int(lm.y * h)
            if i in [4, 8]:  # Thumb and index tips
                color = (0,255,255) if pinch['active'] else (0,255,0)
                cv2.circle(frame, (x,y), 8, color, -1)
            else:
                cv2.circle(frame, (x,y), 5, (0,255,0), -1)
            cv2.circle(frame, (x,y), 2, (255,255,255), -1)
        
        # Draw pinch line
        if pinch['active']:
            p1 = (int(landmarks[4].x * w), int(landmarks[4].y * h))
            p2 = (int(landmarks[8].x * w), int(landmarks[8].y * h))
            
            if pinch['percent'] < 30:
                color = (0,0,255)
            elif pinch['percent'] < 70:
                color = (0,255,255)
            else:
                color = (0,255,0)
            
            cv2.line(frame, p1, p2, color, 3)
            mx, my = (p1[0]+p2[0])//2, (p1[1]+p2[1])//2
            cv2.putText(frame, f"{int(pinch['percent'])}%", (mx-20, my-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
        
        # Draw gesture name
        if gesture != "UNKNOWN":
            wrist = (int(landmarks[0].x * w), int(landmarks[0].y * h))
            
            if self.triggered.get(gesture, False):
                cv2.rectangle(frame, (wrist[0]-70, wrist[1]-90), 
                             (wrist[0]+120, wrist[1]-40), (0,255,255), -1)
            else:
                cv2.rectangle(frame, (wrist[0]-70, wrist[1]-90), 
                             (wrist[0]+120, wrist[1]-40), (0,0,0), -1)
            
            icons = {"OPEN_PALM": "✋ OPEN", "FIST": "👊 FIST",
                    "THUMBS_UP": "👍 UP", "THUMBS_DOWN": "👎 DOWN"}
            colors = {"OPEN_PALM": (0,255,0), "FIST": (0,0,255),
                     "THUMBS_UP": (255,255,0), "THUMBS_DOWN": (0,165,255)}
            
            cv2.putText(frame, icons.get(gesture, gesture), 
                       (wrist[0]-65, wrist[1]-60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, colors.get(gesture, (255,255,255)), 2)

def draw_volume_bar(frame, volume, x, y, width=300, height=25):
    """Draw volume bar"""
    cv2.rectangle(frame, (x, y), (x+width, y+height), (50,50,50), -1)
    
    fill = int((volume / 100) * width)
    if volume < 30:
        color = (0,0,255)
    elif volume < 70:
        color = (0,255,255)
    else:
        color = (0,255,0)
    
    cv2.rectangle(frame, (x, y), (x+fill, y+height), color, -1)
    cv2.rectangle(frame, (x, y), (x+width, y+height), (255,255,255), 2)
    cv2.putText(frame, f"Volume: {volume}%", (x, y-5),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

def main():
    print("\n" + "="*50)
    print("GESTURE CONTROL SYSTEM")
    print("="*50)
    print("Gestures:")
    print("  ✋ Open Palm  - Play/Pause")
    print("  👊 Fist       - Stop")
    print("  👍 Thumbs Up  - Next Track")
    print("  👎 Thumbs Down- Previous Track")
    print("  👌 Pinch      - Volume Control")
    print("\nControls:")
    print("  q - Quit")
    print("  d - Toggle debug")
    print("  f - Toggle mirror")
    print("="*50)
    
    # Camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Detector
    detector = HandDetector(max_hands=2)
    
    # Loop
    mirror = True
    debug = False
    fps = 0
    frame_count = 0
    fps_time = time.time()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process frame
        frame, hands = detector.process_frame(frame, mirror)
        frame_count += 1
        
        # FPS
        if time.time() - fps_time >= 1:
            fps = frame_count
            frame_count = 0
            fps_time = time.time()
        
        # UI
        cv2.putText(frame, f"FPS: {fps}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
        cv2.putText(frame, f"Mirror: {'ON' if mirror else 'OFF'}", (10, 55),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0) if mirror else (0,0,255), 1)
        
        # Volume
        if hands:
            volume = hands[0]['pinch']['volume']
            progress = hands[0]['pinch']['progress']
            calibrated = hands[0]['pinch']['calibrated']
            
            if not calibrated:
                cv2.putText(frame, f"Calibrating: {progress}%", (50, frame.shape[0]-110),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255), 1)
        else:
            volume = 50
        
        draw_volume_bar(frame, volume, 50, frame.shape[0]-80, 400, 25)
        
        # Debug
        if debug and hands:
            y = 100
            for h in hands:
                cv2.putText(frame, f"{h['side']}: {h['gesture']}", (10, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,0), 1)
                y += 20
        
        cv2.imshow('Gesture Control', frame)
        
        # Keys
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('d'):
            debug = not debug
        elif key == ord('f'):
            mirror = not mirror
    
    cap.release()
    cv2.destroyAllWindows()
    print("\nDone.")

if __name__ == "__main__":
    main()