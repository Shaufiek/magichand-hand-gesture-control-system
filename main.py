import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import time
import sys
import os
import math

class HandLandmarkDetector:
    """
    A class for hand landmark detection with coordinate extraction and normalization
    """
    
    def __init__(self, max_hands=2, detection_confidence=0.5):
        """
        Initialize the hand detector using MediaPipe Tasks API.
        """
        self.max_hands = max_hands
        self.detection_confidence = detection_confidence
        self.frame_height = 0
        self.frame_width = 0
        
        # Download model if needed
        model_path = self._get_model_path()
        
        # Initialize the landmarker
        options = vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=model_path),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=max_hands,
            min_hand_detection_confidence=detection_confidence,
            min_hand_presence_confidence=detection_confidence,
            min_tracking_confidence=detection_confidence
        )
        
        self.landmarker = vision.HandLandmarker.create_from_options(options)
        print(f"Hand detector initialized successfully!")
        print(f"  - Max hands: {max_hands}")
        print(f"  - Detection confidence: {detection_confidence}")
    
    def _get_model_path(self):
        """Get or download the hand landmark model."""
        model_path = os.path.join(os.path.dirname(__file__), "hand_landmarker.task")
        
        if not os.path.exists(model_path):
            print("Downloading hand landmark model...")
            import urllib.request
            url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            urllib.request.urlretrieve(url, model_path)
        
        return model_path
    
    def find_hands(self, frame, draw=True, flip_type=True):
        """
        Detect hands in the frame and extract landmarks with normalized coordinates.
        """
        # Store frame dimensions
        self.frame_height, self.frame_width = frame.shape[:2]
        
        # Flip for mirror effect
        if flip_type:
            working_frame = cv2.flip(frame, 1)
        else:
            working_frame = frame
        
        # Convert BGR to RGB and create MediaPipe Image
        rgb_frame = cv2.cvtColor(working_frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Detect hands
        timestamp = int(time.time() * 1000)
        detection_result = self.landmarker.detect_for_video(mp_image, timestamp)
        
        # Process results
        hands_data = []
        
        if detection_result and detection_result.hand_landmarks:
            for idx, hand_landmarks in enumerate(detection_result.hand_landmarks):
                # Extract both raw and normalized landmarks
                landmarks_raw = self._extract_raw_landmarks(hand_landmarks)
                landmarks_norm = self._extract_normalized_landmarks(hand_landmarks)
                
                # Get handedness
                hand_label = "Unknown"
                hand_score = 1.0
                if detection_result.handedness and idx < len(detection_result.handedness):
                    hand_label = detection_result.handedness[idx][0].category_name
                    hand_score = detection_result.handedness[idx][0].score
                
                # Calculate hand bounding box and center
                bbox = self._calculate_bounding_box(landmarks_raw)
                hand_center = self._calculate_hand_center(landmarks_raw)
                
                # Calculate relative positions (normalized relative to wrist)
                relative_landmarks = self._calculate_relative_positions(landmarks_raw)
                
                # Calculate scale-invariant features (distances between key points)
                scale_invariant_features = self._calculate_scale_invariant_features(landmarks_raw)
                
                hand_data = {
                    'hand_id': idx,
                    'hand_label': hand_label,
                    'confidence': hand_score,
                    'landmarks_raw': landmarks_raw,        # Pixel coordinates
                    'landmarks_norm': landmarks_norm,      # Normalized coordinates (0-1)
                    'relative_landmarks': relative_landmarks,  # Relative to wrist
                    'scale_invariant_features': scale_invariant_features,  # Distance ratios
                    'bounding_box': bbox,                  # Hand bounding box
                    'hand_center': hand_center,            # Center of hand
                    'wrist_position': landmarks_raw[0] if landmarks_raw else None  # Wrist position
                }
                hands_data.append(hand_data)
                
                # Draw on frame if requested
                if draw:
                    self._draw_landmarks(working_frame, hand_landmarks, hand_label, bbox, hand_center)
        
        # Copy the annotated working frame back to the original frame
        frame[:] = working_frame
        
        return frame, hands_data
    
    def _extract_raw_landmarks(self, hand_landmarks):
        """
        Extract raw pixel coordinates for all 21 landmarks.
        
        Returns:
            list: List of (x, y) tuples in pixel coordinates
        """
        landmarks = []
        for lm in hand_landmarks:
            cx = int(lm.x * self.frame_width)
            cy = int(lm.y * self.frame_height)
            landmarks.append((cx, cy))
        return landmarks
    
    def _extract_normalized_landmarks(self, hand_landmarks):
        """
        Extract normalized coordinates (0-1 range) for all 21 landmarks.
        These are scale-invariant and work regardless of image size.
        
        Returns:
            list: List of (x_norm, y_norm) tuples in range [0, 1]
        """
        landmarks = []
        for lm in hand_landmarks:
            landmarks.append((lm.x, lm.y))
        return landmarks
    
    def _calculate_bounding_box(self, landmarks_raw):
        """
        Calculate the bounding box around the hand.
        
        Returns:
            dict: Bounding box with x_min, y_min, width, height
        """
        if not landmarks_raw:
            return None
        
        x_coords = [point[0] for point in landmarks_raw]
        y_coords = [point[1] for point in landmarks_raw]
        
        x_min, x_max = min(x_coords), max(x_coords)
        y_min, y_max = min(y_coords), max(y_coords)
        
        return {
            'x_min': x_min,
            'y_min': y_min,
            'width': x_max - x_min,
            'height': y_max - y_min,
            'center_x': (x_min + x_max) // 2,
            'center_y': (y_min + y_max) // 2
        }
    
    def _calculate_hand_center(self, landmarks_raw):
        """
        Calculate the center of the hand (average of all landmarks).
        
        Returns:
            tuple: (center_x, center_y)
        """
        if not landmarks_raw:
            return None
        
        avg_x = sum(point[0] for point in landmarks_raw) // len(landmarks_raw)
        avg_y = sum(point[1] for point in landmarks_raw) // len(landmarks_raw)
        
        return (avg_x, avg_y)
    
    def _calculate_relative_positions(self, landmarks_raw):
        """
        Calculate positions relative to the wrist (landmark 0).
        This makes gestures invariant to hand position on screen.
        
        Returns:
            list: List of (dx, dy) relative to wrist
        """
        if not landmarks_raw or len(landmarks_raw) < 1:
            return []
        
        wrist_x, wrist_y = landmarks_raw[0]
        relative_positions = []
        
        for i, (x, y) in enumerate(landmarks_raw):
            dx = x - wrist_x
            dy = y - wrist_y
            relative_positions.append((dx, dy))
        
        return relative_positions
    
    def _calculate_scale_invariant_features(self, landmarks_raw):
        """
        Calculate scale-invariant features like distances between key points.
        These features work regardless of hand distance from camera.
        
        Returns:
            dict: Dictionary of scale-invariant features
        """
        if not landmarks_raw or len(landmarks_raw) < 21:
            return {}
        
        features = {}
        
        # Helper function to calculate distance between two landmarks
        def distance(idx1, idx2):
            x1, y1 = landmarks_raw[idx1]
            x2, y2 = landmarks_raw[idx2]
            return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        # Get palm size (distance from wrist to middle finger MCP) as reference
        palm_size = distance(0, 9)  # Wrist to middle finger base
        
        if palm_size > 0:  # Avoid division by zero
            # Normalized finger lengths (divided by palm size)
            features['thumb_length'] = distance(0, 4) / palm_size      # Wrist to thumb tip
            features['index_length'] = distance(0, 8) / palm_size      # Wrist to index tip
            features['middle_length'] = distance(0, 12) / palm_size    # Wrist to middle tip
            features['ring_length'] = distance(0, 16) / palm_size      # Wrist to ring tip
            features['pinky_length'] = distance(0, 20) / palm_size     # Wrist to pinky tip
            
            # Normalized finger tip distances from each other
            features['thumb_index_distance'] = distance(4, 8) / palm_size   # Thumb to index
            features['index_middle_distance'] = distance(8, 12) / palm_size # Index to middle
            features['middle_ring_distance'] = distance(12, 16) / palm_size # Middle to ring
            features['ring_pinky_distance'] = distance(16, 20) / palm_size  # Ring to pinky
            
            # Hand openness (average distance of fingertips from palm center)
            palm_center = self._calculate_palm_center(landmarks_raw)
            if palm_center:
                px, py = palm_center
                fingertip_indices = [4, 8, 12, 16, 20]
                total_distance = 0
                for idx in fingertip_indices:
                    fx, fy = landmarks_raw[idx]
                    dist = math.sqrt((fx - px)**2 + (fy - py)**2)
                    total_distance += dist
                features['hand_openness'] = (total_distance / 5) / palm_size
        
        return features
    
    def _calculate_palm_center(self, landmarks_raw):
        """
        Calculate the center of the palm using MCP joints.
        
        Returns:
            tuple: (center_x, center_y) of palm
        """
        if len(landmarks_raw) < 13:  # Need at least up to middle MCP
            return None
        
        # Use the MCP joints (base of fingers) to find palm center
        mcp_indices = [1, 5, 9, 13, 17]  # Thumb MCP, Index MCP, Middle MCP, Ring MCP, Pinky MCP
        
        sum_x = 0
        sum_y = 0
        count = 0
        
        for idx in mcp_indices:
            if idx < len(landmarks_raw):
                x, y = landmarks_raw[idx]
                sum_x += x
                sum_y += y
                count += 1
        
        if count > 0:
            return (sum_x // count, sum_y // count)
        return None
    
    def _draw_landmarks(self, frame, hand_landmarks, hand_label, bbox=None, hand_center=None):
        """Draw landmarks, connections, and additional info on the frame."""
        h, w = frame.shape[:2]
        
        # Define hand connections
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8),        # Index
            (0, 9), (9, 10), (10, 11), (11, 12),    # Middle
            (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
            (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
            (5, 9), (9, 13), (13, 17)               # Palm
        ]
        
        # Draw connections
        for connection in connections:
            if connection[0] < len(hand_landmarks) and connection[1] < len(hand_landmarks):
                pt1 = hand_landmarks[connection[0]]
                pt2 = hand_landmarks[connection[1]]
                x1, y1 = int(pt1.x * w), int(pt1.y * h)
                x2, y2 = int(pt2.x * w), int(pt2.y * h)
                cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
        
        # Draw landmarks with different colors for fingertips
        for i, lm in enumerate(hand_landmarks):
            cx, cy = int(lm.x * w), int(lm.y * h)
            # Fingertips (4,8,12,16,20) are yellow
            if i in [4, 8, 12, 16, 20]:
                cv2.circle(frame, (cx, cy), 8, (0, 255, 255), -1)  # Yellow
                cv2.circle(frame, (cx, cy), 3, (255, 255, 255), -1)
                # Add small label for fingertips in debug mode
                # (You can enable this if needed)
            else:
                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)  # Green
                cv2.circle(frame, (cx, cy), 2, (255, 255, 255), -1)
        
        #Optionally draw bounding box (commented out by default)
        # if bbox:
        #     cv2.rectangle(frame, 
        #                  (bbox['x_min'], bbox['y_min']), 
        #                  (bbox['x_min'] + bbox['width'], bbox['y_min'] + bbox['height']), 
        #                  (255, 0, 255), 2)
    
    def get_fingertip_positions(self, hand_data):
        """Get fingertip positions as a dictionary."""
        fingertips = {}
        fingertip_ids = {'thumb': 4, 'index': 8, 'middle': 12, 'ring': 16, 'pinky': 20}
        
        for name, tip_id in fingertip_ids.items():
            if tip_id < len(hand_data['landmarks_raw']):
                fingertips[name] = hand_data['landmarks_raw'][tip_id]
        
        return fingertips
    
    def get_normalized_fingertip_positions(self, hand_data):
        """Get normalized fingertip positions (0-1 range)."""
        fingertips = {}
        fingertip_ids = {'thumb': 4, 'index': 8, 'middle': 12, 'ring': 16, 'pinky': 20}
        
        for name, tip_id in fingertip_ids.items():
            if tip_id < len(hand_data['landmarks_norm']):
                fingertips[name] = hand_data['landmarks_norm'][tip_id]
        
        return fingertips
    
    def get_relative_fingertip_positions(self, hand_data):
        """Get fingertip positions relative to wrist."""
        fingertips = {}
        fingertip_ids = {'thumb': 4, 'index': 8, 'middle': 12, 'ring': 16, 'pinky': 20}
        
        for name, tip_id in fingertip_ids.items():
            if tip_id < len(hand_data['relative_landmarks']):
                fingertips[name] = hand_data['relative_landmarks'][tip_id]
        
        return fingertips
    
    def print_hand_data(self, hand_data):
        """Print comprehensive hand data for debugging."""
        if not hand_data:
            print("No hand data")
            return
        
        print(f"\n--- Hand {hand_data['hand_id'] + 1} ({hand_data['hand_label']}) ---")
        print(f"Confidence: {hand_data['confidence']:.3f}")
        
        # Print raw fingertip positions
        print("\nRaw Fingertip Positions (pixels):")
        raw_tips = self.get_fingertip_positions(hand_data)
        for finger, pos in raw_tips.items():
            print(f"  {finger}: {pos}")
        
        # Print normalized fingertip positions
        print("\nNormalized Fingertip Positions (0-1):")
        norm_tips = self.get_normalized_fingertip_positions(hand_data)
        for finger, pos in norm_tips.items():
            print(f"  {finger}: ({pos[0]:.3f}, {pos[1]:.3f})")
        
        # Print scale-invariant features
        print("\nScale-Invariant Features:")
        for feature_name, value in hand_data['scale_invariant_features'].items():
            print(f"  {feature_name}: {value:.3f}")


def flip_frame_horizontally(frame):
    """Flip the frame horizontally to create a mirror-like experience."""
    return cv2.flip(frame, 1)


def main():
    """Main function with enhanced data visualization."""
    
    # Initialize camera
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        camera = cv2.VideoCapture(1)
        if not camera.isOpened():
            print("Error: Could not open camera")
            return
    
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Initialize detector
    detector = HandLandmarkDetector(max_hands=2)
    
    print("\n" + "="*60)
    print("CONTROLS:")
    print("  'q' - Quit")
    print("  'd' - Toggle debug info")
    print("  'p' - Print detailed hand data")
    print("  'f' - Toggle mirror flip")
    print("  'n' - Print normalized coordinates")
    print("="*60)
    
    # Main loop variables
    fps = 0
    frame_count = 0
    start_time = time.time()
    debug_mode = False
    flip_enabled = True
    
    while True:
        # Read frame
        ret, frame = camera.read()
        if not ret:
            break
        
        # Detect hands with coordinate extraction
        frame, hands_data = detector.find_hands(frame, draw=True, flip_type=flip_enabled)
        
        # Calculate FPS
        frame_count += 1
        if time.time() - start_time >= 1:
            fps = frame_count
            frame_count = 0
            start_time = time.time()
        
        # Draw UI
        cv2.putText(frame, f"FPS: {fps}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Flip status
        flip_status = "ON" if flip_enabled else "OFF"
        flip_color = (0, 255, 0) if flip_enabled else (0, 0, 255)
        cv2.putText(frame, f"Mirror: {flip_status}", 
                    (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, flip_color, 1)
        
        if hands_data:
            cv2.putText(frame, f"Hands: {len(hands_data)}", (10, 80),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            if debug_mode:
                y = 105
                for i, hand in enumerate(hands_data):
                    # Basic hand info
                    text = f"H{i+1}: {hand['hand_label']} ({hand['confidence']:.2f})"
                    cv2.putText(frame, text, (10, y), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                    y += 20
                    
                    # Show some scale-invariant features
                    if 'scale_invariant_features' in hand:
                        features = hand['scale_invariant_features']
                        if 'hand_openness' in features:
                            open_text = f"  Openness: {features['hand_openness']:.2f}"
                            cv2.putText(frame, open_text, (10, y),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                            y += 20
        else:
            cv2.putText(frame, "No hands detected", (10, 80),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Show frame
        cv2.imshow('Hand Detection - Task 2.4', frame)
        
        # Handle keys
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('d'):
            debug_mode = not debug_mode
        elif key == ord('f'):
            flip_enabled = not flip_enabled
            print(f"Mirror mode: {'ON' if flip_enabled else 'OFF'}")
        elif key == ord('p') and hands_data:
            print("\n" + "="*50)
            print("DETAILED HAND DATA")
            print("="*50)
            for hand in hands_data:
                detector.print_hand_data(hand)
        elif key == ord('n') and hands_data:
            print("\n" + "="*50)
            print("NORMALIZED COORDINATES")
            print("="*50)
            for hand in hands_data:
                norm_tips = detector.get_normalized_fingertip_positions(hand)
                print(f"\n{hand['hand_label']} Hand (normalized):")
                for finger, (x, y) in norm_tips.items():
                    print(f"  {finger}: ({x:.3f}, {y:.3f})")
    
    # Cleanup
    camera.release()
    cv2.destroyAllWindows()
    print("\nProgram ended successfully.")


if __name__ == "__main__":
    main()