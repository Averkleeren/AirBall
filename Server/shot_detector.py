"""ShotDetector

Detects basketball shooting motions from a stream of MediaPipe pose
landmarks and produces a structured JSON description of each shot.
"""
from __future__ import annotations

import json
import math
import os
import uuid
from collections import deque
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import mediapipe as mp

_POSE = mp.solutions.pose.PoseLandmark


class ShotDetector:
    """Stateful shot detector.

    Call :meth:`update` on every frame.  It returns a shot-analysis dict
    when a complete shooting motion has been captured, otherwise ``None``.
    """

    # --- Tunable detection thresholds ---
    VY_START_NORM: float = 1.2   # body-lengths / s to start a shot
    VY_END_NORM: float = 0.25    # body-lengths / s to end a shot
    ELBOW_EXT_MIN: float = 5.0   # degrees increase to confirm arm drive
    KNEE_BEND_START: float = 4.0 # degrees below baseline to detect load
    MAX_DURATION: float = 3.0    # seconds - force-end runaway shots
    MIN_DURATION: float = 0.08   # seconds - ignore very short blips

    def __init__(self, buffer_size: int = 90, vel_window: int = 3) -> None:
        """
        Parameters
        ----------
        buffer_size : rolling frame buffer kept for pre-roll context
        vel_window  : number of frames used to compute smoothed wrist velocity
        """
        self.buf: deque[Dict[str, Any]] = deque(maxlen=buffer_size)
        self.vel_window = max(2, vel_window)
        self.in_shot: bool = False
        self.current_shot_frames: List[Dict[str, Any]] = []

        # Landmark indices (shortcuts)
        self.RW = _POSE.RIGHT_WRIST.value
        self.LW = _POSE.LEFT_WRIST.value
        self.RE = _POSE.RIGHT_ELBOW.value
        self.LE = _POSE.LEFT_ELBOW.value
        self.RS = _POSE.RIGHT_SHOULDER.value
        self.LS = _POSE.LEFT_SHOULDER.value

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(
        self,
        lm_list,
        frame_w: int,
        frame_h: int,
        ts: float,
        ball_speed_px_s: Optional[float] = None,
    ) -> Optional[Dict[str, Any]]:
        """Process one frame of landmarks.

        Parameters
        ----------
        lm_list        : MediaPipe NormalizedLandmarkList landmarks
        frame_w/h      : full-resolution frame dimensions
        ts             : timestamp in seconds
        ball_speed_px_s: optional speed from BallColorTracker (px/frame)

        Returns a shot dict when a shot finishes, else None.
        """
        pix = self._to_pixel_list(lm_list, frame_w, frame_h)
        entry: Dict[str, Any] = {
            'lm': lm_list,
            'ts': ts,
            'pix': pix,
            'scale': self._compute_scale(pix),
            'ball_speed': ball_speed_px_s,
        }
        self.buf.append(entry)

        if len(self.buf) < self.vel_window:
            return None

        side = self._choose_side(lm_list)
        indices = self._side_indices(side)
        wrist_idx = indices['wrist']
        elbow_idx = indices['elbow']
        shoulder_idx = indices['shoulder']

        vy_norm = self._wrist_velocity_norm(wrist_idx)

        # Elbow angle change (last two frames)
        a, b = self.buf[-2], self.buf[-1]
        elbow_prev = self._elbow_angle(a['pix'], shoulder_idx, elbow_idx, wrist_idx)
        elbow_now  = self._elbow_angle(b['pix'], shoulder_idx, elbow_idx, wrist_idx)

        knee_idx  = indices['knee']
        hip_idx   = indices['hip']
        ankle_idx = indices['ankle']

        knee_prev = self._joint_angle(a['pix'], hip_idx, knee_idx, ankle_idx)
        knee_now  = self._joint_angle(b['pix'], hip_idx, knee_idx, ankle_idx)

        if not self.in_shot:
            baseline_knee = (
                float(np.mean([self._joint_angle(e['pix'], hip_idx, knee_idx, ankle_idx)
                                for e in list(self.buf)[:-2]]))
                if len(self.buf) > 5 else knee_prev
            )
            knee_drop = baseline_knee - knee_now
            arm_drive = (
                vy_norm > self.VY_START_NORM
                and (elbow_now - elbow_prev) > self.ELBOW_EXT_MIN
            )
            if arm_drive or knee_drop > self.KNEE_BEND_START:
                self.in_shot = True
                self.current_shot_frames = list(self.buf)
            return None

        # --- Currently tracking a shot ---
        self.current_shot_frames.append(b)

        start_ts = self.current_shot_frames[0]['ts']
        duration = b['ts'] - start_ts
        shot_ending = (
            (vy_norm < self.VY_END_NORM and duration > self.MIN_DURATION)
            or duration > self.MAX_DURATION
        )

        if shot_ending:
            shot = self._finalize_shot(
                self.current_shot_frames, indices
            )
            self.in_shot = False
            self.current_shot_frames = []
            return shot

        return None

    # ------------------------------------------------------------------
    # Geometry helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_pixel_list(lm_list, frame_w: int, frame_h: int):
        """Convert normalised landmarks to (x_px, y_px, z, vis) tuples."""
        return [
            (
                float(lm.x) * frame_w,
                float(lm.y) * frame_h,
                float(lm.z),
                float(getattr(lm, 'visibility', 0.0)),
            )
            for lm in lm_list
        ]

    def _compute_scale(self, pix) -> float:
        """Body scale in pixels (shoulder width or torso length, whichever larger)."""
        try:
            ls = pix[_POSE.LEFT_SHOULDER.value]
            rs = pix[_POSE.RIGHT_SHOULDER.value]
            lh = pix[_POSE.LEFT_HIP.value]
            rh = pix[_POSE.RIGHT_HIP.value]
            sw = self._dist2d(ls, rs)
            tl = (self._dist2d(ls, lh) + self._dist2d(rs, rh)) / 2.0
            return float(max(sw, tl, 1.0))
        except Exception:
            return 1.0

    def _choose_side(self, lm_list) -> str:
        try:
            rv = lm_list[self.RW].visibility
            lv = lm_list[self.LW].visibility
            return 'right' if rv >= lv else 'left'
        except Exception:
            return 'right'

    def _side_indices(self, side: str) -> Dict[str, int]:
        r = side == 'right'
        return {
            'wrist':    self.RW   if r else self.LW,
            'elbow':    self.RE   if r else self.LE,
            'shoulder': self.RS   if r else self.LS,
            'knee':     (_POSE.RIGHT_KNEE.value   if r else _POSE.LEFT_KNEE.value),
            'ankle':    (_POSE.RIGHT_ANKLE.value  if r else _POSE.LEFT_ANKLE.value),
            'hip':      (_POSE.RIGHT_HIP.value    if r else _POSE.LEFT_HIP.value),
        }

    def _wrist_velocity_norm(self, wrist_idx: int) -> float:
        """Smoothed upward wrist velocity normalised by body scale (body-lengths/s)."""
        window = list(self.buf)[-self.vel_window:]
        if len(window) < 2:
            return 0.0
        ys  = [e['pix'][wrist_idx][1] for e in window]
        tss = [e['ts'] for e in window]
        # total vertical displacement over window (upward = positive)
        dy = ys[0] - ys[-1]
        dt = tss[-1] - tss[0] if tss[-1] != tss[0] else 1 / 30
        vy = dy / dt
        scale = float(self.buf[-1].get('scale', 1.0) or 1.0)
        return vy / scale

    @staticmethod
    def _elbow_angle(pix, sh_idx, el_idx, wr_idx) -> float:
        sh = (pix[sh_idx][0], pix[sh_idx][1])
        el = (pix[el_idx][0], pix[el_idx][1])
        wr = (pix[wr_idx][0], pix[wr_idx][1])
        return ShotDetector._angle3(sh, el, wr)

    @staticmethod
    def _joint_angle(pix, a_idx, b_idx, c_idx) -> float:
        a = (pix[a_idx][0], pix[a_idx][1])
        b = (pix[b_idx][0], pix[b_idx][1])
        c = (pix[c_idx][0], pix[c_idx][1])
        return ShotDetector._angle3(a, b, c)

    @staticmethod
    def _angle3(a, b, c) -> float:
        """Angle at vertex b in the triangle a-b-c (degrees)."""
        v1 = (a[0] - b[0], a[1] - b[1])
        v2 = (c[0] - b[0], c[1] - b[1])
        dot  = v1[0]*v2[0] + v1[1]*v2[1]
        mag1 = math.hypot(*v1)
        mag2 = math.hypot(*v2)
        if mag1 * mag2 == 0:
            return 0.0
        return math.degrees(math.acos(max(-1.0, min(1.0, dot / (mag1 * mag2)))))

    @staticmethod
    def _dist2d(p1, p2) -> float:
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    # ------------------------------------------------------------------
    # Shot finalisation
    # ------------------------------------------------------------------

    def _finalize_shot(
        self,
        frames: List[Dict[str, Any]],
        indices: Dict[str, int],
    ) -> Dict[str, Any]:
        """Build and save the structured shot JSON from a captured frame sequence."""
        if not frames:
            return {}

        wi  = indices['wrist']
        eli = indices['elbow']
        shi = indices['shoulder']
        ki  = indices['knee']
        hi  = indices['hip']
        ai  = indices['ankle']
        ni  = _POSE.NOSE.value

        start_ts = frames[0]['ts']
        end_ts   = frames[-1]['ts']
        ts_list  = [f['ts'] for f in frames]

        dts = [ts_list[i] - ts_list[i-1] for i in range(1, len(ts_list))]
        median_dt = float(np.median(dts)) if dts else 1/30
        fps = 1.0 / median_dt if median_dt > 0 else 30.0

        # --- Per-frame metrics ---
        elbow_angles     = []
        knee_angles      = []
        hip_angles       = []
        wrist_positions  = []
        shoulder_pos     = []
        head_positions   = []
        scales           = []
        forearm_angles   = []

        for f in frames:
            pix = f['pix']
            scales.append(f.get('scale', 1.0))

            sh  = (pix[shi][0], pix[shi][1])
            el  = (pix[eli][0], pix[eli][1])
            wr  = (pix[wi][0],  pix[wi][1])
            hip = (pix[hi][0],  pix[hi][1])
            kn  = (pix[ki][0],  pix[ki][1])
            ank = (pix[ai][0],  pix[ai][1])
            nose = (pix[ni][0], pix[ni][1]) if ni < len(pix) else (sh[0], sh[1] - 100)

            elbow_angles.append(self._angle3(sh, el, wr))
            knee_angles.append(self._angle3(hip, kn, ank))
            hip_angles.append(self._angle3(sh, hip, kn))
            wrist_positions.append({'x': wr[0], 'y': wr[1]})
            shoulder_pos.append({'x': sh[0], 'y': sh[1]})
            head_positions.append({'x': nose[0], 'y': nose[1]})
            forearm_angles.append(math.atan2(wr[1] - el[1], wr[0] - el[0]))

        scale = float(np.median(scales)) if scales else 1.0
        wrist_ys = [p['y'] for p in wrist_positions]

        # Key frame indices
        release_i = int(np.argmin(wrist_ys))
        load_i    = int(np.argmin(knee_angles))
        release_ts = ts_list[release_i]
        load_ts    = ts_list[load_i]

        # Hip extension start
        HIP_EXT_THRESH = 4.0
        hip_at_load = hip_angles[load_i]
        hip_ext_i = next(
            (i for i in range(load_i, len(hip_angles))
             if hip_angles[i] - hip_at_load > HIP_EXT_THRESH),
            None,
        )
        hip_ext_ts = ts_list[hip_ext_i] if hip_ext_i is not None else None

        # Elbow extension start
        ELBOW_EXT_THRESH = 5.0
        elbow_min = float(np.min(elbow_angles[:release_i + 1]))
        elbow_ext_i = next(
            (i for i in range(load_i, release_i + 1)
             if elbow_angles[i] - elbow_min > ELBOW_EXT_THRESH),
            None,
        )
        elbow_ext_ts = ts_list[elbow_ext_i] if elbow_ext_i is not None else None

        # Wrist snap (max forearm angular velocity)
        fa_vel = [
            abs((forearm_angles[i] - forearm_angles[i-1])
                / (dts[i-1] if i - 1 < len(dts) and dts[i-1] > 0 else median_dt))
            for i in range(1, len(forearm_angles))
        ]
        if fa_vel:
            snap_i    = int(np.argmax(fa_vel)) + 1
            snap_ts   = ts_list[snap_i]
            snap_av   = float(fa_vel[snap_i - 1])
        else:
            snap_ts = None
            snap_av = 0.0

        # Sequencing
        leg_before_arm = (
            hip_ext_ts < elbow_ext_ts
            if hip_ext_ts and elbow_ext_ts else None
        )
        leg_to_elbow_delay = (
            float(elbow_ext_ts - hip_ext_ts)
            if hip_ext_ts and elbow_ext_ts else None
        )

        # Release-relative heights
        rel_head_y     = (head_positions[release_i]['y'] - wrist_positions[release_i]['y']) / scale
        rel_shoulder_y = (shoulder_pos[release_i]['y']   - wrist_positions[release_i]['y']) / scale

        # Head stability
        r0 = max(0, release_i - 5)
        r1 = min(len(head_positions) - 1, release_i + 5)
        head_ys = [head_positions[i]['y'] for i in range(r0, r1 + 1)]
        head_var = float(np.var(head_ys) / (scale * scale)) if head_ys else 0.0

        # Follow-through
        follow_start_i = follow_end_i = None
        FLEX_THRESH = 0.15  # radians
        if forearm_angles:
            ref_ang = forearm_angles[release_i]
            for i in range(release_i + 1, len(forearm_angles)):
                if abs(forearm_angles[i] - ref_ang) > FLEX_THRESH:
                    follow_start_i = i
                    break
            if follow_start_i is not None:
                hold = follow_start_i
                while hold < len(forearm_angles) and abs(forearm_angles[hold] - ref_ang) > FLEX_THRESH:
                    hold += 1
                follow_end_i = hold

        follow_start_ts = ts_list[follow_start_i] if follow_start_i is not None else None
        follow_end_ts   = (
            ts_list[follow_end_i]
            if follow_end_i is not None and follow_end_i < len(ts_list)
            else None
        )
        follow_hold = (
            float(follow_end_ts - follow_start_ts)
            if follow_start_ts and follow_end_ts else 0.0
        )

        # Peak wrist vertical speed (upward positive, px/s)
        if dts and len(wrist_ys) > 1:
            # ys decrease as wrist moves up => negate diff for upward speed
            peak_wrist_v = float(np.max(
                -np.diff(wrist_ys) / np.maximum(np.array(dts), 1e-6)
            ))
        else:
            peak_wrist_v = 0.0

        # Average ball speed during shot (optional)
        ball_speeds = [f['ball_speed'] for f in frames if f.get('ball_speed') is not None]
        avg_ball_speed = float(np.mean(ball_speeds)) if ball_speeds else None

        # ------------------------------------------------------------------
        shot_id = str(uuid.uuid4())
        shot = {
            'id': shot_id,
            'detection_window': {
                'start': start_ts, 'end': end_ts,
                'duration': end_ts - start_ts,
            },
            'fps': float(fps),
            'phases': {
                'set':                   {'ts': float(start_ts)},
                'load':                  {'ts': float(load_ts), 'knee_angle_deg': float(knee_angles[load_i])},
                'hip_extension_start':   {'ts': float(hip_ext_ts) if hip_ext_ts else None},
                'elbow_extension_start': {'ts': float(elbow_ext_ts) if elbow_ext_ts else None},
                'wrist_snap':            {'ts': float(snap_ts) if snap_ts else None,
                                          'angular_velocity_rad_s': snap_av},
                'release':               {'ts': float(release_ts)},
                'follow_through':        {
                    'start_ts': follow_start_ts,
                    'end_ts': follow_end_ts,
                    'hold_duration': follow_hold,
                },
            },
            'timing': {
                'leg_drive_before_arm_extension': leg_before_arm,
                'leg_to_elbow_delay_s': leg_to_elbow_delay,
            },
            'metrics': {
                'angles': {
                    'elbow': {
                        'at_set_deg':     float(elbow_angles[0]),
                        'at_load_deg':    float(elbow_angles[load_i]),
                        'at_release_deg': float(elbow_angles[release_i]),
                    },
                    'knee': {
                        'min_during_load_deg': float(knee_angles[load_i]),
                        'at_release_deg':      float(knee_angles[release_i]),
                    },
                    'hip': {
                        'at_load_deg':          float(hip_angles[load_i]),
                        'peak_extension_deg':   float(max(hip_angles)),
                    },
                },
                'velocities': {
                    'peak_wrist_upward_px_s':          peak_wrist_v,
                    'peak_forearm_angular_velocity_rad_s': float(max(fa_vel)) if fa_vel else 0.0,
                    'avg_ball_speed_px_frame':         avg_ball_speed,
                },
                'release': {
                    'ts':                      float(release_ts),
                    'wrist_y_px':              float(wrist_positions[release_i]['y']),
                    'wrist_above_head_norm':   rel_head_y,
                    'wrist_above_shoulder_norm': rel_shoulder_y,
                },
                'follow_through': {'hold_duration_s': follow_hold},
                'stability':      {'head_vertical_variance_norm': head_var},
            },
            'frame_count': len(frames),
        }

        # Persist to Shots/
        try:
            os.makedirs('Shots', exist_ok=True)
            with open(os.path.join('Shots', f'shot_{shot_id}.json'), 'w') as f:
                json.dump(shot, f, indent=2)
        except Exception:
            pass

        return shot
