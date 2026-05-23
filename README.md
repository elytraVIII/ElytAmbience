# 🍃 ElytAmbience

**ElytAmbience** is a native ambient sound generator built for the BSD desktop. It is a high-performance rewrite of the popular [Blanket](https://github.com/rafaelmardojai/blanket) application, specifically optimized for **FreeBSD** and **GhostBSD**.

![ElytAmbience Screenshot](screenshot.png)

---

### ✨ Features
*   **🚀 Native Performance:** Built using GTK3 and GStreamer for a lightweight, efficient experience.
*   **🎧 Immersive Sounds:** Includes 14 atmospheric loops (Rain, Storm, City, etc.) with individual volume sliders.
*   **💾 Persistence:** Automatically remembers your active sounds and volume levels between sessions.
*   **🎨 MATE Integration:** Designed to look and feel right at home on the MATE Desktop Environment.
*   **📥 Background Playback:** Hides to the system tray so you can focus on your work while it plays.

---

### 📦 Installation

#### From Binary (Recommended for GhostBSD/FreeBSD)
Install the latest version using:
```bash
sudo pkg add https://github.com/elytraVIII/ElytAmbience/releases/latest/download/elytambiance-freebsd.pkg
```

#### From Source
Ensure you have the build dependencies installed (`meson`, `ninja`, `python3.11`, `py311-gobject3`, `gstreamer1-plugins-good`).

```bash
# Setup the build directory
meson setup build

# Compile the application
meson compile -C build

# Install system-wide
sudo meson install -C build
```

---
*Developed by ElytLabs. Bringing essential tools to the BSD desktop.*
