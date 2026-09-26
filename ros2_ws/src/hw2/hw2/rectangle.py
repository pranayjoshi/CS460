import math
 
from hw2.shape_base import ShapeDrawer, run
 
WIDTH = 4.0      # long side (units)
HEIGHT = 2.0     # short side (units)
SIDE_SPEED = 2.0
RIGHT_ANGLE = math.pi / 2.0
 
 
class RectangleDrawer(ShapeDrawer):
    def __init__(self):
        super().__init__('rectangle_drawer')
        # Opposite sides are equal: WIDTH, HEIGHT, WIDTH, HEIGHT
        for side_length in (WIDTH, HEIGHT, WIDTH, HEIGHT):
            self.add_forward(side_length, SIDE_SPEED)
            self.add_turn(RIGHT_ANGLE)
        self.get_logger().info('Drawing a rectangle...')
 
 
def main(args=None):
    run(RectangleDrawer, args)
 
 
if __name__ == '__main__':
    main()
 