"""
Face Security Alarm System
==========================
A Python project using OpenCV that detects faces via webcam.
Register your face, then the system monitors the camera and triggers
an alarm popup when unknown persons are detected.

Perfect for learning computer vision and face detection basics!
9th class prototype project.
"""

import cv2
import numpy as np
import os
import pickle
from datetime import datetime


# ============================================================
# CONFIGURATION - Change these settings as needed
# ============================================================
KNOWN_FACES_DIR = "known_faces"      # Folder to store registered faces
MODEL_FILE = "face_model.pkl"        # Saved face recognition model
CONFIDENCE_THRESHOLD = 0.6           # How strict the recognition is (0.0-1.0)
ALARM_COOLDOWN = 3                   # Seconds between alarm triggers
CAMERA_INDEX = 0                     # 0 = default webcam, 1 = second camera, etc.
WINDOW_NAME = "Face Security Alarm System"


# ============================================================
# HELPER FUNCTIONS
# ============================================================
def ensure_directories():
    """Create necessary folders if they don't exist."""
    if not os.path.exists(KNOWN_FACES_DIR):
        os.makedirs(KNOWN_FACES_DIR)
        print(f"Created folder: {KNOWN_FACES_DIR}")


def load_face_recognizer():
    """Load the trained face recognizer from disk, or create a new one."""
    if os.path.exists(MODEL_FILE):
        with open(MODEL_FILE, 'rb') as f:
            data = pickle.load(f)
        print("Loaded existing face model.")
        return data['recognizer'], data['labels']
    else:
        # Create a new LBPH face recognizer (Local Binary Patterns Histograms)
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        labels = {}  # Maps label ID -> person name
        print("Created new face recognizer.")
        return recognizer, labels


def save_face_recognizer(recognizer, labels):
    """Save the trained face recognizer to disk."""
    data = {'recognizer': recognizer, 'labels': labels}
    with open(MODEL_FILE, 'wb') as f:
        pickle.dump(data, f)
    print("Saved face model.")


def get_face_detector():
    """Load OpenCV's pre-trained Haar Cascade face detector."""
    # This file comes with OpenCV installation
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    detector = cv2.CascadeClassifier(cascade_path)
    if detector.empty():
        raise RuntimeError("Could not load face detector. Check OpenCV installation.")
    return detector


