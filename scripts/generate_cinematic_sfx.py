#!/usr/bin/env python3
"""
OmniPress Cinematic SFX Generator — Multi-Layered Sound Design for Channel Intro.
Synthesizes professional, broadcast-quality stereo audio (48kHz 16-bit PCM) timed precisely
to the Remotion ChannelIntro composition (90 frames at 30 fps = 3.0 seconds).

Layers:
1. Analog Tape Hiss & Vinyl Warmth (0.0s - 3.0s)
2. Military Cipher / Typewriter Decoding Bursts (0.2s - 0.9s, frames 6-28)
3. Heavy Classified Stamp Slam & Transient Snap (at 0.60s, frame 18 - sync with camera shake)
4. Cinematic Sub-Bass Boom / Braam (0.60s - 2.8s)
5. Golden Anamorphic Flare Shimmer Whoosh (0.75s - 1.6s, frames 22-48)
"""

import math
import struct
import wave
import random
from pathlib import Path

SAMPLE_RATE = 48000  # Broadcast standard 48 kHz
DURATION = 4.0       # 4.0 seconds (120 frames @ 30fps)
TOTAL_SAMPLES = int(SAMPLE_RATE * DURATION)


def clamp(val, min_val=-1.0, max_val=1.0):
    return max(min_val, min(max_val, val))


