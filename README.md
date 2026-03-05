# Hand Gesture Control System

Control VLC media player with hand gestures using your Webcam

## What You Need

- Python 3.8 or higher
- A webcam
- VLC media player installed
- Some music or video files

## Quick Setup

### 1. Get the code
Put all these files in one folder named "hand-gesture-control-system":
- `main.py` - Detects hands and gestures
- `media_controller.py` - Sends commands to VLC for control
- `run.py` - Main program to start system and connect everything
- `config.json` - Settings
- `requirements.txt` - Packages to install


### 2. Setting Up Your Python Environment

#### What is a Virtual Environment?
A virtual environment keeps your project packages separate from other Python projects.


#### a. Open Terminal
Open PowerShell (Windows) or Terminal (Mac/Linux) in your project folder:
cd C:\hand-gesture-control-system

#### b. Create Virtual Environment
In PowerShell (Windows) or Terminal (Mac/Linux) run the following command:
python -m venv venv

#### c. Activate the Environment
In PowerShell (Windows) or Terminal (Mac/Linux) run the following command:
Windows: venv\Scripts\activate
Max/Linux: source venv/bin/activate

### 3. Install required packages in your created environment
Open terminal in your folder and run:
pip install -r requirements.txt

### 4. Prepare your music
Create a music folder in your project directory and add your MP3 files:

text
your-folder/
  ├── music/
  │    ├── track1.mp3
  │    ├── track2.mp3
  │    └── ...
  ├── main.py
  ├── run.py
  └── ...



### 5. How to use

Step 1: Open VLC
- Launch VLC manually
- Load your music/ files
- Click on the VLC window



Step 2: Run the program
bash
python run.py


Step 3: Make gestures
Stand in front of your camera and use these gestures:

✋ Open palm:	Play / Pause
👊 Fist:	Stop
✌️ Two fingers:	Next track
🤟 Three fingers:	Previous track
🤏 Pinch:	Volume control

Pinch tip: Close together = quieter, far apart = louder



Step 4: Quit
Press q in the camera window to exit



### 6. Troubleshooting

Gestures not working?

- Make sure your hand is in good lightning
- Stand about arms-length from camera
- Hold gestures for a second



VLC not responding?

- Click on the VLC window to make it active
- Check that VLC is open and playing



Camera not working?

- Try changing device_id in config.json from 0 to 1



### 7. Customize Settings

Edit config.json to adjust:

- Camera resolution
- Gesture cooldown time
- Pinch sensitivity

