
import math

from hw2.shape_base import ShapeDrawer, run

RADIUS = 2.0                 # circle radius in turtlesim units
LINEAR_SPEED = 2.0           # forward speed (units/s)
ANGULAR_SPEED = LINEAR_SPEED / RADIUS   # v = w * r  ->  w = v / r


class CircleDrawer(ShapeDrawer):
    def __init__(self):
        super().__init__('circle_drawer')
        # One arc that sweeps a full revolution (2*pi radians)
        self.add_arc(LINEAR_SPEED, ANGULAR_SPEED, 2.0 * math.pi)
        self.get_logger().info('Drawing a circle...')


def main(args=None):
    run(CircleDrawer, args)


if __name__ == '__main__':
    main()