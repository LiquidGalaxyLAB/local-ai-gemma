# ARM LG Deployment Analysis

This reference documents the feasibility and approaches for running a Liquid Galaxy-like setup on ARM hardware (specifically Raspberry Pi 5), based on hands-on investigation conducted July 2026.

## Quick Reference

| Approach | Performance | Multi-screen | ViewSync | Earth native | KML | Effort |
|----------|------------|--------------|----------|-------------|-----|--------|
| 3× QEMU x86_64 VMs | Impossible (<1 FPS) | Yes (3 VMs) | Yes | Yes | Yes | Very high |
| 1× QEMU x86_64 VM | Poor (slideshow) | No | No | Yes | Yes | High |
| Box64 + Earth | Good (est.) | 2× HDMI | No | Translated | Yes | Medium |
| CesiumJS web globe | Excellent | 2× browser | Pseudo-sync | No | Import | Low |
| Marble (KDE) | Excellent | Via WM | No | Yes | Low |
| **Hybrid: KVM aarch64 VM + Box64** | Good if Earth runs via box64 | Yes (3 VMs) | Yes | Via box64 | Yes | Very high |

## Hardware Under Test

| Component | Specification |
|-----------|---------------|
| Board | Raspberry Pi 5 Model B Rev 1.1 |
| CPU | 4× Cortex-A76 @ 2.4 GHz (max), 1.5 GHz (min) |
| RAM | 8 GB LPDDR4X |
| Storage | 469 GB NVMe (432 GB available) |
| GPU | VideoCore VII (V3D 7.1.4) via Mesa, 2× render nodes (/dev/dri/renderD128) |
| Display | Wayland (wayland-0), 2× HDMI (HDMI-A-1, HDMI-A-2) |
| Networking | GbE + WiFi, dual-band |
| KVM | Confirmed available at /dev/kvm — for ARM guests only, NOT for x86 |
| OS | Debian 13 (trixie/sid) aarch64 |
| Hermes Profile | liquid-galaxy-agent |

## QEMU Packages Available (Debian ARM)

All installed by default on this rig:

| Package | Purpose |
|---------|---------|
| `qemu-system-x86` | x86/x86_64 system emulator binaries |
| `qemu-system-arm` | ARM system emulator binaries |
| `qemu-utils` | qemu-img, qemu-nbd, etc. |
| `qemu-user` | User-mode emulation for running individual x86 binaries |
| `qemu-user-binfmt` | binfmt registration for transparent x86 binary execution |
| `box64` | Dynamic recompiler: runs amd64 binaries on arm64 (~85% native speed) |

## QEMU x86_64 Emulation

On ARM, `qemu-system-x86_64` runs in **TCG (Tiny Code Generator)** mode — full software emulation. No hardware acceleration for x86 guests on ARM.

### Expected Performance

| Metric | Expectation |
|--------|-------------|
| CPU throughput | ~5-10% of native x86_64 single-core |
| Boot time (Ubuntu 16.04) | 5-8 minutes |
| SSH responsiveness | Usable (200-500ms latency) |
| Google Earth GUI | <1 FPS, software OpenGL (llvmpipe) |
| 3 simultaneous VMs | Not usable (4 cores ÷ 3 guests) |
| GPU acceleration | None — no passthrough from Pi GPU |

**Why it's impractical:** Google Earth is a 3D OpenGL app. QEMU on ARM emulates the x86 CPU AND the GPU in software. Result: 0.1-1 FPS. Even one VM is barely usable; 3 is impossible.

## Box64 Approach

Box64 dynamically recompiles x86_64 instructions to ARM64 — NOT a VM, translates individual binaries.

| Metric | Expectation |
|--------|-------------|
| CPU throughput | ~60-85% of native (DynaRec) |
| OpenGL | Forwarded to native VideoCore/Mesa |
| Single-instance Earth | Potentially usable at modest FPS |
| Multiple instances | One per HDMI output (Pi 5 has 2) |
| ViewSync | Not available (single process) |

