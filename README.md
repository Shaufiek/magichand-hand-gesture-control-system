# Hand Gesture Control System

Control VLC media player with hand gestures using your Webcam

## What You Need

- Python 3.8 or higher
- A webcam
- VLC media player installed
- Some music or video files

## Quick Setup

### 1. Get the code
Put all the following files in your folder:
- `main.py` - Detects hands and gestures
- `media_controller.py` - Sends commands to VLC for control
- `app.py` - NEW: Web app interface
- `run.py` - Original program (optional)
- `run.bat` - NEW: One-click launcher for Windows
- `config.json` - Settings
- `requirements.txt` - Packages to install

### 2. Setting Up Your Python Environment

#### What is a Virtual Environment?
A virtual environment keeps your project packages separate from other Python projects.

#### a. Open Terminal
Open PowerShell (Windows) or Terminal (Mac/Linux) in your project folder:
cd C:\your-folder

#### b. Create Virtual Environment
python -m venv venv

#### c. Activate the Environment
**Windows:** `venv\Scripts\activate` or `venv\Scripts\Activate.ps1`  
**Mac/Linux:** `source venv/bin/activate`

### 3. Install required packages
pip install -r requirements.txt

### 4. Prepare your music
Create a `music` folder in your project directory for your music/video files:

your-folder/
  ├── music/
  │    ├── track1.mp4
  │    ├── track2.mp4
  │    └── ...
  ├── main.py
  ├── app.py
  └── ...

## How to Use

### Option 1: Web App (EASIEST - Recommended)
1. **Double-click `run.bat`**
2. Your browser will open automatically
3. Open VLC manually and load your music
4. Click "Start Camera" in the web app
5. Make gestures to control VLC!
6. Click "Stop Camera" or close the browser to quit

### Option 2: Original Program (Terminal)
1. Run: `python run.py`
2. Follow the terminal instructions
3. Press 'q' in the camera window to quit

## Gestures

| Gesture | Command |
|---------|---------|
| ✋ Open Palm | Play / Pause |
| 👊 Fist | Stop |
| ✌️ Two Fingers | Next Track |
| 🤟 Three Fingers | Previous Track |
| 🤏 Pinch | Volume Control |

**Pinch tip:** Close together = quieter, far apart = louder

## Troubleshooting

**Gestures not working?**
- Make sure your hand is in good lighting
- Stand about arms-length from camera
- Hold gestures for a second

**VLC not responding?**
- Click on the VLC window to make it active
- Check that VLC is open and playing

**Camera not working?**
- Try changing `device_id` in `config.json` from 0 to 1

## Customize Settings

Edit `config.json` to adjust:
- Camera resolution
- Gesture cooldown time
- Pinch sensitivity