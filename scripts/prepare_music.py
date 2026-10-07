#!/usr/bin/env python3
"""Render an original, quiet piano-and-pad loop for the site's existing audio controls."""

from pathlib import Path
import json
import subprocess
import tempfile
import wave

import numpy as np
from scipy.signal import butter, sosfilt


ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "music"
RATE, DURATION = 44100, 96
SAMPLES = RATE * DURATION
RNG = np.random.default_rng(20261003)


def frequency(note):
    return 440 * 2 ** ((note - 69) / 12)


def add_note(track, start, note, length, gain, pan=0, pad=False):
    time = np.arange(round(length * RATE), dtype=np.float64) / RATE
    hz = frequency(note)
    if pad:
        signal = sum(np.sin(2 * np.pi * hz * (1 + detune) * time + phase) * weight
                     for detune, phase, weight in [(-.0018, 0, .42), (0, .7, .42), (.0018, 1.2, .42), (0, .4, .08)])
        signal += .12 * np.sin(4 * np.pi * hz * time + .5)
        envelope = np.sin(np.pi * time / length) ** 2
    else:
        # Soft attack and independently decaying partials, without sharp percussion.
        signal = np.zeros_like(time)
        for partial, weight in [(1, 1), (2, .24), (3, .085), (4, .022)]:
            signal += weight * np.sin(2 * np.pi * hz * partial * (1 + .00006 * partial ** 2) * time) * np.exp(-time * (.43 + .19 * partial))
        envelope = (1 - np.exp(-time / .024)) * np.minimum(1, (length - time) / .5)
    mono = signal * envelope * gain
    stereo = np.stack([mono * np.sqrt((1 - pan) / 2), mono * np.sqrt((1 + pan) / 2)], axis=1)
    indices = (round(start * RATE) + np.arange(len(time))) % SAMPLES
    track[indices] += stereo.astype(np.float32)


def main():
    DESTINATION.mkdir(exist_ok=True)
    track = np.zeros((SAMPLES, 2), dtype=np.float32)
    chords = [[50, 57, 61, 64, 66], [47, 54, 57, 61, 64], [43, 50, 54, 57, 59],
              [45, 52, 54, 59, 61], [42, 49, 52, 57, 61], [43, 50, 54, 57, 62]]
    melody = [[73, 76, 69], [73, 71, 69], [74, 71, 69], [73, 76, 78], [76, 73, 69], [71, 74, 69]]
    for index, chord in enumerate(chords):
        start = index * 16
        for voice, note in enumerate(chord):
            add_note(track, start - 2, note, 20, .025 if voice else .032, (voice - 2) * .14, pad=True)
        for beat, voice in enumerate([0, 2, 4, 1, 3, 2, 4, 3]):
            add_note(track, start + beat * 2 + .18, chord[voice] + 12, 9, .085 * RNG.uniform(.83, 1), (voice - 2) * .18)
        for beat, note in enumerate(melody[index]):
            add_note(track, start + 3 + beat * 4, note, 11, .056, [-.25, .3, -.1][beat])
    # Circular reverb preserves decays across the loop boundary.
    wet = sosfilt(butter(2, 3100, fs=RATE, output="sos"),
                  np.concatenate([track[-RATE * 2:], track]), axis=0)[RATE * 2:]
    for delay, gain in [(.23, .14), (.47, .13), (.79, .12), (1.13, .10), (1.67, .085), (2.39, .07), (3.47, .045)]:
        track += np.roll(wet[:, ::-1], round(delay * RATE), axis=0) * gain
    track = sosfilt(butter(2, 42, btype="highpass", fs=RATE, output="sos"),
                    np.concatenate([track[-RATE * 2:], track]), axis=0)[RATE * 2:]
    track *= .45 / np.max(np.abs(track))
    assert np.isfinite(track).all() and np.max(np.abs(track)) <= .451
    pcm = np.round(track * 32767).astype("<i2")
    with tempfile.TemporaryDirectory(prefix="music-render-", dir=DESTINATION) as temporary:
        wav = Path(temporary) / "warm-airy.wav"
        with wave.open(str(wav), "wb") as stream:
            stream.setnchannels(2); stream.setsampwidth(2); stream.setframerate(RATE); stream.writeframes(pcm.tobytes())
        output = DESTINATION / "ShouYuLove_Warm_Airy_v1_1.mp3"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(wav),
                        "-c:a", "libmp3lame", "-b:a", "160k", "-metadata", "title=以手予爱 · 晨光", str(output)], check=True)
    (DESTINATION / "ShouYuLove_Warm_Airy_v1_1.txt").write_text(
        "以手予爱 · 晨光\n原创合成背景音乐，未使用第三方录音或旋律。\n"
        "96 秒循环，D 大调，60 BPM；柔和钢琴音色、缓慢和声与空气感混响。\n"
        "使用 scripts/prepare_music.py 重建；延音跨越循环边界，页面切换保持同一首背景音乐。\n")
    print(json.dumps({"file": str(output.relative_to(ROOT)), "seconds": DURATION,
                      "rms_dbfs": 20 * np.log10(np.sqrt(np.mean(track ** 2))),
                      "boundary_step": float(np.max(np.abs(track[0] - track[-1])))}))


if __name__ == "__main__":
    main()