**Caveats:** Untested on Pi 5. May crash on missing x86 libs, DRM checks, or complex OpenGL. Font rendering often breaks under translation.

## Web-Based Globe Alternative

Since Earth isn't viable on ARM, a web-based globe is the best practical option:

| Platform | ARM native | KML | Multi-screen | Performance |
|----------|-----------|-----|--------------|-------------|
| CesiumJS | Yes | Yes (import) | Browser windows | Excellent |
| OpenWebGlobe | Yes | Partial | Browser windows | Good |
| Mapbox GL JS | Yes | Limited | Browser windows | Excellent |
| Marble (KDE) | Yes (native) | Yes | Wayland multi-monitor | Good |

**LG-like workflow with CesiumJS on Pi 5:**
1. Chromium loads CesiumJS with KML from local Apache
2. Dual HDMI → two windows with offset camera views
3. Camera via WebSocket Python daemon (replaces /tmp/query.txt)
4. KML layers from `lg-data-visualization` work unchanged
5. No ViewSync, but synchronized camera via shared state

This is not standard LG but reuses the entire data pipeline.

## Summary

| Approach | Works? | Performance | Standard LG? | Best for |
|----------|--------|------------|--------------|----------|
| 3× QEMU x86_64 VMs | Possible | Terrible | Yes (topology) | No one |
| 1× QEMU x86_64 VM | Possible | Poor | Partial (1 screen) | Dev testing |
| Box64 + Earth | Untested | Good (est.) | No (1 process) | Single-screen LG-ish |
| **Hybrid: KVM aarch64 VMs + Box64** | **Hypothetical** | **Good (est.)** | **Yes (3 VMs)** | **Experimental ARM LG** |
| Web globe (CesiumJS) | Works now | Excellent | No | Best ARM option |

## Hybrid Approach: KVM aarch64 VMs + Box64

This approach uses the Pi 5's KVM hardware virtualization to run fast native ARM VMs, then uses box64 inside each VM to translate Google Earth Pro x86 → ARM. It maintains the full LG 3-VM topology.

Concept:
1. Create 3 KVM-accelerated aarch64 VMs (lg1, lg2, lg3) — native ARM speed
2. Each VM runs Ubuntu ARM (22.04 LTS or Debian ARM)
3. Install box64 inside each VM (`apt install box64`)
4. Install Google Earth Pro x86_64 .deb manually via dpkg-deb extract + box64
5. Configure Apache/PHP/ViewSync per standard LG
6. LG control scripts adapted for the aarch64 environment

Pros:
- 3-VM topology preserved (real LG setup)
- Native VM speed (KVM-accelerated)
- ViewSync works over UDP between VMs
- All Pi 5 resources usable (dual HDMI, GPU)

Cons:
- Untested — Google Earth Pro's OpenGL rendering may have issues under box64
- The official install.sh won't work (targets x86 Ubuntu 16.04)
- All LG scripts need manual adaptation
- Complex setup — no automated install path exists

### Box64 Earth Test Command

```bash
# Extract Earth .deb (can't dpkg -i on ARM)
wget http://dl.google.com/dl/earth/client/current/google-earth-stable_current_amd64.deb
dpkg-deb -x google-earth-stable_current_amd64.deb /tmp/google-earth
# Run via box64
box64 /tmp/google-earth/opt/google/earth/pro/googleearth
```

Expected: Earth GUI launches with software OpenGL rendering. FPS depends on the Pi's Mesa/VideoCore GL driver under box64 translation. See also: https://github.com/ptitSeb/box64

## References

- Box64: https://github.com/ptitSeb/box64
- CesiumJS: https://cesium.com/platform/cesiumjs/
- LG Wiki: https://lg-wiki-coral.vercel.app/
- QEMU ARM docs: https://www.qemu.org/docs/master/system/target-arm.html