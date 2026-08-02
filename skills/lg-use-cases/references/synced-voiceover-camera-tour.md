# Synced Voiceover + Camera Tour Pattern

This pattern applies to ANY data tour on the LG — geography education, armed conflicts, maritime domain awareness, historical events, etc.

## Core Sequence

```
1. Generate all KML content (features, styles, labels)
2. Deploy KML to Apache (sudo cp to master.kml)
3. Wait 8 seconds for Earth's 3s NetworkLink refresh + cache update
4. Deploy initial right-screen text panel
5. Generate TTS narration for the whole tour
6. For each stop in the tour:
   a. Fly camera to location (flytoview via /tmp/query.txt)
   b. Update right-screen text panel (deploy new PNG)
   c. Play zone-specific TTS (2-4 sentences)
   d. Dwell 10-12 seconds
7. Final wide overview (20,000km range, 0 tilt)
```

## Timing Parameters

| Step | Duration | Notes |
|------|----------|-------|
| KML deploy + wait | 8s | Allows NetworkLink refresh + cache bust |
| Fly to location | 1s | /tmp/query.txt consumed by Earth daemon |
| Text panel update | 2s | SCP + sudo cp to Apache |
| TTS playback + dwell | 10-12s | Voiceover 2-4 sentences |
| Total per zone | ~15s | |

## Camera Parameters

```python
def fly_to(lon, lat, rng=600000, tilt=55):
    f = '<LookAt><longitude>' + str(lon) + '</longitude><latitude>' + str(lat) \
        + '</latitude><range>' + str(rng) + '</range><tilt>' + str(tilt) \
        + '</tilt><heading>0</heading><altitudeMode>relativeToGround</altitudeMode></LookAt>'
    cmd = 'rm -f /tmp/query.txt && echo "flytoview=' + f + '" > /tmp/query.txt'
    subprocess.run(['sshpass', '-p', LG_PASS, 'ssh', '-o', 'StrictHostKeyChecking=no', 'lg@' + LG_IP, cmd])
```

## Right-Screen Text Panel Deployment

```python
def deploy_panel(path):
    subprocess.run(['sshpass', '-p', LG_PASS, 'scp', '-o', 'StrictHostKeyChecking=no',
        path, 'lg@' + LG_IP + ':/home/lg/panel.png'])
    subprocess.run(['sshpass', '-p', LG_PASS, 'ssh', '-o', 'StrictHostKeyChecking=no',
        'lg@' + LG_IP,
        'echo ' + LG_PASS + ' | sudo -S cp /home/lg/panel.png /var/www/html/kml/right_panel.png 2>/dev/null'])
```

## Text Panel Content Per Stop

| Element | Purpose |
|---------|---------|
| Zone/stop name | Large text at top |
| 2-4 line description | Wrapped body text |
| Intensity/importance bar | 5-block indicator |
| Coordinates | Lat/Lon reference |
| Status indicator | Colored dot + status text |

## Use Cases This Pattern Applies To

- Armed Conflicts (10 zones × 12s = 2 min tour)
- Geography Education (Date Line, Monsoon, Turkey EQ)
- Maritime Domain Awareness (chokepoint flythrough)
- History Education (timeline flythrough)
- Supply Chain (trade route animation)
