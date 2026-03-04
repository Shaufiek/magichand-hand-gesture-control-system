import cv2
import time
import os
import glob
import json
from main import HandDetector
from media_controller import MediaController

def main():
    print("\n" + "="*40)
    print("GESTURE MEDIA CONTROL")
    print("="*40)
    
    # Load config
    with open("config.json", 'r') as f:
        config = json.load(f)
    cam = config["camera"]
    
    # Find music
    tracks = []
    music = r"C:\hand-gesture-control-system\music"
    if os.path.exists(music):
        tracks = glob.glob(os.path.join(music, "*.mp3"))
    
    print(f"\n📁 {len(tracks)} tracks found")
    
    # Controller
    controller = MediaController()
    
    print("\n📺 Open VLC, load playlist, click on VLC window")
    input("Press Enter when ready...")
    
    # Camera
    cap = cv2.VideoCapture(cam["device_id"])
    if not cap.isOpened():
        cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam["frame_width"])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam["frame_height"])
    
    detector = HandDetector()
    
    print("\n" + "-"*30)
    print("GESTURES:")
    print("  ✋ PLAY/PAUSE")
    print("  👊 STOP")
    print("  ✌️ NEXT")
    print("  🤟 PREV")
    print("  🤏 VOLUME")
    print("\nPress 'q' to quit")
    print("-"*30)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        
        frame, data = detector.process_frame(frame, mirror=True)
        controller.handle_gesture(data)
        
        cv2.imshow('Gesture Control', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("\n✅ Done")

if __name__ == "__main__":
    main()