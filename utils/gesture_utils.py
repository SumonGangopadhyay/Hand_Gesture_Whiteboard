def fingers_up(hand):
    fingers = []

    # Determine hand side: if pinky tip (20) x > index tip (8) x, it's right hand
    is_right_hand = hand[20].x > hand[8].x

    # Thumb: for right hand, tip > IP joint x; for left, tip < IP joint x
    if is_right_hand:
        fingers.append(hand[4].x > hand[3].x)
    else:
        fingers.append(hand[4].x < hand[3].x)

    # Other fingers: tip y < PIP y (assuming palm facing camera)
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]

    for tip, pip in zip(tips, pips):
        fingers.append(hand[tip].y < hand[pip].y)

    return fingers

def is_gesture(fingers, pattern):
    """
    Check if fingers match the pattern with some tolerance.
    pattern: list of True/False for required state, or None for don't care
    """
    for i, req in enumerate(pattern):
        if req is not None and fingers[i] != req:
            return False
    return True