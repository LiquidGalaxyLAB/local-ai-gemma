import subprocess, sys, time, os

ip = sys.argv[1]
user = sys.argv[2]
pw = 'lg'

# Fix autostart
desktop = '[Desktop Entry]\nName=LG\nExec=env DISPLAY=:0 LIBGL_ALWAYS_SOFTWARE=1 QT_XCB_GL_INTEGRATION=none /opt/google/earth/pro/googleearth --no_system_check --no_signin\nType=Application\n'
with open('/tmp/lg_d.desktop', 'w') as f:
    f.write(desktop)

subprocess.run(['sudo', '-S', 'cp', '/tmp/lg_d.desktop', '/home/' + user + '/.config/autostart/lg.desktop'], input=(pw + '\n').encode())
print(ip + ' ' + user + ' autostart fixed')

# Kill Earth
subprocess.run(['sudo', '-S', 'killall', '-9', 'googleearth-bin', 'googleearth'], input=(pw + '\n').encode(), stderr=subprocess.DEVNULL)
time.sleep(2)

# Merge X authority
subprocess.run(['sudo', '-S', 'xauth', '-f', '/home/' + user + '/.Xauthority', 'extract', '/tmp/xc', user + '/unix:0'], input=(pw + '\n').encode(), stderr=subprocess.DEVNULL)
subprocess.run(['sudo', '-S', 'chmod', '644', '/tmp/xc'], input=(pw + '\n').encode(), stderr=subprocess.DEVNULL)
subprocess.run(['xauth', 'merge', '/tmp/xc'], stderr=subprocess.DEVNULL)

# Start Earth
subprocess.run(['sudo', '-S', 'rm', '-f', '/home/' + user + '/.googleearth/instance-running-lock'], input=(pw + '\n').encode(), stderr=subprocess.DEVNULL)
with open('/tmp/run_e.sh', 'w') as f:
    f.write('XAUTHORITY=/home/' + user + '/.Xauthority DISPLAY=:0 LIBGL_ALWAYS_SOFTWARE=1 QT_XCB_GL_INTEGRATION=none nohup /opt/google/earth/pro/googleearth --no_system_check --no_signin > /dev/null 2>&1 &\n')
subprocess.run(['chmod', '+x', '/tmp/run_e.sh'])
subprocess.Popen(['script', '-q', '-c', '/bin/su - ' + user + ' -c "/tmp/run_e.sh"', '/dev/null'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(ip + ' ' + user + ' Earth restarted')