def generate_intro_sfx(output_wav_path: Path):
    output_wav_path.parent.mkdir(parents=True, exist_ok=True)
    random.seed(42)  # Deterministic synthesis

    # Stereo buffers
    left_channel = [0.0] * TOTAL_SAMPLES
    right_channel = [0.0] * TOTAL_SAMPLES

    # -------------------------------------------------------------
    # LAYER 1: Analog Tape & Vinyl Atmosphere (Very subtle bed)
    # -------------------------------------------------------------
    for i in range(TOTAL_SAMPLES):
        t = i / SAMPLE_RATE
        env = min(1.0, t * 5.0) * max(0.0, 1.0 - (t - 3.4) / 0.6 if t > 3.4 else 1.0)
        noise = (random.random() * 2.0 - 1.0) * 0.012
        # Crackle impulses
        crackle = 0.08 if random.random() < 0.0003 else 0.0
        val = (noise + crackle) * env
        left_channel[i] += val
        right_channel[i] += val

    # -------------------------------------------------------------
    # LAYER 2: Military Cipher Typewriter Clicks (Frames 6-28 -> 0.20s - 0.93s)
    # -------------------------------------------------------------
    click_times = [
        0.20, 0.24, 0.27, 0.31, 0.35, 0.38, 0.42, 0.45, 0.49,
        0.53, 0.56, 0.60, 0.64, 0.68, 0.72, 0.76, 0.81, 0.86, 0.91
    ]
    for c_time in click_times:
        start_idx = int(c_time * SAMPLE_RATE)
        click_dur_samples = int(SAMPLE_RATE * 0.018)  # 18ms micro click
        pan = (c_time - 0.2) / 0.7  # Pans gently from left (0.0) to right (1.0)
        click_freq = 1800.0 + (random.random() * 800.0)

        for s in range(click_dur_samples):
            idx = start_idx + s
            if idx >= TOTAL_SAMPLES:
                break
            env = math.exp(-s / (SAMPLE_RATE * 0.003))  # Fast exponential decay
            wave_val = math.sin(2.0 * math.pi * click_freq * (s / SAMPLE_RATE))
            val = wave_val * env * 0.16
            left_channel[idx] += val * (1.0 - pan * 0.6)
            right_channel[idx] += val * (0.4 + pan * 0.6)

    # -------------------------------------------------------------
    # LAYER 3: Heavy Classified Stamp Impact (Frame 18 -> 0.60s)
    # -------------------------------------------------------------
    stamp_start_idx = int(0.60 * SAMPLE_RATE)
    stamp_dur_samples = int(SAMPLE_RATE * 0.25)
    for s in range(stamp_dur_samples):
        idx = stamp_start_idx + s
        if idx >= TOTAL_SAMPLES:
            break
        t_stamp = s / SAMPLE_RATE
        # Snap/Crack transient (high pitched snap)
        snap_env = math.exp(-t_stamp / 0.008)
        snap = (random.random() * 2.0 - 1.0) * snap_env * 0.55
        # Wood/rubber mechanical thud (140 Hz downward pitch bend)
        thud_freq = max(45.0, 160.0 - t_stamp * 600.0)
        thud_env = math.exp(-t_stamp / 0.045)
        thud = math.sin(2.0 * math.pi * thud_freq * t_stamp) * thud_env * 0.65

        impact_val = snap + thud
        left_channel[idx] += impact_val * 0.85
        right_channel[idx] += impact_val * 0.85

    # -------------------------------------------------------------
    # LAYER 4: Deep Cinematic Sub-Bass Boom / Braam (0.60s -> 2.8s)
    # -------------------------------------------------------------
    boom_start_idx = int(0.60 * SAMPLE_RATE)
    boom_dur_samples = int(SAMPLE_RATE * 3.2)
    for s in range(boom_dur_samples):
        idx = boom_start_idx + s
        if idx >= TOTAL_SAMPLES:
            break
        t_boom = s / SAMPLE_RATE
        # Pitch starts at 68 Hz and glides down to 42 Hz
        freq = max(40.0, 68.0 - t_boom * 10.0)
        # Deep resonant envelope with saturation
        env = math.exp(-t_boom / 0.95)
        base_sine = math.sin(2.0 * math.pi * freq * t_boom)
        # Soft saturation / harmonics (cinematic brass/sub feel)
        saturated = math.tanh(base_sine * 1.6) * 0.68
        val = saturated * env
        left_channel[idx] += val
        right_channel[idx] += val

    # -------------------------------------------------------------
    # LAYER 5: Golden Shimmer & Whoosh Swell (Frames 22-48 -> 0.73s - 1.60s)
    # -------------------------------------------------------------
    whoosh_start_idx = int(0.72 * SAMPLE_RATE)
    whoosh_dur_samples = int(SAMPLE_RATE * 0.88)
    for s in range(whoosh_dur_samples):
        idx = whoosh_start_idx + s
        if idx >= TOTAL_SAMPLES:
            break
        t_whoosh = s / SAMPLE_RATE
        progress = t_whoosh / 0.88  # 0 to 1
        # Bell curve envelope
        env = math.sin(progress * math.pi) ** 2
        # Crystalline bells / metallic shimmer (chimes at 2400Hz, 3200Hz, 4800Hz)
        bell1 = math.sin(2.0 * math.pi * 2400.0 * t_whoosh) * 0.18
        bell2 = math.sin(2.0 * math.pi * 3200.0 * t_whoosh) * 0.14
        bell3 = math.sin(2.0 * math.pi * 4800.0 * t_whoosh) * 0.08
        air_noise = (random.random() * 2.0 - 1.0) * 0.15
        shimmer_val = (bell1 + bell2 + bell3 + air_noise) * env * 0.42

        # Dynamic stereo panning (sweeping left to right across the golden streak)
        pan_l = math.cos(progress * math.pi * 0.5)
        pan_r = math.sin(progress * math.pi * 0.5)

        left_channel[idx] += shimmer_val * pan_l
        right_channel[idx] += shimmer_val * pan_r

    # -------------------------------------------------------------
    # MASTERING: Normalization and Fade-Out
    # -------------------------------------------------------------
    # Find peak
    peak = 0.0001
    for i in range(TOTAL_SAMPLES):
        peak = max(peak, abs(left_channel[i]), abs(right_channel[i]))

    target_peak = 0.92  # -0.7 dBFS headroom
    gain = target_peak / peak

    # Write 16-bit PCM WAV
    with wave.open(str(output_wav_path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)

        out_bytes = bytearray()
        for i in range(TOTAL_SAMPLES):
            # Smooth fade-out in last 0.35 seconds
            t = i / SAMPLE_RATE
            master_fade = 1.0
            if t > 3.65:
                master_fade = max(0.0, 1.0 - (t - 3.65) / 0.35)

            samp_l = clamp(left_channel[i] * gain * master_fade)
            samp_r = clamp(right_channel[i] * gain * master_fade)

            int_l = int(samp_l * 32767.0)
            int_r = int(samp_r * 32767.0)

            out_bytes.extend(struct.pack("<hh", int_l, int_r))

        wf.writeframes(out_bytes)

    print(f"✅ Áudio cinemático sintetizado: {output_wav_path} (Duração: {DURATION}s @ {SAMPLE_RATE}Hz)")


if __name__ == "__main__":
    import sys
    import subprocess
    import shutil
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("public/intro_sfx.wav")
    generate_intro_sfx(out)
    if shutil.which("ffmpeg") and out.suffix.lower() == ".wav":
        mp3_out = out.with_suffix(".mp3")
        subprocess.run(["ffmpeg", "-y", "-i", str(out), "-b:a", "192k", str(mp3_out)], check=False)
        print(f"✅ Versão compactada para web gerada: {mp3_out}")