def draw_text_with_background(img, text, position, font_scale=0.7, color=(255, 255, 255), 
                               bg_color=(0, 0, 0), thickness=2):
    """Draw text with a background rectangle for better visibility."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    x, y = position
    # Draw background rectangle
    cv2.rectangle(img, (x - 5, y - text_h - 5), (x + text_w + 5, y + baseline + 5), bg_color, -1)
    # Draw text
    cv2.putText(img, text, (x, y), font, font_scale, color, thickness)


# ============================================================
# FACE REGISTRATION MODE
# ============================================================
def register_face(recognizer, labels, detector):
    """
    Register a new face by capturing multiple samples from webcam.
    The user enters their name, then we capture 30 face images.
    """
    name = input("\nEnter the person's name: ").strip()
    if not name:
        print("Name cannot be empty!")
        return recognizer, labels

    print(f"\nRegistering face for: {name}")
    print("Look at the camera. Press SPACE to capture each sample.")
    print("We need 30 samples. Press ESC to cancel.")

    # Assign a new label ID
    label_id = len(labels)
    labels[label_id] = name

    # Create person's folder
    person_dir = os.path.join(KNOWN_FACES_DIR, name.replace(" ", "_"))
    if not os.path.exists(person_dir):
        os.makedirs(person_dir)

    face_samples = []
    count = 0

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return recognizer, labels

    while count < 30:
        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(50, 50))

        # Draw rectangle around detected face
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            draw_text_with_background(frame, f"Samples: {count}/30", (x, y - 10), 
                                      color=(0, 255, 0), bg_color=(0, 0, 0))

        cv2.imshow("Register Face - Press SPACE to capture, ESC to cancel", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == 27:  # ESC key
            print("Registration cancelled.")
            break
        elif key == 32 and len(faces) > 0:  # SPACE key
            # Take the largest face detected
            (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (200, 200))  # Standardize size
            face_samples.append(face_roi)
            
            # Save sample image
            sample_path = os.path.join(person_dir, f"{count:03d}.jpg")
            cv2.imwrite(sample_path, face_roi)
            
            count += 1
            print(f"Captured sample {count}/30")

    cap.release()
    cv2.destroyAllWindows()

    if count > 0:
        print(f"\nTraining model with {count} new samples for {name}...")
        # Add new samples to recognizer
        new_labels = np.array([label_id] * count)
        recognizer.update(face_samples, new_labels)
        save_face_recognizer(recognizer, labels)
        print(f"Successfully registered {name}!")
    else:
        print("No samples captured. Registration cancelled.")
        # Remove the label we added
        if label_id in labels:
            del labels[label_id]

    return recognizer, labels


# ============================================================
# FACE RECOGNITION / ALARM MODE
# ============================================================
def run_alarm_system(recognizer, labels, detector):
    """
    Main alarm loop: monitor webcam, recognize faces, trigger alarm for unknowns.
    """
    print("\nStarting Face Security Alarm System...")
    print("Press 'q' to quit, 'r' to register a new face.")

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    last_alarm_time = 0
    unknown_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(50, 50))

        current_time = datetime.now().timestamp()

        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (200, 200))

            # Predict using the trained recognizer
            label_id, confidence = recognizer.predict(face_roi)

            # Lower confidence = better match (LBPH returns distance)
            is_known = confidence < (100 * (1 - CONFIDENCE_THRESHOLD))

            if is_known and label_id in labels:
                name = labels[label_id]
                color = (0, 255, 0)  # Green for known
                label_text = f"KNOWN: {name} ({confidence:.1f})"
            else:
                name = "UNKNOWN"
                color = (0, 0, 255)  # Red for unknown
                label_text = f"ALARM: UNKNOWN PERSON! ({confidence:.1f})"
                
                # Trigger alarm (with cooldown)
                if current_time - last_alarm_time > ALARM_COOLDOWN:
                    trigger_alarm(frame, unknown_count)
                    last_alarm_time = current_time
                    unknown_count += 1

            # Draw rectangle and label
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            draw_text_with_background(frame, label_text, (x, y - 10), 
                                      color=color, bg_color=(0, 0, 0))

        # Draw status info
        status = f"Known faces: {len(set(labels.values()))} | Unknown detections: {unknown_count}"
        draw_text_with_background(frame, status, (10, 30), font_scale=0.6, 
                                  color=(255, 255, 255), bg_color=(0, 0, 0))
        draw_text_with_background(frame, "Press 'q' to quit | 'r' to register new face", 
                                  (10, frame.shape[0] - 20), font_scale=0.5, 
                                  color=(200, 200, 200), bg_color=(0, 0, 0))

        cv2.imshow(WINDOW_NAME, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            cap.release()
            cv2.destroyAllWindows()
            recognizer, labels = register_face(recognizer, labels, detector)
            cap = cv2.VideoCapture(CAMERA_INDEX)

    cap.release()
    cv2.destroyAllWindows()
    print("Alarm system stopped.")


def trigger_alarm(frame, count):
    """
    Trigger visual and audio alarm when unknown person detected.
    """
    print(f"\n!!! ALARM #{count + 1}: UNKNOWN PERSON DETECTED !!!")
    
    # Visual alarm - flash the screen red
    alarm_frame = frame.copy()
    overlay = np.zeros_like(alarm_frame)
    overlay[:] = (0, 0, 255)  # Red
    alarm_frame = cv2.addWeighted(alarm_frame, 0.7, overlay, 0.3, 0)
    
    draw_text_with_background(alarm_frame, "!!! INTRUDER ALERT !!!", 
                              (alarm_frame.shape[1]//2 - 200, alarm_frame.shape[0]//2),
                              font_scale=1.5, color=(255, 255, 255), bg_color=(0, 0, 255), thickness=3)
    
    cv2.imshow(WINDOW_NAME, alarm_frame)
    cv2.waitKey(500)  # Show alarm for 500ms
    
    # Audio alarm (system beep)
    try:
        import winsound
        winsound.Beep(1000, 500)  # Frequency 1000Hz, duration 500ms
    except ImportError:
        # Linux/Mac fallback
        print('\a')  # Terminal bell
    
    # Save snapshot of intruder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    snapshot_dir = "intruder_snapshots"
    if not os.path.exists(snapshot_dir):
        os.makedirs(snapshot_dir)
    snapshot_path = os.path.join(snapshot_dir, f"intruder_{timestamp}.jpg")
    cv2.imwrite(snapshot_path, frame)
    print(f"Snapshot saved: {snapshot_path}")


# ============================================================
# MAIN ENTRY POINT
# ============================================================
def main():
    print("=" * 50)
    print("  FACE SECURITY ALARM SYSTEM")
    print("  9th Class Project - Computer Vision Demo")
    print("=" * 50)

    # Setup
    ensure_directories()
    detector = get_face_detector()
    recognizer, labels = load_face_recognizer()

    # Check if we have any registered faces
    if len(labels) == 0:
        print("\nNo registered faces found!")
        print("You need to register at least one face first.")
        recognizer, labels = register_face(recognizer, labels, detector)
        
        if len(labels) == 0:
            print("No faces registered. Exiting.")
            return

    # Run the alarm system
    run_alarm_system(recognizer, labels, detector)


if __name__ == "__main__":
    main()