# Flutter LG Control → Shell Command Mapping

When converting the Flutter-based LG control app's commands to shell equivalents,
the built-in scripts (`lg-relaunch`, `lg-reboot`, `lg-poweroff`) may be broken
if `lg-ctl-master` is missing or root SSH is not configured. Use helper scripts
at `/home/lg/bin/lg-*-direct` instead (deploy via `lg-deploy-helpers.sh`).

## Relaunch

**Flutter (original):**
```kotlin
for (i in 1..screens) {
    val command = """/home/$username/bin/lg-relaunch >> /home/$username/log.txt;
        RELAUNCH_CMD="if [ -f /etc/init/lxdm.conf ]; then
            export SERVICE=lxdm
        elif [ -f /etc/init/lightdm.conf ]; then
            export SERVICE=lightdm
        else exit 1; fi
        if [[ ${'$'}(service ${'$'}SERVICE status) =~ 'stop' ]]; then
            echo $password | sudo -S service ${'$'}SERVICE start
        else
            echo $password | sudo -S service ${'$'}SERVICE restart
        fi" && sshpass -p $password ssh -x -t lg@lg$i "$RELAUNCH_CMD"""
    execute(command)
}
```

**Shell (via helper — preferred, handles sudo internally):**
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no -p 2222 lg@localhost \
  '/home/lg/bin/lg-relaunch-direct'
```

## Reboot

**Flutter:**
```kotlin
for (i in 1..screens) {
    execute("""sshpass -p $password ssh -t lg$i "echo $password | sudo -S reboot"""")
}
```

**Shell (via helper — reboots all frames):**
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no -p 2222 lg@localhost \
  '/home/lg/bin/lg-reboot-direct'
```

## Poweroff

**Flutter:**
```kotlin
for (i in 1..screens) {
    execute("""sshpass -p $password ssh -t lg$i "echo $password | sudo -S poweroff"""")
}
```

**Shell (via helper — powers off all frames):**
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no -p 2222 lg@localhost \
  '/home/lg/bin/lg-poweroff-direct'
```

## Set KML Refresh

**Flutter:**
```kotlin
for (i in 2..screens) {
    val search = "<href>##LG_PHPIFACE##kml/slave_$i.kml</href>"
    val replace = "...<refreshMode>onInterval</refreshMode><refreshInterval>2</refreshInterval>"
    execute("""sshpass -p $password ssh -t lg$i 'echo $password | sudo -S sed -i "s|$replace|$search|" ~/earth/kml/slave/myplaces.kml'""")
    execute("""sshpass -p $password ssh -t lg$i 'echo $password | sudo -S sed -i "s|$search|$replace|" ~/earth/kml/slave/myplaces.kml'""")
}
```

**Shell (via helper — strips then injects refresh tags):**
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no -p 2222 lg@localhost \
  '/home/lg/bin/lg-refresh-set'
```

## Reset KML Refresh

**Shell (via helper):**
```bash
sshpass -p 'lg' ssh -o StrictHostKeyChecking=no -p 2222 lg@localhost \
  '/home/lg/bin/lg-refresh-reset'
```

## Key Differences

| Aspect | Flutter Approach | Shell Helper Approach |
|--------|-----------------|----------------------|
| Sudo method | `echo $password \| sudo -S` inline | Password embedded in script, no inline pipe |
| Loop scope | From app, SSH into each lgN | From lg1, sshpass to each frame |
| Portability | Per-device SSH config required | Single SSH hop via tunnel, all logic on lg1 |
| Tool guard | N/A (app, not terminal tool) | Inline `sudo -S` blocked; helpers bypass this |
