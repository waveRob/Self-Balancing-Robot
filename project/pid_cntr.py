import json, socket, time, threading
import rcpy
import rcpy.mpu9250 as mpu
import rcpy.motor as motor
import rcpy.encoder as encoder
import utils
from utils import complementary_filter, joystick_thread
from evdev import InputDevice, categorize, ecodes
from PIDController import PIDController
from LowPassFilter import LowPassFilter


print("Press Ctrl-C to exit")


# Setup Connection to Host Computer #
# HOST = "192.168.7.1"   # usb connection
HOST = "192.168.137.1"  # hotspot connection
PORT = 5005            # open this on your PC
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# Initialize Motors and IMU
rcpy.set_state(rcpy.RUNNING)
mpu.initialize(enable_dmp=False)       # raw rates; set True if you use DMP


# Open Joystick # 
try:
    gamepad = InputDevice('/dev/input/event2')
    print(f"Connected to {gamepad.name}")
    threading.Thread(target=joystick_thread, args=(gamepad,), daemon=True).start()
except:
    print("Joistick not connected")
    jstick_x = 0.0
    jstick_y = 0.0
    button_y = False


# Constance #
MAX_ANGLE = 35
SPS = 50  # samples per second
MAX_SPEED = 0.9
MOTOR_POWER = False
CYCLETIME = 1/SPS


# Init Controllers #
k_throttle = 60 * (2152/SPS)
k_steering = 0.008 * (2152/SPS)

pid_angl = PIDController(
    k_p = 0.004,
    k_d = 0.0,
    k_i = 0.00001,
    e_int_max = 100,
    dt = CYCLETIME,
    )

pid_stab = PIDController(
    k_p = 1.4/30,
    k_d = 0.04/30,
    k_i = 0.0/30,
    e_int_max = 100,
    dt = CYCLETIME,
    )

balanc_ang = 12.5  # balancing angle


# Init Filter #
lpf_angl = LowPassFilter(Tf=0.06, dt=CYCLETIME)
lpf_throttle = LowPassFilter(Tf=0.6, dt=CYCLETIME)
lpf_steering = LowPassFilter(Tf=0.2, dt=CYCLETIME)


# Encoder Initialization #
enc2_prev = encoder.get(2)
enc3_prev = encoder.get(3)
wheel_speed = 0.0


# Init Variables #
u = 0.0
filt_ang = 0.0
e_pre = e_int  = 0.0
countdown = 3*SPS
dt = 1.0/SPS

jstick_x = jstick_y = 0.0
jstick_btn_y = False


# Main Loop #
try:
    while rcpy.get_state() == rcpy.RUNNING:
        # Get Loop Time #
        laptime_start = time.time()
        
        
        # Initialisation Delay #
        if countdown > 0:
            countdown -= 1
        elif countdown == 0 and MOTOR_POWER == False:
            MOTOR_POWER = True
            e_int = 0
            u = 0

        
        # Get Joystick Values #
        try:
            jstick_x = utils.axis_x
            jstick_y = utils.axis_y
            jstick_btn_y = utils.button_y
        except:
            pass
        
        # Stop if Y is pressed on Controller
        if jstick_btn_y == True:
            break
        
        
        # Get Encoders Values #
        enc2 = encoder.get(2)
        enc3 = encoder.get(3)
        enc_delta = ((enc3 - enc3_prev) - (enc2 - enc2_prev)) / 2
        enc2_prev, enc3_prev = enc2, enc3
        
        wheel_speed = -(enc_delta / dt)
            
            
        # Get IMU Values #
        d = mpu.read()
        ax, ay, az = d["accel"]
        gx, gy, gz = d["gyro"]
        
        
        # Get Tilt Angle #
        filt_ang = complementary_filter(filt_ang, gx, ay, az, dt, Tf=0.3)
        
        if filt_ang >= balanc_ang + MAX_ANGLE or filt_ang <= balanc_ang - MAX_ANGLE:
            print(f"Angle limit reached")
            break
        
        
        # Controller #
        throttle = k_throttle * lpf_throttle.step(jstick_y)
        steering = k_steering * lpf_steering.step(jstick_x)
        ref_angle = lpf_angl.step(pid_angl.step(-throttle-wheel_speed)) + balanc_ang 
        u = pid_stab.step(ref_angle - filt_ang)
        
        u_left = u - steering
        u_right = u + steering
        
        # Global limits
        u_left = min(MAX_SPEED, u_left)
        u_left = max(-MAX_SPEED, u_left)
        u_right = min(MAX_SPEED, u_right)
        u_right = max(-MAX_SPEED, u_right)


        # Send Date to Host #
        msg = {
            "t": laptime_start, "filt_ang": filt_ang, "cntr_ref":balanc_ang,
        }
        sock.sendto((json.dumps(msg) + "\n").encode(), (HOST, PORT))


        # Delay for Equal Elaps Time #
        elapsed = time.time() - laptime_start
        if CYCLETIME > elapsed:
            time.sleep(CYCLETIME - elapsed)
            
            
        # Set Motors always at CYCLETIME #
        if MOTOR_POWER:
            motor.set(2, -u_right)
            motor.set(3, u_left)
        
except KeyboardInterrupt:
    # Catch Ctrl-C
    pass

finally:
    print("\nBye BeagleBone!")