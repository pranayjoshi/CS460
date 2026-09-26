import math
 
from hw2.shape_base import ShapeDrawer, run
 
SIDE_LENGTH = 2.5   # all four sides are equal
SIDE_SPEED = 2.0
 
 
class DiamondDrawer(ShapeDrawer):
    def __init__(self):
        super().__init__('diamond_drawer')
        self.add_turn(math.pi / 4.0)              # tilt the square by 45 degrees
        for _ in range(3):
            self.add_forward(SIDE_LENGTH, SIDE_SPEED)
            self.add_turn(math.pi / 2.0)          # 90 degree corner
        self.add_forward(SIDE_LENGTH, SIDE_SPEED)  # 4th side closes the diamond
        self.add_turn(math.pi / 4.0)              # face the original heading again
        self.get_logger().info('Drawing a diamond...')
 
 
def main(args=None):
    run(DiamondDrawer, args)
 
 
if __name__ == '__main__':
    main()
 