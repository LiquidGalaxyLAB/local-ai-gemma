# Voice/Audio on Raspberry Pi — Hermes TTS Setup

## What It Is

Hermes agent can speak responses aloud using Text-to-Speech (TTS). On the Raspberry Pi, this runs through **Edge TTS** (free, no API key) and plays audio through **PipeWire** to Bluetooth headphones.

## How It Works

```
Hermes Agent → text_to_speech() tool → Edge TTS → MP3 → pw-play → PipeWire → Bluetooth headphones → Rockerz 550
```

1. Agent calls `text_to_speech(text)` — generates an MP3 via Microsoft Edge's free TTS API
2. MP3 saved to `~/.hermes/profiles/liquid-galaxy-agent/audio_cache/`
3. `pw-play` (PipeWire's native player) plays the MP3 through the default audio sink
4. Audio routes through PipeWire → Bluetooth to the Rockerz 550 headphones

## How to Implement

### Prerequisites

```bash
# PipeWire (already running on Pi OS)
sudo apt-get install pipewire pipewire-pulse wireplumber

# TTS dependency
pip install edge-tts
```

### Bluetooth Headset Pairing

```bash
bluetoothctl scan on       # Find device
bluetoothctl pair <MAC>    # Pair
bluetoothctl trust <MAC>   # Trust for auto-connect
bluetoothctl connect <MAC> # Connect (negotiates HSP/HFP for mic)

# Verify audio sink
wpctl status | grep -i bluez
# Expected: Rockerz 550 as default sink
```

### Playback

```bash
# Kill any lingering audio first
pkill -f pw-play 2>/dev/null

# Play the TTS file
pw-play /path/to/file.mp3
```

### Config

In `config.yaml`:
```yaml
tts:
  provider: edge  # free, no API key
```

### Critical Rule: Avoid Audio Overlap

Old audio keeps playing if a new command comes in. Always kill previous playback before new TTS:

```bash
pkill -f pw-play 2>/dev/null
```

---

## Midterm Reference

- **Definition:** Agent-driven Text-to-Speech for kiosk-style voice output on Liquid Galaxy
- **Platform:** Raspberry Pi 5, PipeWire audio, Rockerz 550 Bluetooth headphones
- **Provider:** Edge TTS (free, Microsoft, no API key needed)
- **Player:** `pw-play` (PipeWire native CLI player)
- **Key constraint:** Kill old playback before new TTS to prevent audio pile-up
