#!/usr/bin/env python3
"""Restart Earth on a slave VM with --no_system_check, X authority sync, and QT_XCB_GL_INTEGRATION=none."""
import subprocess, time, sys, os

ip = sys.argv[1]
user = sys.argv[2]
pw = 'lg'

subprocess.run(['sudo', '-S', 'killall', '-9', 'googleearth-bin', 'googleearth'], input=(pw + '\n').encode(), stderr=subprocess.DEVNULL)
time.sleep(2)
subprocess.run(['sudo', '-S', 'xauth', '-f', '/home/' + user + '/.Xauthority', 'extract', '/tmp/xc', user + '/unix:0'], input=(pw + '\n').encode(), stderr=subprocess.DEVNULL)
subprocess.run(['sudo', '-S', 'chmod', '644', '/tmp/xc'], input=(pw + '\n').encode(), stderr=subprocess.DEVNULL)
subprocess.run(['xauth', 'merge', '/tmp/xc'], stderr=subprocess.DEVNULL)
subprocess.run(['sudo', '-S', 'rm', '-f', '/home/' + user + '/.googleearth/instance-running-lock'], input=(pw + '\n').encode(), stderr=subprocess.DEVNULL)
with open('/tmp/run_e.sh', 'w') as f:
    f.write('XAUTHORITY=/home/' + user + '/.Xauthority DISPLAY=:0 LIBGL_ALWAYS_SOFTWARE=1 QT_XCB_GL_INTEGRATION=none nohup /opt/google/earth/pro/googleearth --no_system_check --no_signin > /dev/null 2>&1 &\n')
subprocess.run(['chmod', '+x', '/tmp/run_e.sh'])
subprocess.Popen(['script', '-q', '-c', '/bin/su - ' + user + ' -c "/tmp/run_e.sh"', '/dev/null'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(ip + ' ' + user + ' Earth restarted')
