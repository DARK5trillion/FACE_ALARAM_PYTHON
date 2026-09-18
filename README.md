# Face Security Alarm System 🔒

A Python project using OpenCV that detects faces via webcam. Register your face, then the system monitors the camera and triggers an alarm popup when unknown persons are detected.

Perfect for learning computer vision and face detection basics! Great 9th class prototype project.

## Features

- **Face Registration**: Capture and store multiple face samples per person
- **Real-time Recognition**: Live webcam monitoring with face detection
- **Intruder Alarm**: Visual + audio alert when unknown faces detected
- **Snapshot Capture**: Automatically saves photos of intruders with timestamps
- **Persistent Model**: Saves trained model to disk (survives restarts)
- **Multiple Users**: Register as many people as you want

## Requirements

- Python 3.7+
- Webcam
- Windows / Linux / macOS

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/DARK5trillion/FACE_ALARAM_PYTHON.git
   cd FACE_ALARAM_PYTHON
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Run the program:
```bash
python main.py
```

### First Run - Register Your Face:
1. The program will detect no registered faces
2. Enter your name when prompted
3. Look at the camera and press **SPACE** to capture 30 samples
4. Press **ESC** to cancel if needed

### Daily Use - Alarm Mode:
- **Green box + "KNOWN: Name"** = Registered person detected ✅
- **Red box + "ALARM: UNKNOWN PERSON!"** = Intruder detected 🚨
- Press **'r'** to register a new face anytime
- Press **'q'** to quit

### Alarm Features:
- 🔴 **Visual**: Screen flashes red with "INTRUDER ALERT"
- 🔊 **Audio**: System beep sound
- 📸 **Snapshot**: Saves intruder photo to `intruder_snapshots/` folder with timestamp

## Project Structure

```
FACE_ALARAM_PYTHON/
├── main.py                 # Main application
├── requirements.txt        # Python dependencies
├── face_model.pkl          # Trained model (auto-generated)
├── known_faces/            # Registered face images (auto-generated)
│   └── Person_Name/
│       ├── 000.jpg
│       ├── 001.jpg
│       └── ...
├── intruder_snapshots/     # Intruder photos (auto-generated)
│   └── intruder_20240115_143022.jpg
├── .gitignore
├── LICENSE
└── README.md
```

## How It Works

1. **Face Detection**: Uses OpenCV's Haar Cascade classifier to find faces in webcam frames
2. **Face Recognition**: Uses LBPH (Local Binary Patterns Histograms) algorithm
3. **Training**: When you register a face, it captures 30 samples and trains the model
4. **Recognition**: Compares detected faces against trained model
5. **Threshold**: Confidence threshold determines "known" vs "unknown"

## Customization

Edit these constants at the top of `main.py`:

```python
KNOWN_FACES_DIR = "known_faces"
MODEL_FILE = "face_model.pkl"
CONFIDENCE_THRESHOLD = 0.6
ALARM_COOLDOWN = 3
CAMERA_INDEX = 0
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Could not open camera" | Check webcam connection, try `CAMERA_INDEX = 1` |
| "Module not found: cv2" | Run `pip install opencv-python` |
| Poor recognition | Re-register with better lighting, increase samples |
| False alarms | Increase `CONFIDENCE_THRESHOLD` (e.g., 0.7) |
| Missed known faces | Decrease `CONFIDENCE_THRESHOLD` (e.g., 0.5) |

## License

MIT License - Feel free to use for school projects!

---

**Made for 9th Class Computer Science Project** 🎓