from machine import Pin, PWM, time_pulse_us
import time

# ---- Ultrasonic sensor setup ----
TRIG_PIN = 21
ECHO_PIN = 20
SOUND_SPEED = 340  # m/s
TRIG_PULSE_DURATION_US = 10
MAX_PULSE_US = 30000  # timeout

trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

# ---- Servo setup ----
SERVO_PIN = 0
servo = PWM(Pin(SERVO_PIN))
servo.freq(50)  # standard 50Hz

# ---- Gate/logic config ----
THRESHOLD_CM = 15.0          # open when object is closer than this
OPEN_ANGLE = 0               # reversed: 0° = OPEN
CLOSED_ANGLE = 90            # reversed: 90° = CLOSED
HOLD_OPEN_SEC = 4.0          # keep gate open this long after object leaves

# ---- State ----
gate_open = False
last_open_time = 0.0

# ---- Helpers ----
def set_servo_angle(angle):
    """Set servo to angle (0–180). Adjust pulse widths if needed."""
    min_us = 500
    max_us = 2500
    duty_us = min_us + (max_us - min_us) * angle / 180.0
    duty = int(duty_us / 20000.0 * 65535.0)  # 20 ms period at 50 Hz
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

def measure_distance_cm():
    """Return distance in cm. If timeout, return a large number."""
    trig.value(0)
    time.sleep_us(5)
    trig.value(1)
    time.sleep_us(TRIG_PULSE_DURATION_US)
    trig.value(0)

    duration = time_pulse_us(echo, 1, MAX_PULSE_US)  # microseconds
    if duration < 0:
        return 9999.0  # treat timeout as 'far away'
    # distance cm = (speed m/s * us) / 20000
    return (SOUND_SPEED * duration) / 20000.0

# ---- Init: start closed ----
close_gate()

# ---- Main loop ----
while True:
    dist = measure_distance_cm()
    print("Distance: {:.1f} cm".format(dist))

    now_ms = time.ticks_ms()

    if dist < THRESHOLD_CM:
        if not gate_open:
            open_gate()
    else:
        if gate_open:
            # hold open for HOLD_OPEN_SEC after last open trigger
            if time.ticks_diff(now_ms, last_open_time) >= int(HOLD_OPEN_SEC * 1000):
                close_gate()

    time.sleep(0.05)  # 50 ms loop
