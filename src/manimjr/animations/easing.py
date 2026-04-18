import math

def smooth(t):
    # This is a 'Sigmoid' style curve: slow start, fast middle, slow end.
    # It’s the standard 'Ease In Out'
    return t * t * (3 - 2 * t)

def ease_out_quint(t):
    # Very fast start, very soft landing
    return 1 - pow(1 - t, 5)