#!/usr/bin/env python3

import sys, select, termios, tty, rclpy
from geometry_msgs.msg import Twist

# Velocidades máximas y pasos de ajuste
MAX_LIN_VEL = 0.5
MAX_ANG_VEL = 1.2
STEP_SIZE = 0.05

# Mensaje de ayuda (solo se imprime una vez)
msg = """
Control Your Mobile Robot!
---------------------------
  Moving around:    Lateral motion (Omni)
        w                    
   a    s    d          g       j
        x

w/x : increase/decrease linear velocity, Vx  (Max vel: 0.5)
a/d : increase/decrease angular velocity, W  (Max vel: 1.2)
g/j : increase/decrease lateral velocity, Vy (Max vel: 0.5)
space key, s : force stop

CTRL-C to quit
"""

def get_key():
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    key = sys.stdin.read(1) if rlist else ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, termios.tcgetattr(sys.stdin))
    return key

def limit_velocity(vel, max_vel):
    return max(min(vel, max_vel), -max_vel)

def print_vels(vx, w, vy):
    sys.stdout.write("\rcurrently:\tVx: {:.2f}\t W: {:.2f}\t Vy: {:.2f}  ".format(vx, w, vy))
    sys.stdout.flush()

def main():
    settings = termios.tcgetattr(sys.stdin)  # Guarda la configuración inicial

    rclpy.init()
    node = rclpy.create_node('omni_teleop_keyboard')
    pub = node.create_publisher(Twist, 'cmd_vel', 10)

    vx, vy, w = 0.0, 0.0, 0.0

    try:
        print(msg)
        while True:
            key = get_key()
            if key in {'w', 'x', 'a', 'd', 'g', 'j'}:
                vx += STEP_SIZE if key == 'w' else -STEP_SIZE if key == 'x' else 0
                vy += STEP_SIZE if key == 'g' else -STEP_SIZE if key == 'j' else 0
                w  += STEP_SIZE if key == 'a' else -STEP_SIZE if key == 'd' else 0

                vx, vy = limit_velocity(vx, MAX_LIN_VEL), limit_velocity(vy, MAX_LIN_VEL)
                w = limit_velocity(w, MAX_ANG_VEL)
                print_vels(vx, w, vy)

            elif key in {'s', ' '}:
                vx, vy, w = 0.0, 0.0, 0.0
                print_vels(vx, w, vy)

            elif key == '\x03':  # CTRL-C
                break

            twist = Twist()
            twist.linear.x, twist.linear.y, twist.angular.z = vx, vy, w
            pub.publish(twist)

    finally:
        pub.publish(Twist())
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)  # RESTAURA LA TERMINAL CORRECTAMENTE

if __name__ == '__main__':
    main()
