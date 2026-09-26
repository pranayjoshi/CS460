import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from turtlesim.msg import Pose

# Tolerances used to decide when a segment is finished
DISTANCE_TOLERANCE = 0.01   # turtlesim units
ANGLE_TOLERANCE = 0.005     # radians (about 0.3 degrees)


def normalize_angle(angle):
    """Wrap an angle to the range [-pi, pi]."""
    return math.atan2(math.sin(angle), math.cos(angle))


def clamp(value, low, high):
    """Limit value to the range [low, high]."""
    return max(low, min(high, value))


class ShapeDrawer(Node):
    """Base node: publishes Twist, subscribes to Pose, runs a segment queue."""

    CONTROL_PERIOD = 0.02  # seconds -> 50 Hz control loop

    def __init__(self, node_name):
        super().__init__(node_name)

        # Publisher: velocity commands to the turtle
        self.cmd_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        # Subscriber: the turtle's current position and heading
        self.pose_sub = self.create_subscription(
            Pose, '/turtle1/pose', self.pose_callback, 10)

        self.pose = None            # latest Pose (None until first message)
        self.segments = []          # queue of segments still to run
        self.current = None         # segment being executed right now
        self.segment_start = None   # (x, y) where the current forward segment began
        self.target_heading = None  # ideal heading; prevents turn error build-up
        self.arc_swept = 0.0        # angle swept so far in the current arc
        self.last_theta = 0.0       # previous heading, used to measure the arc
        self.done = False

        self.timer = self.create_timer(self.CONTROL_PERIOD, self.control_loop)

    # ------------------------------------------------------------------
    # ROS callbacks
    # ------------------------------------------------------------------
    def pose_callback(self, msg):
        """Store the latest pose reported by turtlesim."""
        self.pose = msg

    # ------------------------------------------------------------------
    # Building blocks used by the shape classes to describe a path
    # ------------------------------------------------------------------
    def add_forward(self, distance, speed=1.5):
        """Drive straight for `distance` units."""
        self.segments.append(
            {'kind': 'forward', 'distance': distance, 'speed': speed})

    def add_turn(self, angle, max_speed=1.5):
        """Rotate in place by `angle` radians (positive = counter-clockwise)."""
        self.segments.append(
            {'kind': 'turn', 'angle': angle, 'max_speed': max_speed})

    def add_arc(self, linear, angular, sweep):
        """Drive along a curve (radius = linear / angular) sweeping `sweep` radians."""
        self.segments.append(
            {'kind': 'arc', 'linear': linear, 'angular': angular, 'sweep': sweep})

    # ------------------------------------------------------------------
    # Control loop
    # ------------------------------------------------------------------
    def control_loop(self):
        """Runs at 50 Hz: execute the current segment or start the next one."""
        if self.pose is None or self.done:
            return  # wait for the first pose message

        if self.target_heading is None:
            self.target_heading = self.pose.theta

        if self.current is None:
            if not self.segments:
                self.finish()
                return
            self.current = self.segments.pop(0)
            self.begin_segment(self.current)

        linear, angular, finished = self.run_segment(self.current)
        if finished:
            self.current = None
            self.publish_velocity(0.0, 0.0)
        else:
            self.publish_velocity(linear, angular)

    def begin_segment(self, seg):
        """Record the starting conditions of a segment."""
        if seg['kind'] == 'forward':
            self.segment_start = (self.pose.x, self.pose.y)
        elif seg['kind'] == 'turn':
            self.target_heading = normalize_angle(self.target_heading + seg['angle'])
        elif seg['kind'] == 'arc':
            self.arc_swept = 0.0
            self.last_theta = self.pose.theta
            self.target_heading = normalize_angle(
                self.target_heading + math.copysign(seg['sweep'], seg['angular']))

    def run_segment(self, seg):
        """Return (linear, angular, finished) for the current segment."""
        if seg['kind'] == 'forward':
            travelled = math.hypot(self.pose.x - self.segment_start[0],
                                   self.pose.y - self.segment_start[1])
            remaining = seg['distance'] - travelled
            if remaining <= DISTANCE_TOLERANCE:
                return 0.0, 0.0, True
            # Slow down as we approach the end so we do not overshoot
            speed = clamp(2.0 * remaining, 0.1, seg['speed'])
            return speed, 0.0, False

        if seg['kind'] == 'turn':
            error = normalize_angle(self.target_heading - self.pose.theta)
            if abs(error) <= ANGLE_TOLERANCE:
                return 0.0, 0.0, True
            # Proportional control, with a minimum speed so it never stalls
            angular = clamp(4.0 * error, -seg['max_speed'], seg['max_speed'])
            if abs(angular) < 0.1:
                angular = math.copysign(0.1, error)
            return 0.0, angular, False

        # Arc: keep a constant radius until the requested angle is swept
        self.arc_swept += abs(normalize_angle(self.pose.theta - self.last_theta))
        self.last_theta = self.pose.theta
        remaining = seg['sweep'] - self.arc_swept
        if remaining <= ANGLE_TOLERANCE:
            return 0.0, 0.0, True
        # Scale BOTH velocities so the radius stays the same while slowing down
        scale = clamp(remaining / 0.3, 0.05, 1.0)
        return seg['linear'] * scale, seg['angular'] * scale, False

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def publish_velocity(self, linear, angular):
        """Publish a Twist with forward speed `linear` and turn rate `angular`."""
        msg = Twist()
        msg.linear.x = float(linear)
        msg.angular.z = float(angular)
        self.cmd_pub.publish(msg)

    def stop(self):
        """Command zero velocity (safe to call even during shutdown)."""
        try:
            self.publish_velocity(0.0, 0.0)
        except Exception:  # context may already be shut down after Ctrl+C
            pass

    def finish(self):
        """Stop the turtle and tell main() the drawing is complete."""
        self.publish_velocity(0.0, 0.0)
        self.timer.cancel()
        self.done = True
        self.get_logger().info('Drawing complete - turtle stopped.')


def run(node_class, args=None):
    """Create the node, spin until it is done, then shut down cleanly."""
    rclpy.init(args=args)
    node = node_class()
    try:
        while rclpy.ok() and not node.done:
            rclpy.spin_once(node, timeout_sec=0.1)
        # Spin briefly so the final zero-velocity message is actually sent
        for _ in range(5):
            rclpy.spin_once(node, timeout_sec=0.05)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()