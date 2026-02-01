import cv2
import numpy as np

def create_canvas(w, h):
    return np.zeros((h, w, 3), dtype=np.uint8)

def draw_line(canvas, prev, curr, color=(255,0,255), thickness=12):
    if prev is not None:
        cv2.line(canvas, prev, curr, color, thickness, cv2.LINE_AA)

def erase_area(canvas, center, radius=30):
    # Use rectangle for more controlled erasing
    x, y = center
    cv2.rectangle(canvas, (x - radius, y - radius), (x + radius, y + radius), (0,0,0), -1)