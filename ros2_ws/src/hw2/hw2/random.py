import math
import random
 
from turtlesim.srv import SetPen
 
from hw2.shape_base import ShapeDrawer, clamp, normalize_angle, run
 
RUN_TIME = 40.0          # seconds of drawing before the turtle stops
WORLD_SIZE = 11.0        # turtlesim window is about 11 x 11 units
CENTER = WORLD_SIZE / 2.0
SAFE_MARGIN = 1.5        # start steering away when this close to a wall
 
 
class RandomDrawer(ShapeDrawer):
    def __init__(self):
        super().__init__('random_drawer')
        self.pen_client = self.create_client(SetPen, '/turtle1/set_pen')
        self.elapsed = 0.0       # seconds since drawing started
        self.hold_until = 0.0    # when to pick the next random motion
        self.linear = 0.0
        self.angular = 0.0
        self.get_logger().info(f'Drawing a random pattern for {RUN_TIME:.0f} s...')
 
    def control_loop(self):
        """Runs at 50 Hz: wander randomly, but stay away from the walls."""
        if self.pose is None or self.done:
            return
 
        self.elapsed += self.CONTROL_PERIOD
        if self.elapsed >= RUN_TIME:
            self.finish()
            return
 
        if self.near_wall():
            linear, angular = self.steer_to_center()
            self.hold_until = self.elapsed   # pick a fresh motion afterwards
        else:
            if self.elapsed >= self.hold_until:
                self.pick_new_motion()
            linear, angular = self.linear, self.angular
 
        self.publish_velocity(linear, angular)
 
    def near_wall(self):
        """True if the turtle is inside the safety margin of any wall."""
        x, y = self.pose.x, self.pose.y
        return (x < SAFE_MARGIN or x > WORLD_SIZE - SAFE_MARGIN or
                y < SAFE_MARGIN or y > WORLD_SIZE - SAFE_MARGIN)
 
    def steer_to_center(self):
        """Turn toward the middle of the window and drive there."""
        desired = math.atan2(CENTER - self.pose.y, CENTER - self.pose.x)
        error = normalize_angle(desired - self.pose.theta)
        angular = clamp(4.0 * error, -3.0, 3.0)
        # Turn in place if facing away from the centre, otherwise move forward
        linear = 1.5 if abs(error) < 0.6 else 0.0
        return linear, angular
 
    def pick_new_motion(self):
        """Choose a random speed, turn rate, duration and pen colour."""
        self.linear = random.uniform(1.0, 2.5)
        self.angular = random.uniform(-3.0, 3.0)
        self.hold_until = self.elapsed + random.uniform(0.5, 2.0)
        self.set_random_pen()
 
    def set_random_pen(self):
        """Ask turtlesim to change the pen colour and width."""
        if not self.pen_client.service_is_ready():
            return
        request = SetPen.Request()
        request.r = random.randint(0, 255)
        request.g = random.randint(0, 255)
        request.b = random.randint(0, 255)
        request.width = random.randint(2, 6)
        request.off = 0
        self.pen_client.call_async(request)
 
 
def main(args=None):
    run(RandomDrawer, args)
 
 
if __name__ == '__main__':
    main()
 