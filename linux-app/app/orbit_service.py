"""Reusable 360° camera orbit (port of the Flutter orbit_service.dart).

Drives the rig by repeatedly sending `flytoview=` LookAt KML with an
incrementing heading, on a Qt timer. Never blocks the UI thread and is
cleanly cancelable. Flies smoothly to the target BEFORE orbiting to avoid an
abrupt camera jump.
"""
from PySide6.QtCore import QObject, QTimer, Signal


class OrbitService(QObject):
    state_changed = Signal(bool)   # (is_orbiting)

    def __init__(self, lg, parent=None):
        super().__init__(parent)
        self.lg = lg
        self._timer = QTimer(self)
        self._timer.setInterval(400)
        self._timer.timeout.connect(self._tick)

        self._orbiting = False
        self._moving = False
        self._step = 0
        self._flyto = None
        self._start_heading = 0.0

        # configurable
        self.steps = 60            # ticks per full 360°
        self.tilt = 72
        self.range_factor = 1.0

    @property
    def is_orbiting(self):
        return self._orbiting

    def start(self, flyto: dict) -> bool:
        if self._orbiting:
            return False
        if not self.lg.is_connected:
            return False

        lat = float(flyto.get("lat"))
        lon = float(flyto.get("lon"))
        base_range = float(flyto.get("range", 500000)) * self.range_factor
        base_tilt = float(flyto.get("tilt", self.tilt))
        self._start_heading = float(flyto.get("heading", 0))

        self._flyto = {
            "lon": lon, "lat": lat,
            "range": base_range, "tilt": base_tilt,
        }

        # 1. smooth fly to target first (no abrupt jump)
        try:
            self.lg.fly_to_smooth(self._flyto, self._start_heading)
        except Exception:
            pass

        self._step = 0
        self._moving = False
        self._orbiting = True
        self.state_changed.emit(True)
        self._timer.start()
        return True

    def _tick(self):
        if not self._orbiting:
            self._timer.stop()
            return
        if self._moving:
            return
        self._moving = True
        try:
            heading = (self._start_heading + self._step * (360.0 / self.steps)) % 360.0
            self.lg.fly_to_smooth(self._flyto, heading)
            self._step += 1
            if self._step >= self.steps:
                self._step = 0
        except Exception:
            pass
        finally:
            self._moving = False

    def stop(self):
        self._timer.stop()
        self._orbiting = False
        self._moving = False
        self._step = 0
        self._flyto = None
        self.state_changed.emit(False)
