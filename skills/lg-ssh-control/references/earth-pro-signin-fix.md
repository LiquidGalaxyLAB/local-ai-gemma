# Google Earth Pro "Cannot Contact Login Server" Dialog

## Symptom

After relaunch, Earth Pro shows a dialog:
"Google Earth can't contact the login server to activate your account."

This is cosmetic — Earth works after dismissing.

## Root Cause

Earth Pro 7.3.x validates its license by contacting Google auth endpoints at
startup. On offline VM rigs, the connections fail and Earth shows the dialog.

## Fix A: Auto-Dismiss (Most Reliable)

Use `xdotool` to send keyboard events that dismiss the dialog automatically.
This works regardless of the dialog's exact wording or which domains Earth tries.

**Prerequisites:** `xdotool` must be installed on the LG VM (usually present).

**Script:** `scripts/dismiss-earth-dialogs.py` in this skill directory.

**Install permanently via autostart:**

1. SCP the script to lg1: `sshpass -p 'lg' scp scripts/dismiss-earth-dialogs.py lg@<LG-IP>:/home/lg/`
2. Deploy the .desktop autostart entry (see `templates/dismiss-earth-dialogs.desktop`) to `/home/lg/.config/autostart/`
3. Relaunch Earth. The dialog may flash briefly but auto-dismisses within ~10s.

```bash
# Quick one-shot test:
sshpass -p 'lg' ssh -f -o StrictHostKeyChecking=no lg@<LG-IP> \
  "DISPLAY=:0 nohup python3 /home/lg/dismiss-earth-dialogs.py > /dev/null 2>&1"
```

## Fix B: DNS Blocking (Faster Failure, Dialog Still Appears)

Add auth domains to `/etc/hosts` pointing to `127.0.0.1` so Earth fails fast
instead of timing out. **Note: the dialog still appears** — this only speeds
up the failure. Combine with Fix A for a no-dialog experience.

Domains to block (from `strings /opt/google/earth/pro/libauth.so`):
- `www.googleapis.com` (OAuth2 token)
- `mapsengine.google.com`
- `earthbuilder.google.com`
- `picasaweb.google.com`
- `google.com`
- `www.google.com`
- `accounts.google.com`
- `plus.google.com`

```bash
for domain in www.googleapis.com mapsengine.google.com earthbuilder.google.com \
  picasaweb.google.com google.com www.google.com accounts.google.com plus.google.com; do
  echo "127.0.0.1 $domain" | sudo tee -a /etc/hosts
done
```

## Fix C: Give the VM Internet Access (Permanent)

On VM rigs, the "no internet" issue is usually a wrong default route.
Check with `ip route show`. The default gateway often points to `255.255.255.0`
on the internal interface instead of the LAN gateway.

```bash
# Fix (temporary, survives until reboot):
sudo route del default
sudo route add default gw 192.168.1.1 dev enp0s9
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# For permanent fix, edit /etc/network/interfaces to add
# `gateway 192.168.1.1` to the LAN interface (enp0s9).
```

**Quick test after fix:** `ping -c 2 google.com`

## Affected Domains (from libauth.so)

| Domain | Purpose |
|--------|---------|
| `www.googleapis.com` | OAuth2 token endpoint |
| `mapsengine.google.com` | Maps Engine login |
| `earthbuilder.google.com` | Earth Builder (legacy) |
| `picasaweb.google.com` | Photo service (legacy) |
| `google.com` | License association |

`kh.google.com` (tile server) is NOT affected — leave unblocked.
