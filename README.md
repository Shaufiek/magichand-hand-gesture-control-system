# 🖐️ MagicHand 👊

**MagicHand** is a user - friendly system  that lets you control  VLC media player using only your  hand gestures and your webcam from your laptop / pc. This allows you to simply raise your hand and control the player , without complicated remote controls or keyboards

---

## What  You Need

- Python  3.8 or higher
- A laptop / pc with a working webcam
-  VLC  media player
- Music or video files  to play

---

##  Setup

### 1.  Download the files
Make sure these files are in one folder :

📁 MagicHand/
- `app.py` - Web app interface
- `main.py` -  Hand detection
- `media_controller.py` - Sends  commands to VLC media player
- `config.json` - Settings
- `requirements.txt` - Required packages
- `run.bat` - Starts the app  with one click ( Windows )
- `magichand_logo.png` #  MagicHand logo

### 2. Setting Up  the Python Environment

####  What is a virtual environment ?
 A virtual environment ensures  that the packages for this project do  not interfere with other projects on your computer .

#### a. Open Terminal
Open PowerShell ( Windows ) or Terminal ( Mac / Linux) in your project folder :
cd C:\your-folder

#### b. Create a virtual environment
python -m venv venv

###  c. Activate  the environment
**Windows:** `venv\Scripts\activate` or `venv\Scripts\Activate.ps1`
**Mac/Linux:**  `source venv/bin/activate`

### 3.  Install the required packages
pip install -r requirements.txt

### 4.  Prepare  your music
Create a  “ music ” folder in  your project folder  and place  your files there:

📁 MagicHand/
  ├── 📁 music/
  │    ├── track1.mp4
  │    ├── track2.mp4
  │    └── ...
  ├── main.py
  ├── app.py
  └── ...

---

##  How to Use MagicHand ?

###   Web App

1. Double-click run.bat
2.  Your browser will open automatically
3. Manually open VLC media player and load your music / videos
4. Click  “ Start Camera”  in the web app
5. Make  gestures  to control VLC media player
6. Click “ Stop Camera ” or close  your browser  to stop

## Gesture Overview

| Gesture |  What it does |
|---------|---------|
| ✋ High-Five | Play / Pause |
| 👊 Fist | Stop |
|  ✌️ 2 Fingers | Next track |
| 🤟 3  Fingers | Previous track |
| 🤏 Thumb  and Index Finger Pinch | Volume up / down |

**Tip:**  The farther apart your thumb and  index finger are , the louder the volume

## Customizing Settings

**You can easily customize MagicHand through the web app itself :**

| What can you customize ? | Where ? |
|---------|---------|
| 📷 Camera ( built-in / external ) |  Settings ==> Camera |
| 🔍 Screen size  | Settings  ==>  UI Scale |
| ⏱️  Gesture response speed | Settings ==>  Delay |
| 🤏 Squeeze volume sensitivity |  Settings  == >  Squeeze Settings |
|  ✌️ Which gesture  performs which action | Settings  ==> Gesture for Action |

**Tip:**  All  settings  are automatically saved in config.json .

## Troubleshooting

| Problem | Solution |
|---------|---------|
| No  camera feed | Check that your webcam is connected . Change the `device_id` in `config.json` from 0 to 1 |
| VLC media player is not  responding  | Click on the VLC window to make it active |
|  Gestures are not recognized | Make sure your hand is n good lightning . Stand at arm ’s length. Hold each gesture for a moment |
| App does not start | Settings ==>  Check that you have  activated your venv and run `pip install -r requirements.txt` |

## Additional Tips for Users
- **Lighting:**  Make sure your hand is well - lit. If nopt then the camera won ’t see your gestures clearly
- **Distance:** Stand  about an arm ’s length  away from the  camera
-  **Patience:** Hold a gesture for 1 – 2 seconds  before the system  responds
- **VLC:** Don’t forget to click on the VLC window before making gestures

---

**MagicHand is designed to make media control accessible to everyone. The design is specificaly tailored to the needs of older adults and people with physical or cognitive disabilities.**

