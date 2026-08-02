# LG Command Channel: /tmp/query.txt

The Liquid Galaxy rig has a background monitoring process that watches
`/tmp/query.txt`. Writing commands to this file triggers real-time camera
and tour actions on all screens.

## Supported Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `flytoview=<LookAt>` | Fly camera to location | `flytoview=<gx:duration>0.3</gx:duration><gx:flyToMode>smooth</gx:flyToMode><LookAt>...` |
| `exittour=true` | Exit any active tour | `exittour=true` |
| `playtour=<name>` | Play a named tour | `playtour=Orbit` |
| (empty) | Clear / stop | `echo "" > /tmp/query.txt` |

## File Lifecycle

1. Script writes command to `/tmp/query.txt`
2. LG monitoring process detects the file, reads the command
3. Executes the command (flies camera, exits tour, etc.)
4. Deletes `/tmp/query.txt` (file is consumed)
5. Next command: file doesn't exist → write it again

**Verification:** After writing, check `cat /tmp/query.txt`. If "No such file
or directory", the command was consumed (success). If the content is still
there, the monitor hasn't picked it up yet (wait and retry).

## Smooth FlyTo Format (Required for Non-Jumpy Motion)

Without `gx:duration` and `gx:flyToMode`, Earth uses default transitions
which appear jumpy and bouncy. The exact format from the La Palma app:

```
flytoview=<gx:duration>0.3</gx:duration><gx:flyToMode>smooth</gx:flyToMode>
<LookAt>
  <longitude>...</longitude>
  <latitude>...</latitude>
  <range>...</range>
  <tilt>...</tilt>
  <heading>...</heading>
  <altitudeMode>relativeToGround</altitudeMode>
</LookAt>
```

Parameters:
- `gx:duration` — 0.3 seconds (short smooth transition between orbit steps)
- `gx:flyToMode` — `smooth` (not `bounce`)
- `heading` — 0 to 360 (bearing from target)

## exittour=true Lifecycle

Send `exittour=true` at three points:
1. **Before starting orbit** — clears any stuck tour from prior session
2. **After orbit completes** — returns Earth to normal navigation mode
3. **On error/stop** — ensures clean state regardless of failure

## Using from Python (on lg1)

```python
def query(cmd):
    with open("/tmp/query.txt", "w") as f:
        f.write(cmd)

# Start fresh
query('exittour=true')
time.sleep(0.1)

# Fly to location
query('flytoview=<gx:duration>0.3</gx:duration><gx:flyToMode>smooth</gx:flyToMode><LookAt>...</LookAt>')
```

## Using from SSH (from Pi)

```bash
sshpass -p 'lg' ssh lg@<LG-IP> \
  'echo "flytoview=<gx:duration>0.3</gx:duration><gx:flyToMode>smooth</gx:flyToMode><LookAt><longitude>2.2945</longitude><latitude>48.8584</latitude><range>3000</range><tilt>60</tilt><heading>0</heading><gx:altitudeMode>relativeToGround</gx:altitudeMode></LookAt>" > /tmp/query.txt'
```

## Source

This mechanism was discovered in the La Palma Volcano Eruption Tracking Tool
(source: `lib/codingapp/kml/flyto.dart`, usage across `Map_Tab.dart`,
`Track_Tab.dart`, `Info.dart`, `custom_builder.dart`). The app writes commands
via SSH over the same connection used for KML deployment.
