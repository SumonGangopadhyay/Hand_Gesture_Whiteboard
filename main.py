import cv2
import numpy as np
import time
from utils.hand_detector import HandDetector
from utils.gesture_utils import fingers_up, is_gesture
from utils.drawing_utils import create_canvas, draw_line, erase_area

# -----------------------------
# EXTRA UTILS
# -----------------------------
def erase_line(canvas, p1, p2, radius=40):
    if p1 is None or p2 is None:
        return
    cv2.line(canvas, p1, p2, (0, 0, 0), radius * 2)

# -----------------------------
# INITIAL SETUP
# -----------------------------
cap = cv2.VideoCapture(0)
# Set higher resolution for bigger screen
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 960)
cap.set(cv2.CAP_PROP_FPS, 30)
detector = HandDetector("models/hand_landmarker.task")

canvas = None
prev_point = None

# FIX: drawing state
is_drawing = False
is_erasing = False

# Position smoothing for better accuracy
smoothing_state = {'ix': 0, 'iy': 0}
smoothing_factor = 0.6  # 0-1, higher = smoother but more laggy

current_color = (255, 0, 255)
colors = [(255,0,255), (0,255,0), (255,0,0), (0,0,255), (255,255,0)]

canvas_history = []
max_history = 10

save_cooldown = 0
color_cooldown = 0
clear_cooldown = 0

last_action_frame = 0

# -----------------------------
# BUTTON SETTINGS
# -----------------------------
button_width = 100
button_height = 50

save_x, save_y = 20, 20
clear_x, clear_y = 140, 20

print("Press Q to quit")

# Set window size for bigger display
cv2.namedWindow("Gesture Whiteboard", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Gesture Whiteboard", 1280, 960)

# -----------------------------
# MAIN LOOP
# -----------------------------
frame_count = 0
detect_every = 1  # Detect hand every frame for better drawing responsiveness
last_hand = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    if canvas is None:
        canvas = create_canvas(w, h)
        canvas_history.append(canvas.copy())

    # Cooldowns
    if save_cooldown > 0:
        save_cooldown -= 1
    if color_cooldown > 0:
        color_cooldown -= 1
    if clear_cooldown > 0:
        clear_cooldown -= 1

    # Hand detection throttling
    hand = last_hand
    if frame_count % detect_every == 0:
        timestamp = int(cap.get(cv2.CAP_PROP_POS_MSEC))
        hand = detector.detect(frame, timestamp)
        last_hand = hand

    action_performed = False

    if hand:
        fingers = fingers_up(hand)

        # Get raw finger position
        raw_ix = int(hand[8].x * w)
        raw_iy = int(hand[8].y * h)
        
        # Apply smoothing for better accuracy
        ix = int(smoothing_state['ix'] * smoothing_factor + raw_ix * (1 - smoothing_factor))
        iy = int(smoothing_state['iy'] * smoothing_factor + raw_iy * (1 - smoothing_factor))
        
        # Update smoothed values for next frame
        smoothing_state['ix'] = ix
        smoothing_state['iy'] = iy

        # -----------------------------
        # SAVE BUTTON
        # -----------------------------
        if (save_x <= ix <= save_x + button_width and
            save_y <= iy <= save_y + button_height and
            fingers[1] and save_cooldown == 0):

            filename = f"my_drawing_{int(time.time())}.png"
            cv2.imwrite(filename, canvas)
            print(f"Saved: {filename}")
            save_cooldown = 30

        # -----------------------------
        # CLEAR BUTTON
        # -----------------------------
        if (clear_x <= ix <= clear_x + button_width and
            clear_y <= iy <= clear_y + button_height and
            fingers[1] and clear_cooldown == 0):

            canvas_history.append(canvas.copy())
            canvas = create_canvas(w, h)
            prev_point = None
            is_drawing = False
            is_erasing = False
            clear_cooldown = 30

        # -----------------------------
        # ☝️ MOVE (1 finger - Index only)
        # -----------------------------
        if is_gesture(fingers, [None, True, False, False, False]):
            is_drawing = False
            is_erasing = False
            prev_point = None

        # -----------------------------
        # ✌️ DRAW (2 fingers - Index + Middle)
        # -----------------------------
        elif is_gesture(fingers, [None, True, True, False, False]):
            if not is_drawing:
                prev_point = (ix, iy)
                is_drawing = True
                is_erasing = False

            draw_line(canvas, prev_point, (ix, iy), current_color)
            prev_point = (ix, iy)
            action_performed = True

            cv2.putText(frame, "DRAW", (20,90),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        # -----------------------------
        # 👌 ERASE (3 fingers - Index + Middle + Ring)
        # -----------------------------
        elif is_gesture(fingers, [None, True, True, True, False]):
            erase_area(canvas, (ix, iy), 20)
            prev_point = None
            is_drawing = False
            is_erasing = True
            action_performed = True

            cv2.rectangle(frame, (ix - 25, iy - 25), (ix + 25, iy + 25), (0,0,255), 2)
            cv2.putText(frame, "ERASE", (20,90),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

    # -----------------------------
    # SAVE HISTORY
    # -----------------------------
    if action_performed and frame_count - last_action_frame > 5:
        canvas_history.append(canvas.copy())
        last_action_frame = frame_count
        if len(canvas_history) > max_history:
            canvas_history.pop(0)

    # -----------------------------
    # DRAW BUTTONS
    # -----------------------------
    cv2.rectangle(frame, (save_x, save_y),
                  (save_x + button_width, save_y + button_height),
                  (0,255,0), -1)
    cv2.putText(frame, "SAVE", (save_x + 10, save_y + 35),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

    cv2.rectangle(frame, (clear_x, clear_y),
                  (clear_x + button_width, clear_y + button_height),
                  (0,0,255), -1)
    cv2.putText(frame, "CLEAR", (clear_x + 5, clear_y + 35),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

    # -----------------------------
    # COMBINE VIEW
    # -----------------------------
    combined = cv2.addWeighted(frame, 0.7, canvas, 0.3, 0)
    cv2.imshow("Gesture Whiteboard", combined)

    if cv2.waitKey(1) & 0xFF in [ord('q'), ord('Q')]:
        break

    frame_count += 1

# -----------------------------
# CLEANUP
# -----------------------------
cap.release()
cv2.destroyAllWindows()
