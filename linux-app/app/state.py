"""Application state: persisted settings (QSettings), the skill catalog, and
background SSH action dispatch. Uses Qt signals so long SSH calls never block
the UI thread."""
import os

from PySide6.QtCore import QObject, QSettings, QThreadPool, Signal

from .lg_service import LgService
from .models import load_skills


class AppState(QObject):
    # signals (emitted from worker threads; auto-queued to the UI thread)
    busy_changed = Signal(bool)
    status_message = Signal(str, bool)      # (message, is_error)
    connected_changed = Signal(bool)
    skills_changed = Signal()
    active_visualization_changed = Signal(object)  # Visualization or None
    orbit_changed = Signal(bool)

    def __init__(self, asset_root: str):
        super().__init__()
        self.lg = LgService()
        self.asset_root = asset_root

        self._settings = QSettings("LiquidGalaxy", "DemoSuite")
        self.host = self._settings.value("ip", "", str)
        self.username = self._settings.value("username", "lg", str)
        self.password = self._settings.value("pass", "lg", str)
        self.port = self._settings.value("port", "22", str)
        self.screens = self._settings.value("number_of_rigs", "3", str)

        self.skills = []
        self.skills_loaded = False
        self._busy = False
        self.active_visualization = None
        self._orbiting = False

        self._pool = QThreadPool.globalInstance()

    # ------------------------------------------------------------- properties
    @property
    def busy(self):
        return self._busy

    @busy.setter
    def busy(self, value):
        self._busy = value
        self.busy_changed.emit(value)

    @property
    def orbiting(self):
        return self._orbiting

    @orbiting.setter
    def orbiting(self, value):
        self._orbiting = value
        self.orbit_changed.emit(value)
    @property
    def has_settings(self):
        return bool(self.host.strip())

    @property
    def screen_count(self):
        try:
            return int(self.screens)
        except (ValueError, TypeError):
            return 3

    @property
    def rightmost_screen(self):
        return self.screen_count // 2 + 1

    @property
    def leftmost_screen(self):
        return self.screen_count // 2 + 2

    @property
    def connected(self):
        return self.lg.is_connected

    # ------------------------------------------------------------- settings
    def save_settings(self):
        self._settings.setValue("ip", self.host)
        self._settings.setValue("username", self.username)
        self._settings.setValue("pass", self.password)
        self._settings.setValue("port", self.port)
        self._settings.setValue("number_of_rigs", self.screens)

    def load_skills(self):
        # asset_root is the bundle root (contains assets/); skills.json lives
        # at assets/skills.json, and viz asset paths are "assets/kml/...".
        path = os.path.join(self.asset_root, "assets", "skills.json")
        self.skills = load_skills(path)
        self.skills_loaded = True
        self.skills_changed.emit()

    # ------------------------------------------------------------- worker helpers
    def _run_bg(self, fn, *args):
        """Run fn(*args) on a thread-pool thread, with a busy gate."""
        if self._busy:
            return
        self.busy = True

        def task():
            try:
                fn(*args)
            finally:
                self.busy = False

        self._pool.start(task)

    def _run_ssh(self, fn, success_msg, *args):
        """Run an SSH fn(*args); connect first if needed; report status."""
        def task():
            try:
                self._ensure_connected()
                fn(*args)
                self.status_message.emit(success_msg, False)
            except Exception as e:
                self.status_message.emit(f"Failed: {self._friendly(e)}", True)

        self._run_bg(task)

    def _ensure_connected(self):
        if not self.lg.is_connected:
            self._connect_now()

    def _connect_now(self):
        self.lg.connect(
            host=self.host.strip(),
            port=int(self.port.strip()),
            username=self.username.strip(),
            password=self.password,
        )

    # ------------------------------------------------------------- actions
    def test_connection(self):
        def task():
            # 0. quick pre-flight: can we even ping the host?
            if self._ping_ok():
                pre = ""
            else:
                pre = ("Host is unreachable at the network level (no ping reply). "
                       "Its IP may have changed, or its network stack is down. ")
            try:
                self._connect_now()
                out = self.lg.test_connection()
                self.connected_changed.emit(True)
                self.status_message.emit(f"Connected: {out}", False)
                # Auto-show the logo on the leftmost screen after connecting
                # (matches the Flutter app / geosaurio-lg).
                try:
                    self.lg.show_logo(self.screen_count, self.password,
                                      self.asset_root)
                except Exception:
                    pass  # non-fatal
            except Exception as e:
                self.lg.disconnect()
                self.connected_changed.emit(False)
                self.status_message.emit(pre + self._friendly(e), True)

        self._run_bg(task)

    def _ping_ok(self):
        """Best-effort ICMP reachability check (no root needed on Linux)."""
        import subprocess
        try:
            r = subprocess.run(
                ["ping", "-c", "1", "-W", "2", self.host.strip()],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                timeout=4)
            return r.returncode == 0
        except Exception:
            return True  # assume reachable if we can't run ping

    def send_visualization(self, viz):
        def task():
            try:
                self._ensure_connected()
                # Always stop a previous or orphaned server-side orbit first.
                self.lg.stop_orbit()
                self.lg.send_visualization(
                    viz, self.screen_count, self.password, self.asset_root)
                self.active_visualization = viz
                self.active_visualization_changed.emit(viz)
                self.status_message.emit(f'"{viz.label}" is showing — orbit is ready', False)
            except Exception as e:
                self.status_message.emit(f"Failed: {self._friendly(e)}", True)
        self._run_bg(task)

    def start_orbit(self):
        viz = self.active_visualization
        if viz is None or self.orbiting or self.busy or viz.no_orbit:
            return
        def task():
            try:
                self._ensure_connected()
                self.orbiting = True
                self.lg.run_orbit_loop(viz.flyto)
                self.status_message.emit(f'Orbit completed around "{viz.label}"', False)
            except Exception as e:
                self.status_message.emit(f"Orbit failed: {self._friendly(e)}", True)
            finally:
                self.orbiting = False
        self._run_bg(task)

    def stop_orbit(self, silent=False):
        try:
            self.lg.stop_orbit()
            if not silent:
                self.status_message.emit("Orbit stopped", False)
        except Exception as e:
            if not silent:
                self.status_message.emit(f"Orbit stop failed: {self._friendly(e)}", True)
        finally:
            self.orbiting = False

    def clear_earth(self):
        def fn():
            self.lg.stop_orbit()
            self.active_visualization = None
            self.active_visualization_changed.emit(None)
            self.lg.clear_earth(self.screen_count, self.password)
        self._run_ssh(fn, "Earth cleared")

    def show_logo(self):
        self._run_ssh(
            lambda: self.lg.show_logo(self.screen_count, self.password,
                                      self.asset_root),
            "Logo shown on leftmost screen")

    def clear_logo(self):
        self._run_ssh(
            lambda: self.lg.clear_logo(self.screen_count, self.password),
            "Logo removed")

    def relaunch_rig(self):
        self._run_ssh(
            lambda: self.lg.relaunch_rig(self.screen_count, self.password),
            "Relaunch command sent")

    def reboot_rig(self):
        def fn():
            self.lg.reboot_rig(self.screen_count, self.password)
        def task():
            try:
                self._ensure_connected()
                fn()
                self.connected_changed.emit(False)
                self.status_message.emit("Reboot sent — rig is restarting", False)
            except Exception as e:
                self.status_message.emit(f"Failed: {self._friendly(e)}", True)
        self._run_bg(task)

    # ------------------------------------------------------------- utils
    def _friendly(self, e):
        s = str(e)
        low = s.lower()
        if any(k in low for k in ("timed out", "refused", "unreachable",
                                   "no route", "network is unreachable",
                                   "name or service not known")):
            return (f"cannot reach the rig at {self.host}:{self.port} — "
                    "is it powered on and on the same network?")
        if any(k in low for k in ("auth", "password", "permission denied",
                                   "bad authentication")):
            return "login failed — check username/password"
        if "service unknown" in low:
            return ("the rig rejected the command ('service unknown') — "
                    "check the SSH command and rig config")
        if "not connected" in low:
            return "not connected — open Settings and test the connection"
        return s if len(s) <= 160 else s[:160]
