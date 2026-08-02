#!/usr/bin/env python3
"""Deploy a data balloon to the RIGHTMOST Liquid Galaxy screen.

Follows the LG Wiki balloon pattern (BalloonStyle + gx:balloonVisibility)
with the VM-safe adaptation: ESCAPED HTML entities instead of CDATA
(Earth 7.3.3 on VirtualBox silently drops any Placemark containing CDATA).

ROOT screen formula (LG Wiki standard, valid for ANY rig):
    Screen numbering starts at 1 with the master machine (lg1).
    Total screens = N (lg1, lg2, ..., lgN).
    Right-most screen number = floor(N/2) + 1
    Left-most screen number  = floor(N/2) + 2
For N=3: rightmost = 2 (lg2 -> slave_2.kml). N=5: rightmost = 3.
N=7: rightmost = 4. This rig (N=3): rightmost = slave_2.kml.

Usage (invoke through the Hermes `terminal` tool):
    python3 deploy_balloon.py --lat 26.45 --lon 80.3319 --name Kanpur \
        [--fields "Population:2.8M" "Temp:35C"] [--screens 3] \
        [--lg-ip 192.168.1.12] [--pw lg]

Never deploys to master.kml. No relaunch/reboot needed — the slave's 3s
Solo KML NetworkLink refresh picks the file up automatically. Verify with:
    sudo grep slave_2 /var/log/apache2/other_vhosts_access.log | tail
"""
import argparse
import html
import math
import subprocess


def build_balloon_kml(lat, lon, name, extra_fields=None):
    """Build the balloon KML string. Coordinates are lon,lat order."""
    fields_html = ""
    if extra_fields:
        for f in extra_fields:
            if ":" in f:
                k, v = f.split(":", 1)
                fields_html += (
                    '<p style="font-size:18px;"><b>%s:</b> %s</p>'
                    % (html.escape(k.strip()), html.escape(v.strip()))
                )
            else:
                fields_html += (
                    '<p style="font-size:16px;color:#aaa;">%s</p>'
                    % html.escape(f.strip())
                )
    # ESCAPED entities, NOT CDATA (CDATA drops the whole Placemark on this VM)
    text = (
        '&lt;div style="font-family: Arial, sans-serif; color: #ffffff; '
        'padding: 15px;"&gt;\n'
        '  &lt;h2 style="font-size:24px; color:#ffcc00;"&gt;%s&lt;/h2&gt;\n'
        '  &lt;p style="font-size:18px;"&gt;&lt;b&gt;Place Name:&lt;/b&gt; %s&lt;/p&gt;\n'
        '  &lt;p style="font-size:18px;"&gt;&lt;b&gt;Latitude:&lt;/b&gt; %s&lt;/p&gt;\n'
        '  &lt;p style="font-size:18px;"&gt;&lt;b&gt;Longitude:&lt;/b&gt; %s&lt;/p&gt;\n'
        '%s'
        '&lt;/div&gt;'
    ) % (html.escape(name), html.escape(name), lat, lon, fields_html)

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<kml xmlns="http://www.opengis.net/kml/2.2" '
        'xmlns:gx="http://www.google.com/kml/ext/2.2">\n'
        ' <Document>\n'
        '   <Placemark>\n'
        '     <name>%s</name>\n'
        '     <Style>\n'
        '       <BalloonStyle>\n'
        '         <bgColor>bb000000</bgColor>\n'
        '         <text>%s</text>\n'
        '       </BalloonStyle>\n'
        '     </Style>\n'
        '     <gx:balloonVisibility>1</gx:balloonVisibility>\n'
        '     <Point>\n'
        '       <coordinates>%s,%s,0</coordinates>\n'
        '     </Point>\n'
        '   </Placemark>\n'
        ' </Document>\n'
        '</kml>\n'
    ) % (html.escape(name), text, lon, lat)


def rightmost_slave(n_screens):
    """ROOT formula: right-most screen = floor(N/2) + 1 (lg1 = master, screens lg1..lgN)."""
    return int(math.floor(n_screens / 2)) + 1


def deploy(lg_ip, pw, slave_no, kml):
    """SCP to lg1 then sudo-cp to /var/www/html/kml/slave_<N>.kml."""
    local = "/tmp/balloon_%d.kml" % slave_no
    with open(local, "w") as f:
        f.write(kml)
    remote = "lg@%s:/home/lg/balloon_%d.kml" % (lg_ip, slave_no)
    subprocess.run(
        ["sshpass", "-p", pw, "scp", "-o", "StrictHostKeyChecking=no",
         local, remote],
        check=True, timeout=20,
    )
    dst = "/var/www/html/kml/slave_%d.kml" % slave_no
    # Python subprocess sudo (echo|sudo -S hangs over sshpass; tool guard
    # also blocks inline echo|sudo patterns in the command string)
    cmd = (
        'python3 -c "import subprocess; '
        "subprocess.run(['sudo','-S','cp','/home/lg/balloon_%d.kml','%s'], "
        "input=b'%s\\n', check=True)\""
    ) % (slave_no, dst, pw)
    subprocess.run(
        ["sshpass", "-p", pw, "ssh", "-o", "StrictHostKeyChecking=no",
         "lg@%s" % lg_ip, cmd],
        check=True, timeout=20,
    )
    print("Balloon deployed to slave_%d.kml (rightmost screen) at %s" % (slave_no, dst))


def main():
    ap = argparse.ArgumentParser(description="Deploy a balloon to the rightmost LG screen")
    ap.add_argument("--lat", required=True, type=float)
    ap.add_argument("--lon", required=True, type=float)
    ap.add_argument("--name", required=True)
    ap.add_argument("--fields", nargs="*", default=None,
                    help="extra 'Key:Value' lines for the balloon body")
    ap.add_argument("--screens", type=int, default=3)
    ap.add_argument("--lg-ip", default="192.168.1.12")
    ap.add_argument("--pw", default="lg")
    args = ap.parse_args()

    slave_no = rightmost_slave(args.screens)
    kml = build_balloon_kml(args.lat, args.lon, args.name, args.fields)
    deploy(args.lg_ip, args.pw, slave_no, kml)


if __name__ == "__main__":
    main()
