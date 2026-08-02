Session learnings: Liquid Galaxy VM (lg1) network & SSH troubleshooting

Summary

- Environment in this session:
  - Hermes agent runs on a Raspberry Pi 5 (Raspberry Pi OS) on the 192.168.1.0/24 network (this device: 192.168.1.21 at time of session).
  - A Windows laptop sits on the same 192.168.1.0/24 network (192.168.1.10) and can reach both the Raspberry Pi and the Liquid Galaxy master VM (lg1).
  - Liquid Galaxy master (lg1) is on a different subnet (192.168.53.3) and was not directly reachable from the Raspberry Pi due to missing routing/forwarding.

- Key findings
  - Direct SSH/ping from the Pi to 192.168.53.3 timed out; TCP/22 was unreachable.
  - Adding a static route on the Pi ("sudo ip route add 192.168.53.0/24 via 192.168.1.10 dev wlan0") alone did not help because the Windows laptop did not forward traffic between subnets.
  - The working, low-risk workaround used in this session: a reverse SSH tunnel from the Windows laptop into the Pi that forwards LG1:22 back to the Pi on localhost:2222.

- Commands used (reference)
  - Add route on the Pi (attempted):
    sudo ip route add 192.168.53.0/24 via 192.168.1.10 dev wlan0

  - Reverse SSH tunnel (run on Windows laptop; forwards LG1:22 back to the Pi):
    ssh -N -R 2222:192.168.53.3:22 lg@192.168.1.21

  - From the Pi, verify SSH through the tunnel:
    sshpass -p 'lg' ssh -o StrictHostKeyChecking=no -p 2222 lg@localhost

- Notes & recommendations for future users
  - If the environment has an intermediate host (laptop) that can reach both subnets but does not forward, prefer a reverse SSH tunnel from that host rather than changing routing or Windows firewall settings.
  - For non-interactive automation from the Pi, ensure sshpass is installed or set up key-based auth.
  - Document the tunnel approach in the lg-ssh-control skill as a "Network Workarounds" reference so operators deploying VM-based LG rigs can reproduce it.

- Where saved
  - This file lives under the liquid-galaxy skill: ~/.hermes/profiles/liquid-galaxy-agent/skills/liquid-galaxy/references/session-learnings.md
