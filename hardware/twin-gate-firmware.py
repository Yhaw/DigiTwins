# MicroPython - Smart Gate with WebSocket reporting (Pico W)
# Requires: uwebsockets (client), MicroPython on Pico W

import network
import time
import machine
import ujson
import uwebsockets.client as websockets
from machine import Pin, PWM, time_pulse_us

# ==== USER CONFIGURATION ====
SSID = ''
PASSWORD = ''
WS_URL = "wss://digitwins.onrender.com/ws?roomId=arnold-853&role=device"
#WS_URL = "wss://cc-digi-twin-crcqaec0fwh6dxbt.eastus-01.azurewebsites.net/ws?roomId=arnold-853&role=device"


# ---- Ultrasonic sensor setup ----
TRIG_PIN = 21
ECHO_PIN = 20
SOUND_SPEED = 340          # m/s
TRIG_PULSE_DURATION_US = 10
MAX_PULSE_US = 30000       # timeout for time_pulse_us

trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

# ---- Servo setup ----
SERVO_PIN = 0
servo = PWM(Pin(SERVO_PIN))
servo.freq(50)  # 50 Hz

# ---- Gate/logic config ----
THRESHOLD_CM = 15.0          # open when object is closer than this
OPEN_ANGLE = 0               # reversed: 0° = OPEN
CLOSED_ANGLE = 90            # reversed: 90° = CLOSED
HOLD_OPEN_SEC = 4.0          # keep gate open this long after object leaves

# ---- State ----
gate_open = False
last_open_time = 0
last_sent_gate = None        # track last sent state so we only send on change


# ==== Wi-Fi ====
def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to Wi-Fi:", SSID)
        wlan.connect(SSID, PASSWORD)
        t0 = time.ticks_ms()
        while not wlan.isconnected():
            time.sleep(0.2)
            if time.ticks_diff(time.ticks_ms(), t0) > 20000:
                raise RuntimeError("Wi-Fi connect timeout")
    print("Connected:", wlan.ifconfig())


# ==== Servo helpers ====
def set_servo_angle(angle):
    # 0.5ms..2.5ms pulse over 20ms period
    min_us = 500
    max_us = 2500
    duty_us = min_us + (max_us - min_us) * (angle / 180.0)
    duty = int(duty_us / 20000.0 * 65535.0)
    servo.duty_u16(duty)

def open_gate():
    global gate_open, last_open_time
    set_servo_angle(OPEN_ANGLE)
    gate_open = True
    last_open_time = time.ticks_ms()

def close_gate():
    global gate_open
    set_servo_angle(CLOSED_ANGLE)
    gate_open = False


# ==== Ultrasonic ====
def measure_distance_cm():
    trig.value(0)
    time.sleep_us(5)
    trig.value(1)
    time.sleep_us(TRIG_PULSE_DURATION_US)
    trig.value(0)

    duration = time_pulse_us(echo, 1, MAX_PULSE_US)
    if duration < 0:
        return 9999.0
    return (SOUND_SPEED * duration) / 20000.0  # cm


# ==== WebSocket send (safe) ====
def ws_send(ws, obj):
    try:
        ws.send(ujson.dumps(obj))
    except Exception as e:
        print("WS send error:", e)
        raise


# ==== Main control loop with WS reporting ====
def run():
    global last_sent_gate

    # start closed
    close_gate()

    while True:
        try:
            print("Connecting to WebSocket:", WS_URL)
            ws = websockets.connect(WS_URL)
            print("WebSocket connected")

            # optional: non-blocking recv if available
            try:
                if hasattr(ws, "sock"):
                    ws.sock.settimeout(0)
            except Exception:
                pass

            while True:
                # --- sensing and control ---
                dist = measure_distance_cm()
                print("Distance: {:.1f} cm".format(dist))

                now_ms = time.ticks_ms()

                if dist < THRESHOLD_CM:
                    if not gate_open:
                        open_gate()
                else:
                    if gate_open:
                        if time.ticks_diff(now_ms, last_open_time) >= int(HOLD_OPEN_SEC * 1000):
                            close_gate()

                # --- report only on state change ---
                current_gate = "OPEN" if gate_open else "CLOSED"
                if current_gate != last_sent_gate:
                    msg = {"type": "gate_state", "gate": current_gate}
                    print("Sending:", msg)
                    ws_send(ws, msg)
                    last_sent_gate = current_gate

                # --- optional: handle incoming commands OPEN/CLOSE ---
                # If your server sends commands, uncomment to react:
                # try:
                #     incoming = ws.recv()
                #     if incoming:
                #         data = ujson.loads(incoming)
                #         if data.get("type") == "command":
                #             action = str(data.get("action", "")).upper()
                #             if action == "OPEN" and not gate_open:
                #                 open_gate()
                #             elif action == "CLOSE" and gate_open:
                #                 close_gate()
                # except Exception:
                #     pass

                time.sleep(0.05)  # ~20 Hz loop

        except Exception as e:
            print("WebSocket error:", e)
            print("Reconnecting in 5 seconds...")
            try:
                ws.close()
            except Exception:
                pass
            time.sleep(5)


# ==== Boot sequence ====
connect_to_wifi()
run()
