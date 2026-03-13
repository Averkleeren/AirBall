"""BallColorTracker

Detects a basketball in a BGR frame using HSV color masking and
maintains a rolling trail of positions plus velocity estimates.

Typical usage
-------------
    tracker = BallColorTracker()
    while capturing:
        frame = get_frame()
        result = tracker.update(frame)
        if result:
            x, y, radius = result
            trail = tracker.get_trail()   # list of (x,y) or None
            vx, vy = tracker.get_velocity()

Calibration
-----------
If the basketball colour differs from the default orange range, tweak
HSV_LOWER / HSV_UPPER.  Use a colour picker on a sample frame to find
good values; HSV hue is 0-179 in OpenCV.
"""

from __future__ import annotations

import math
from collections import deque
from typing import Optional, Tuple

import cv2
import numpy as np

# ---------------------------------------------------------------------------
# Colour calibration constants  (OpenCV HSV: H 0-179, S 0-255, V 0-255)
# ---------------------------------------------------------------------------
HSV_LOWER = np.array([5, 100, 100], dtype=np.uint8)   # orange-ish lower bound
HSV_UPPER = np.array([25, 255, 255], dtype=np.uint8)  # orange-ish upper bound

# Morphology kernel for cleaning up the mask
_MORPH_KERNEL = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))


class BallColorTracker:
    """Track a basketball across frames using HSV color segmentation."""

    def __init__(
        self,
        trail_len: int = 20,
        min_radius: int = 8,
        max_radius: int = 120,
    ) -> None:
        """
        Parameters
        ----------
        trail_len  : number of past positions to remember
        min_radius : minimum contour enclosing-circle radius to accept (px)
        max_radius : maximum enclosing-circle radius to accept (px)
        """
        self.trail_len = trail_len
        self.min_radius = min_radius
        self.max_radius = max_radius

        self._trail: deque[Optional[Tuple[int, int]]] = deque(maxlen=trail_len)
        self._velocity: Tuple[float, float] = (0.0, 0.0)
        self._smoothed_speed: float = 0.0
        self._alpha = 0.4  # EMA smoothing factor for speed

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self, frame: np.ndarray) -> Optional[Tuple[int, int, int]]:
        """Detect the ball in *frame* and update internal state.

        Returns ``(cx, cy, radius)`` if a ball is found, else ``None``.
        The trail and velocity are updated regardless.
        """
        result = self._find_ball(frame)

        if result is not None:
            cx, cy, radius = result
            prev = self._trail[-1] if self._trail else None
            if prev is not None:
                vx = float(cx - prev[0])
                vy = float(cy - prev[1])
                self._velocity = (vx, vy)
                speed = math.hypot(vx, vy)
            else:
                self._velocity = (0.0, 0.0)
                speed = 0.0

            # Exponential moving average for smoothed speed
            self._smoothed_speed = (
                self._alpha * speed + (1 - self._alpha) * self._smoothed_speed
            )
            self._trail.append((cx, cy))
        else:
            self._trail.append(None)
            self._velocity = (0.0, 0.0)

        return result

    def get_trail(self) -> list[Optional[Tuple[int, int]]]:
        """Return the position history as a list (oldest first)."""
        return list(self._trail)

    def get_velocity(self) -> Tuple[float, float]:
        """Return the most recent (vx, vy) in pixels per frame."""
        return self._velocity

    def get_speed(self) -> float:
        """Return the exponentially smoothed speed in pixels per frame."""
        return self._smoothed_speed

    def reset(self) -> None:
        """Clear all accumulated state."""
        self._trail.clear()
        self._velocity = (0.0, 0.0)
        self._smoothed_speed = 0.0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _find_ball(
        self, frame: np.ndarray
    ) -> Optional[Tuple[int, int, int]]:
        """Return (cx, cy, radius) of the best ball candidate or None."""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, HSV_LOWER, HSV_UPPER)

        # Clean up noise
        mask = cv2.erode(mask, _MORPH_KERNEL, iterations=1)
        mask = cv2.dilate(mask, _MORPH_KERNEL, iterations=2)

        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if not contours:
            return None

        # Pick the largest contour that fits the radius constraints
        best = None
        best_area = 0
        for cnt in contours:
            (cx, cy), radius = cv2.minEnclosingCircle(cnt)
            radius = int(radius)
            if not (self.min_radius <= radius <= self.max_radius):
                continue
            area = cv2.contourArea(cnt)
            # Circularity check: area / (pi * r^2) should be > 0.4
            if area / (math.pi * radius * radius) < 0.4:
                continue
            if area > best_area:
                best_area = area
                best = (int(cx), int(cy), radius)

        return best
