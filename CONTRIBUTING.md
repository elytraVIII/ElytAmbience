# Contributing to ElytAmbience

Thank you for your interest in contributing to ElytAmbience! We welcome contributions in the form of new sounds, code improvements, or bug reports.

## Sounds
New sounds are welcomed, both to **add** different sounds or to **replace** the existing ones to improve them. Before adding them, the soundclips must pass a criterion:
* **Appropriate license:** Licenses such as `CC BY (SA)` and `CC0`.
* **Technical criterion:** Detailed below.
* **Ogg Vorbis format**

### Technical Criterion
Sounds should fit these psychoacoustic parameters to be comfortable as ambient sounds:

| Criteria | LUFS (Int.) | Range | True Peak (dBTP) | Max LUFS |
| :---: | :---: | :---: | :---: | :---: |
| Minimum | -35 | 5-7 | -30 | -30 |
| Ideal | -27 | 7-🔝 | -7,5 | -25 |
| Maximum | -23 | 🔝 | -6 | -18 |

**Priority:** 1. Range, 2. LUFS Integrated, 3. Maximum LUFS, 4. True Peak.

### How to measure
* Set all faders to 100% (`0 dB = 100%`).
* Use analyzers like **x42 Meter Collection** (with Carla) or **Ardour** (Loudness Analysis).

### How to fit
* **Range:** Cannot be changed upwards. If > 3.5 and doesn't fit, contact the original sound editor or the ElytAmbience maintainers.
* **LUFS:** Modify by changing the clip's gain (volume).
* **True Peak:** Use a limiter with a threshold slightly above -6 dB and short release times (<5 ms).

### Where to put the soundclips
Files go in `assets/sounds` with the `.ogg` extension (Ogg Vorbis encoding).

### Icons
Sounds must have a symbolic icon. No sound will be included without a proper icon. Icons go in `assets/icons` and should follow the naming convention `elytambiance-<soundname>-symbolic.svg`.

---
*Based on the contributing guidelines from [Blanket](https://github.com/rafaelmardojai/blanket).*
