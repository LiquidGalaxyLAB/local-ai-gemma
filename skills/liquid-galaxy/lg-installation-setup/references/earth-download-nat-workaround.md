# Google Earth Download Through VirtualBox NAT

The official LG install.sh downloads Google Earth Pro from:
`http://dl.google.com/dl/earth/client/current/google-earth-stable_current_amd64.deb`

## The Problem

Through VirtualBox NAT, HTTP (port 80) downloads to `dl.google.com` often stall at 0%. HTTPS downloads to the same host also stall. The symptom is `wget` hanging indefinitely with a 0-byte file. This is not a repo issue — it's specific to Google's CDN through VirtualBox's NAT engine.

Ping to 8.8.8.8 works. DNS resolves correctly. HTTPS to `archive.ubuntu.com` works at full speed (2.4 MB/s). But `dl.google.com` over both HTTP and HTTPS hangs at 0%.

## The Fix

**Download Earth on the host machine, SCP to the VM:**

```bash
# On the host (Pi/laptop) — runs instantly:
wget "https://dl.google.com/dl/earth/client/current/google-earth-stable_current_amd64.deb"

# SCP to the VM:
sshpass -p 'lg' scp google-earth-stable_current_amd64.deb lg1@192.168.1.7:/home/lg1/google-earth.deb

# On the VM:
sudo dpkg -i /home/lg1/google-earth.deb
sudo apt-get install -f -y    # fix any deps
```

**Alternative — patch the install.sh to use HTTPS and hope it works:**

The official install.sh uses `http://dl.google.com/...`. Patch it to `https://` before running:

```bash
sed -i 's|http://dl.google.com/dl/earth|https://dl.google.com/dl/earth|g' install.sh
```

This sometimes helps but not always — Google's CDN through NAT is unreliable regardless of protocol.

## Verification

```bash
dpkg -l | grep google-earth
# Expected: google-earth-pro-stable  7.3.3.7786-r0  amd64
ls -la /opt/google/earth/pro/googleearth
# Expected: regular file, ~800 bytes (wrapper script)
```
