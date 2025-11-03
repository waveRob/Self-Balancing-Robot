"""
Run this script on the host machine to visualize the controller
"""

import json, socket, collections
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", PORT))
sock.setblocking(False)

N = 500  # points to keep
tbuf = collections.deque(maxlen=N)
filt_angl_buf = collections.deque(maxlen=N)
ref_angl_buf = collections.deque(maxlen=N)
angl_ubuf = collections.deque(maxlen=N)
angl_upbuf = collections.deque(maxlen=N)
angl_udbuf = collections.deque(maxlen=N)
angl_uibuf = collections.deque(maxlen=N)
stab_ubuf = collections.deque(maxlen=N)
stab_upbuf = collections.deque(maxlen=N)
stab_udbuf = collections.deque(maxlen=N)
stab_uibuf = collections.deque(maxlen=N)

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)

(line_filt_angl,) = ax1.plot([], [], label="measurement (deg)")
(line_ref_angl,) = ax1.plot([], [], label="ref (deg)")
ax1.set_title("Measurement and Reference")
ax1.legend()
ax1.set_ylabel("Angle (deg)")
ax1.grid(True)

(line_angl_u,) = ax2.plot([], [], color="red", label="Control (u)")
(line_angl_up,) = ax2.plot([], [], color="blue", label="Control (u_p)")
(line_angl_ud,) = ax2.plot([], [], color="green", label="Control (u_d)")
(line_angl_ui,) = ax2.plot([], [], color="orange", label="Control (u_i)")
ax2.set_title("Angel Reference PID (outer loop)")
ax2.legend()
ax2.set_ylabel("u (-)")
ax2.grid(True)

(line_stab_u,) = ax3.plot([], [], color="red", label="Control (u)")
(line_stab_up,) = ax3.plot([], [], color="blue", label="Control (u_p)")
(line_stab_ud,) = ax3.plot([], [], color="green", label="Control (u_d)")
(line_stab_ui,) = ax3.plot([], [], color="orange", label="Control (u_i)")
ax3.set_title("Stabalizing PID (inner loop)")
ax3.legend()
ax3.set_xlabel("time (s)")
ax3.set_ylabel("u (-)")
ax3.grid(True)

t0 = None
def update(_):
    global t0
    # drain any waiting packets
    while True:
        try:
            data, _ = sock.recvfrom(4096)
            d = json.loads(data.decode())
            if t0 is None: t0 = d["t"]

            tbuf.append(d["t"] - t0)
            filt_angl_buf.append(d["filt_angl"])
            ref_angl_buf.append(d["ref_angl"])
            angl_ubuf.append(d["angl_u"])
            angl_upbuf.append(d["angl_up"])
            angl_udbuf.append(d["angl_ud"])
            angl_uibuf.append(d["angl_ui"])
            stab_ubuf.append(d["stab_u"])
            stab_upbuf.append(d["stab_up"])
            stab_udbuf.append(d["stab_ud"])
            stab_uibuf.append(d["stab_ui"])
        except BlockingIOError:
            break
        
    if not tbuf: return None

    line_filt_angl.set_data(tbuf, filt_angl_buf)
    line_ref_angl.set_data(tbuf, ref_angl_buf)
    ax1.set_xlim(max(0, tbuf[0]), tbuf[-1] if tbuf else 10)
    ax1.relim(); ax1.autoscale(axis="y", tight=False)

    line_angl_u.set_data(tbuf, angl_ubuf)
    line_angl_up.set_data(tbuf, angl_upbuf)
    line_angl_ud.set_data(tbuf, angl_udbuf)
    line_angl_ui.set_data(tbuf, angl_uibuf)
    ax2.set_xlim(max(0, tbuf[0]), tbuf[-1] if tbuf else 10)
    ax2.relim(); ax2.autoscale(axis="y", tight=False)

    line_stab_u.set_data(tbuf, stab_ubuf)
    line_stab_up.set_data(tbuf, stab_upbuf)
    line_stab_ud.set_data(tbuf, stab_udbuf)
    line_stab_ui.set_data(tbuf, stab_uibuf)
    ax3.set_xlim(max(0, tbuf[0]), tbuf[-1] if tbuf else 10)
    ax3.relim(); ax3.autoscale(axis="y", tight=False)



    return None

ani = FuncAnimation(fig, update, interval=50, blit=False)
plt.show()
