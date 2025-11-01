# 🛰️ TwinGate, The IoT Digital Twin Demo

**TwinGate** is a lightweight **IoT + Digital Twin** demo connecting a **Raspberry Pi Pico** (MicroPython) to a **web-based 3D dashboard** via a Node.js WebSocket backend.  
It uses an **ultrasonic sensor** and a **servo motor** to mirror real-world motion in a 3D twin.

> Built in collaboration with **Lesley Edinam** , Interactive Web Developer & 3D Artist (React • Three.js).

---

## 📺 Live 3D Dashboard

- **RoadTwin (3D dashboard):** https://roadtwin.netlify.app/  
  Use this to **view** the twin and **add/register devices** (see flow below).

---

## Repository Structure

```
DigiTwins-Workshop/
├── hardware/
│   ├── twin-gate-firmware.py   # MicroPython firmware for Raspberry Pi Pico
│   ├── uwebsockets/           # WebSocket client library for Pico
│   └── schematic.png         # Hardware wiring diagram
│
├── src/
│   └── index.js             # Backend server implementation
│
├── package.json            # Project dependencies
├── LICENSE               # MIT License
└── README.md            # Project documentation
```

---

## 🚀 Features

- Real-time **WebSocket** device → backend → 3D dashboard
- **Ultrasonic** distance + **servo** motion demo
- Simple **room-based** sessions for multi-device demos
- MicroPython firmware for **Raspberry Pi Pico**

---

## 🧩 Getting Started

### Installation Steps

1. Clone the repository
   ```bash
   git clone https://github.com/Arnold208/DigiTwins-Workshop.git
   cd DigiTwins-Workshop
   ```

2. Install and start backend (requires Node.js v18+)
   ```bash
   npm install
   npm start
   ```

Server endpoints:
- Local development: `http://localhost:3000`
- Production: `https://digitwins.onrender.com`
3) Frontend (3D Twin)
RoadTwin: https://roadtwin.netlify.app/

🔌 Hardware (Raspberry Pi Pico)
Parts: Raspberry Pi Pico, HC-SR04 ultrasonic, SG90 servo, breadboard & jumpers.

Pins:

Component	Pico Pin	Notes
Ultrasonic Trigger	GP20	Output trigger
Ultrasonic Echo	GP21	Use divider if HC-SR04 (Echo is 5V)
Servo Signal	GP0	PWM out
VCC	5V (VBUS)	Power (sensor & servo)
GND	GND	Common ground

⚠️ Echo line on standard HC-SR04 is 5V. Use a divider (e.g., 2kΩ to GND, 1kΩ to pin) before GP21.

⬆️ Flashing Firmware
Open Thonny, connect Pico.

Copy hardware/uwebsockets/ onto the Pico (root).

Copy hardware/twin-gate-firmware.py onto the Pico (optionally rename to main.py for auto-run).

Edit Wi-Fi + WebSocket WS_URL in the firmware (see below).

Run.

🔁 Device Registration & Viewing Flow (RoadTwin)
TwinGate uses room-based sessions to keep devices and viewers in sync.

A) Create / Join a Room (Viewer)
Open RoadTwin: https://roadtwin.netlify.app/

Click Join Room.

Enter a Room ID (e.g., leslie-871) and join.

You’ll see an empty scene waiting for device telemetry.

### Device Configuration

Configure your device's WebSocket URL in the Pico firmware (`twin-gate-firmware.py`):

```python
# For production server
WS_URL = "wss://digitwins.onrender.com/ws?roomId=workshop-001&role=device"

# For local development
WS_URL = "ws://localhost:3000/ws?roomId=workshop-001&role=device"
```
Reboot the Pico. Once connected:

The device auto-registers in the backend upon first telemetry message.

The RoadTwin dashboard (in the same room) will show the device and start updating the 3D scene.

### Manual Device Registration (Optional)

You can pre-register devices using the registration API:

```http
POST /api/devices
Content-Type: application/json

{
    "devid": "pico-001",
    "name": "Distance Sensor Unit",
    "roomId": "workshop-001"
}
```
Not required for basic demos — the default flow auto-registers on first telemetry in most setups.

### Telemetry Format

Example WebSocket payload:

```json
{
    "type": "telemetry",
    "devid": "pico-001",
    "roomId": "workshop-001",
    "distance_cm": 42.7,
    "servo_deg": 90,
    "timestamp": 1730457600
}
```
The backend relays this to RoadTwin, which animates the 3D model (e.g., gate tilt or marker position).

## System Architecture

### Data Flow
Pico measures distance and updates servo.

Firmware sends WebSocket telemetry to backend (room-scoped).

Backend broadcasts to RoadTwin (same room).

The 3D twin responds in real time.

## Troubleshooting

### Common Issues and Solutions
No device in dashboard

Ensure roomId in firmware matches the room you joined on RoadTwin.

Check that the backend URL in WS_URL is reachable (local vs hosted).

No distance readings

Verify HC-SR04 wiring; use an Echo voltage divider; start with a flat target at 10–50 cm.

Servo doesn’t move

Confirm 5 V supply and GP0 PWM wire.

Backend errors

Run npm install again.

Confirm Node v18+.

## Credits

### Development Team
Kimkpe Arnold Sylvian, IoT Engineer & Educator

Lesley (Leslie) Edinam, Interactive Web Developer • 3D Artist (React, Three.js)

📜 License
MIT free to use for learning, demos, and extensions.

## Roadmap

### Planned Improvements
Add a wiring schematic.png under hardware/.

Include a short GIF of the live demo in action.

Add status badges (Node version, license, build).
