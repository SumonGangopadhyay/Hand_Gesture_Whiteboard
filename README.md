# Hand Gesture Whiteboard 🖐️✍️

A computer-vision based **air whiteboard** that lets you draw, erase, move, change colors, undo, and save your work using **hand gestures** captured from a webcam.

Built using **Python, OpenCV, and MediaPipe (Tasks API)**.

---

## 🚀 Features

| Gesture | Action |
|------|------|
| ☝️ 1 finger (Index) | Move pointer (no drawing) |
| ✌️ 2 fingers (Index + Middle) | Draw / write |
| 👌 3 fingers (Index + Middle + Ring) | Erase |
| 👍 Thumb + Index | Change color |
| 🤞 Index + Pinky | Undo last action |
| Touch SAVE button with index finger | Save drawing as image |
| Touch CLEAR button with index finger | Clear entire canvas |

- **Improved Drawing**: Thicker lines (12px) and frame-by-frame detection for smoother fast drawing
- **Simple Gesture System**: 1 finger move, 2 fingers draw, 3 fingers erase
- **Continuous Erase**: Hold 3 fingers to erase continuously at finger position

---

## 🧠 Tech Stack

- Python 3.10+
- OpenCV
- MediaPipe Tasks API
- NumPy

---

## 📁 Project Structure