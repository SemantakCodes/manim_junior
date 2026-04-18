"""Pure easing functions: t ∈ [0, 1] → t' ∈ [0, 1]."""


def linear(t: float) -> float:
    """No-op easing — constant rate of change."""
    return t


def ease_in_quad(t: float) -> float:
    """Accelerate from zero velocity (quadratic)."""
    return t * t


def ease_out_quad(t: float) -> float:
    """Decelerate to zero velocity (quadratic)."""
    return 1.0 - (1.0 - t) ** 2


def ease_in_out_quad(t: float) -> float:
    """Accelerate then decelerate (quadratic)."""
    if t < 0.5:
        return 2.0 * t * t
    return 1.0 - (-2.0 * t + 2.0) ** 2 / 2.0


def ease_in_cubic(t: float) -> float:
    """Accelerate from zero velocity (cubic)."""
    return t ** 3


def ease_out_cubic(t: float) -> float:
    """Decelerate to zero velocity (cubic)."""
    return 1.0 - (1.0 - t) ** 3


def ease_in_out_cubic(t: float) -> float:
    """Accelerate then decelerate (cubic)."""
    if t < 0.5:
        return 4.0 * t ** 3
    return 1.0 - (-2.0 * t + 2.0) ** 3 / 2.0


def smooth_step(t: float) -> float:
    """Smooth Hermite interpolation (3t² - 2t³)."""
    return t * t * (3.0 - 2.0 * t)
