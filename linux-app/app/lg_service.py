"""Liquid Galaxy control service — paramiko port of the Flutter lg_service.dart.

Mirrors the LG org conventions exactly:
  - connect via paramiko SSHClient (username + password)
  - fly camera via   echo "flytoview=<LookAt>" > /tmp/query.txt
  - deploy KML via SFTP upload + sudo cp into /var/www/html/kml/
  - rightmost screen = N // 2 + 1  (balloons / text panels)
  - leftmost  screen = N // 2 + 2  (logo)
  - clear via exittour=true + blank KMLs
"""
import os

import paramiko


class LgCommandError(Exception):
    def __init__(self, message, command=""):
        self.message = message
        self.command = command
        super().__init__(message)


class LgService:
    def __init__(self):
        self._client = None
        self.base_url = "http://lg1:81"

    @property
    def is_connected(self):
        return self._client is not None

    # ------------------------------------------------------------- connection
    def connect(self, host, port, username, password, timeout=8):
        self.disconnect()
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            timeout=timeout,
            look_for_keys=False,
            allow_agent=False,
        )
        self._client = client

    def disconnect(self):
        if self._client is not None:
            try:
                self._client.close()
            except Exception:
                pass
        self._client = None

    def test_connection(self):
        out = self._exec("echo LG_OK && hostname && uname -m")
        return out

    # ------------------------------------------------------------- screen formula
    @staticmethod
    def rightmost_screen(screens):
        return 1 if screens == 1 else screens // 2 + 1

    @staticmethod
    def leftmost_screen(screens):
        return 1 if screens == 1 else screens // 2 + 2

    # ------------------------------------------------------------- primitives
    def _exec(self, command):
        if self._client is None:
            raise LgCommandError("Not connected")
        stdin, stdout, stderr = self._client.exec_command(command)
        out = stdout.read().decode("utf-8", "replace").strip()
        err = stderr.read().decode("utf-8", "replace").strip()
        code = stdout.channel.recv_exit_status()
        if code != 0 and err:
            raise LgCommandError(err, command)
        return out

    def _upload(self, remote_path, data: bytes):
        if self._client is None:
            raise LgCommandError("Not connected")
        sftp = self._client.open_sftp()
        try:
            with sftp.open(remote_path, "wb") as f:
                f.write(data)
        finally:
            sftp.close()

    def _deploy_text(self, remote_tmp, content, target, password, mkdir_target=None):
        self._upload(remote_tmp, content.encode("utf-8"))
        mkdir = ""
        if mkdir_target:
            mkdir = f"echo '{password}' | sudo -S mkdir -p {mkdir_target} && "
        cp = (f"{mkdir}echo '{password}' | sudo -S cp {remote_tmp} {target} "
              f"&& echo '{password}' | sudo -S touch {target}")
        self._exec(cp)

    def _deploy_bytes(self, remote_tmp, data, target, password, mkdir_target=None):
        self._upload(remote_tmp, data)
        mkdir = ""
        if mkdir_target:
            mkdir = f"echo '{password}' | sudo -S mkdir -p {mkdir_target} && "
        cp = (f"{mkdir}echo '{password}' | sudo -S cp {remote_tmp} {target} "
              f"&& echo '{password}' | sudo -S touch {target}")
        self._exec(cp)

    def force_refresh(self, screen_number, password):
        """Toggle the slave's refreshInterval to force a KML re-fetch."""
        try:
            self._exec(
                f"sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -t lg{screen_number} "
                f"\"echo '{password}' | sudo -S sed -i "
                f"'s|<href>##LG_PHPIFACE##kml/slave_{screen_number}.kml</href>|"
                f"<href>##LG_PHPIFACE##kml/slave_{screen_number}.kml</href>"
                f"<refreshMode>onInterval</refreshMode><refreshInterval>2</refreshInterval>|' "
                f"~/earth/kml/slave/myplaces.kml\"")
            self._exec(
                f"sshpass -p '{password}' ssh -o StrictHostKeyChecking=no -t lg{screen_number} "
                f"\"echo '{password}' | sudo -S sed -i "
                f"'s|<href>##LG_PHPIFACE##kml/slave_{screen_number}.kml</href>"
                f"<refreshMode>onInterval</refreshMode><refreshInterval>2</refreshInterval>|"
                f"<href>##LG_PHPIFACE##kml/slave_{screen_number}.kml</href>|' "
                f"~/earth/kml/slave/myplaces.kml\"")
            return True
        except Exception:
            return False

    # ------------------------------------------------------------- camera
    def fly_to(self, flyto: dict):
        lon = flyto.get("lon")
        lat = flyto.get("lat")
        range_ = flyto.get("range", 500000)
        tilt = flyto.get("tilt", 45)
        heading = flyto.get("heading", 0)
        look_at = (f"<LookAt><longitude>{lon}</longitude><latitude>{lat}</latitude>"
                   f"<range>{range_}</range><tilt>{tilt}</tilt>"
                   f"<heading>{heading}</heading>"
                   f"<altitudeMode>relativeToGround</altitudeMode></LookAt>")
        self._exec(f'echo "flytoview={look_at}" > /tmp/query.txt')

    def fly_to_smooth(self, flyto: dict, heading: float):
        lon = flyto.get("lon")
        lat = flyto.get("lat")
        range_ = flyto.get("range", 500000)
        tilt = flyto.get("tilt", 45)
        look_at = (f"<gx:duration>0.3</gx:duration><gx:flyToMode>smooth</gx:flyToMode>"
                   f"<LookAt><longitude>{lon}</longitude><latitude>{lat}</latitude>"
                   f"<range>{range_}</range><tilt>{tilt}</tilt>"
                   f"<heading>{heading}</heading>"
                   f"<altitudeMode>relativeToGround</altitudeMode></LookAt>")
        self._exec(f'echo "flytoview={look_at}" > /tmp/query.txt')

    # ------------------------------------------------------------- deploy
    def send_visualization(self, viz, screens, password, asset_root):
        """Deploy one pre-baked visualization: fly-to -> master KML ->
        rightmost panel PNG + ScreenOverlay KML -> optional tour."""
        self.fly_to(viz.flyto)

        # 1. master Earth KML (local asset file -> remote)
        master_path = os.path.join(asset_root, viz.master_kml)
        with open(master_path, "rb") as f:
            self._deploy_bytes(
                "/home/lg/app_master.kml", f.read(),
                "/var/www/html/kml/master.kml", password)

        # 2. rightmost panel PNG + its ScreenOverlay KML
        rightmost = self.rightmost_screen(screens)
        png_dir = f"/var/www/html/kml/{viz.skill_id}"
        with open(os.path.join(asset_root, viz.panel_png), "rb") as f:
            self._deploy_bytes(
                "/home/lg/app_panel.png", f.read(),
                f"{png_dir}/{viz.panel_png_filename}", password,
                mkdir_target=png_dir)
        with open(os.path.join(asset_root, viz.panel_kml), "rb") as f:
            self._deploy_bytes(
                "/home/lg/app_panel.kml", f.read(),
                f"/var/www/html/kml/slave_{rightmost}.kml", password)

        # 3. force-refresh the rightmost slave
        self.force_refresh(rightmost, password)

        # 4. optional tour
        if viz.tour:
            self._exec(f'echo "playtour={viz.tour}" > /tmp/query.txt')

    # ------------------------------------------------------------- utilities
    def clear_earth(self, screens, password):
        self._exec('echo "exittour=true" > /tmp/query.txt')
        blank = ('<?xml version="1.0" encoding="UTF-8"?>'
                 '<kml xmlns="http://www.opengis.net/kml/2.2">'
                 '<Document><name>Blank</name></Document></kml>')
        self._upload("/home/lg/app_blank.kml", blank.encode("utf-8"))
        parts = [
            f"echo '{password}' | sudo -S cp /home/lg/app_blank.kml "
            f"/var/www/html/kml/master.kml"
        ]
        leftmost = self.leftmost_screen(screens)
        # Clear every slave EXCEPT the leftmost (logo) screen, so "Clear Earth"
        # doesn't wipe the logo.
        for i in range(1, screens + 1):
            if i == leftmost:
                continue
            parts.append(f"echo '{password}' | sudo -S cp /home/lg/app_blank.kml "
                         f"/var/www/html/kml/slave_{i}.kml")
        self._exec(" && ".join(parts))

    def show_logo(self, screens, password, asset_root=None):
        """Upload final_logo.png + place a 554x500 bottom-left ScreenOverlay
        on the leftmost screen only."""
        leftmost = self.leftmost_screen(screens)

        # 1. upload the image via SFTP (never assume it pre-exists on the rig)
        if asset_root:
            logo_path = os.path.join(asset_root, "assets", "images", "final_logo.png")
            if os.path.exists(logo_path):
                with open(logo_path, "rb") as f:
                    self._deploy_bytes(
                        "/home/lg/final_logo.png", f.read(),
                        "/var/www/html/kml/final_logo.png", password)

        # 2. overlay KML — pixel-exact 554x500, bottom-left anchored
        href = f"{self.base_url}/kml/final_logo.png"
        logo = ('<?xml version="1.0" encoding="UTF-8"?>'
                '<kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>Logo</name>'
                '<ScreenOverlay><name>Logo</name><Icon>'
                f'<href>{href}</href></Icon>'
                '<overlayXY x="0" y="1" xunits="fraction" yunits="fraction"/>'
                '<screenXY x="0.02" y="0.98" xunits="fraction" yunits="fraction"/>'
                '<rotationXY x="0" y="0" xunits="fraction" yunits="fraction"/>'
                '<size x="554" y="500" xunits="pixels" yunits="pixels"/>'
                '</ScreenOverlay></Document></kml>')
        self._upload("/home/lg/app_logo.kml", logo.encode("utf-8"))
        self._exec(f"echo '{password}' | sudo -S cp /home/lg/app_logo.kml "
                   f"/var/www/html/kml/slave_{leftmost}.kml")
        self.force_refresh(leftmost, password)

    def clear_logo(self, screens, password):
        leftmost = self.leftmost_screen(screens)
        blank = ('<?xml version="1.0" encoding="UTF-8"?>'
                 '<kml xmlns="http://www.opengis.net/kml/2.2">'
                 '<Document><name>Empty Logo</name></Document></kml>')
        self._upload("/home/lg/app_logo_blank.kml", blank.encode("utf-8"))
        self._exec(f"echo '{password}' | sudo -S cp /home/lg/app_logo_blank.kml "
                   f"/var/www/html/kml/slave_{leftmost}.kml")
        self.force_refresh(leftmost, password)

    # ------------------------------------------------------------- advanced
    def reboot_rig(self, screens, password):
        for i in range(screens, 0, -1):
            self._exec(f"sshpass -p '{password}' ssh -o StrictHostKeyChecking=no "
                       f"-t lg{i} \"echo '{password}' | sudo -S reboot\"")

    def relaunch_rig(self, screens, password):
        for i in range(screens, 0, -1):
            self._exec(f"sshpass -p '{password}' ssh -o StrictHostKeyChecking=no "
                       f"-t lg{i} \"echo '{password}' | sudo -S service lightdm restart\"")
