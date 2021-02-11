from which_pyqt import PYQT_VER

if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
    from PyQt4.QtCore import QLineF, QPointF, QObject
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import time
from functools import cmp_to_key

# Some global color constants that might be useful
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25


#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

    # Class constructor
    def __init__(self):
        super().__init__()
        self.pause = False

    # Some helper methods that make calls to the GUI, allowing us to send updates
    # to be displayed.

    def showTangent(self, line, color):
        self.view.addLines(line, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseTangent(self, line):
        self.view.clearLines(line)

    def blinkTangent(self, line, color):
        self.showTangent(line, color)
        self.eraseTangent(line)

    def showHull(self, polygon, color):
        self.view.addLines(polygon, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseHull(self, polygon):
        self.view.clearLines(polygon)

    def showText(self, text):
        self.view.displayStatusText(text)

    def solve_hull(self, points):
        num_points = len(points)

        if num_points <= 3:  # base case
            if len(points) is 3:
                hull = [None] * 3
                hull[0] = points[0]

                slope1 = self.get_slope(points[0], points[1])
                slope2 = self.get_slope(points[0], points[2])

                if slope2 > slope1:
                    hull[1] = points[2]
                    hull[2] = points[1]
                else:
                    hull[1] = points[1]
                    hull[2] = points[2]

                return hull

            else:  # if 2 or 1 points
                return points

        left_hull = self.solve_hull(points[:num_points//2])
        right_hull = self.solve_hull(points[num_points//2:num_points + 1])

        return self.combine_hull(left_hull, right_hull)

    def combine_hull(self, left_hull, right_hull):
        upper_tan, left_hull_start_index, right_hull_end_index = self.find_upper_tangent(left_hull, right_hull)
        lower_tan, left_hull_ending_index, right_hull_starting_index = self.find_lower_tangent(left_hull, right_hull)

        # self.showTangent(self.points_to_lines(left_hull), BLUE)
        # self.showTangent(self.points_to_lines(right_hull), BLUE)
        # self.showTangent(self.points_to_lines(upper_tan), YELLOW)
        # self.showTangent(self.points_to_lines(lower_tan), YELLOW)


        combined_hull = []  # First put in upper tan line

        index = left_hull_start_index
        while left_hull[index] != left_hull[left_hull_ending_index]:  # Go through the left side, starting at where the tan ends until hiting where the bottom tan starts
            # self.showTangent([QLineF(left_hull[(index - 1) % len(left_hull)], left_hull[index])], RED)
            combined_hull.append(left_hull[index])
            index = (index - 1) % len(left_hull)
        combined_hull.append(left_hull[index]) #Adds the last node (that is the start of bottom tan)

        index = right_hull_starting_index
        while right_hull[index] != right_hull[right_hull_end_index]:
            # self.showTangent([QLineF(right_hull[(index - 1) % len(right_hull)], right_hull[index])], RED)
            combined_hull.append(right_hull[index])
            index = (index - 1) % len(right_hull)
        combined_hull.append(right_hull[index])

        # self.showTangent(self.points_to_lines(combined_hull), YELLOW)

        return combined_hull

    def find_upper_tangent(self, left_hull, right_hull):
        left_tan, right_tan = False, False

        left_hull_index = self.get_point_index(left_hull, "right")
        right_hull_index = self.get_point_index(right_hull, "left")

        current_slope = self.get_slope(left_hull[left_hull_index], right_hull[right_hull_index])
        # self.showTangent(self.points_to_lines(left_hull), RED)
        # self.showTangent(self.points_to_lines(right_hull), BLUE)

        while not left_tan and not right_tan:
            while not left_tan:
                self.showTangent([QLineF(left_hull[left_hull_index], right_hull[right_hull_index])], GREEN)
                left_hull_index = (left_hull_index - 1) % len(left_hull)
                self.showTangent([QLineF(left_hull[left_hull_index], right_hull[right_hull_index])], YELLOW)
                new_slope = self.get_slope(left_hull[left_hull_index], right_hull[right_hull_index])
                if new_slope < current_slope:
                    left_tan, right_tan = False, False
                    current_slope = new_slope
                else:
                    left_tan = True
                    left_hull_index = (left_hull_index + 1) % len(left_hull)  # Since we can't move up anymore we use the last good index

            while not right_tan:
                self.showTangent([QLineF(left_hull[left_hull_index], right_hull[right_hull_index])], RED)
                right_hull_index = (right_hull_index + 1) % len(right_hull)
                self.showTangent([QLineF(left_hull[left_hull_index], right_hull[right_hull_index])], BLUE)
                new_slope = self.get_slope(left_hull[left_hull_index], right_hull[right_hull_index])
                if new_slope > current_slope:
                    left_tan, right_tan = False, False
                    current_slope = new_slope
                else:
                    right_tan = True
                    right_hull_index = (right_hull_index - 1) % len(right_hull)  # Since we can't move up anymore we use the last good index

        self.showTangent([QLineF(left_hull[left_hull_index], right_hull[right_hull_index])], BLUE)
        return [left_hull[left_hull_index], right_hull[right_hull_index]], left_hull_index, right_hull_index

    def find_lower_tangent(self, left_hull, right_hull):
        left_tan, right_tan = False, False

        left_hull_index = self.get_point_index(left_hull, "right")
        right_hull_index = self.get_point_index(right_hull, "left")

        current_slope = self.get_slope(left_hull[left_hull_index], right_hull[right_hull_index])
        # self.showTangent(self.points_to_lines(left_hull), RED)
        # self.showTangent(self.points_to_lines(right_hull), BLUE)

        while not left_tan and not right_tan:
            while not left_tan:
                # self.showTangent([QLineF(left_hull[left_hull_index], right_hull[right_hull_index])], GREEN)
                left_hull_index = (left_hull_index + 1) % len(left_hull)
                # self.showTangent([QLineF(left_hull[left_hull_index], right_hull[right_hull_index])], YELLOW)
                new_slope = self.get_slope(left_hull[left_hull_index], right_hull[right_hull_index])
                if new_slope > current_slope:
                    left_tan, right_tan = False, False
                    current_slope = new_slope
                else:
                    left_tan = True
                    left_hull_index = (left_hull_index - 1) % len(left_hull)  # Since we can't move up anymore we use the last good index

            while not right_tan:
                # self.showTangent([QLineF(left_hull[left_hull_index], right_hull[right_hull_index])], RED)
                right_hull_index = (right_hull_index - 1) % len(right_hull)
                # self.showTangent([QLineF(left_hull[left_hull_index], right_hull[right_hull_index])], BLUE)
                new_slope = self.get_slope(left_hull[left_hull_index], right_hull[right_hull_index])
                if new_slope < current_slope:
                    left_tan, right_tan = False, False
                    current_slope = new_slope
                else:
                    right_tan = True
                    right_hull_index = (right_hull_index + 1) % len(right_hull)  # Since we can't move up anymore we use the last good index

        # self.showTangent([QLineF(left_hull[left_hull_index], right_hull[right_hull_index])], BLUE)
        return [left_hull[left_hull_index], right_hull[right_hull_index]], left_hull_index, right_hull_index

    def get_slope(self, point1, point2):
        return (point2.y() - point1.y()) / (point2.x() - point1.x())  # Slope = change in y / change in x

    def get_point_index(self, hull, direction):
        index = 0
        record = hull[0].x()

        if direction is "right":
            for i in range(0, len(hull) - 1):
                if hull[i].x() > record:
                    index = i
                    record = hull[i].x()
        elif direction is "left":
            for i in range(0, len(hull) - 1):
                if hull[i].x() < record:
                    index = i
                    record = hull[i].x()

        return index

    def points_to_lines(self, points):
        lines = []
        for i in range(0, len(points)):
            if i == len(points) - 1:
                lines.append(QLineF(points[i], points[0]))
            else:
                lines.append(QLineF(points[i], points[i + 1]))
        return lines

    # This is the method that gets called by the GUI and actually executes
    # the finding of the hull
    def compute_hull(self, points, pause, view):
        self.pause = pause
        self.view = view
        assert (type(points) == list and type(points[0]) == QPointF)

        def compare(item1,
                    item2):  # https://stackoverflow.com/questions/5213033/sort-a-list-of-lists-with-a-custom-compare-function
            if item1.x() < item2.x():
                return -1  # return a negative value (< 0) when the left item should be sorted before the right item
            elif item2.x() < item1.x():
                return 1  # return a positive value (> 0) when the left item should be sorted after the right item
            else:
                return 0  # return 0 when both the left and the right item have the same weight and should be ordered "equally" without precedence

        t1 = time.time()
        sorted_points = sorted(points, key=cmp_to_key(compare))
        # TODO: SORT THE POINTS BY INCREASING X-VALUE
        t2 = time.time()

        t3 = time.time()
        # this is a dummy polygon of the first 3 unsorted points
        # polygon = [QLineF(sortedPoints[i], sortedPoints[(i + 1) % 3]) for i in range(3)]
        # TODO: REPLACE THE LINE ABOVE WITH A CALL TO YOUR DIVIDE-AND-CONQUER CONVEX HULL SOLVER
        polygon = self.points_to_lines(self.solve_hull(sorted_points))
        t4 = time.time()

        # when passing lines to the display, pass a list of QLineF objects.  Each QLineF
        # object can be created with two QPointF objects corresponding to the endpoints
        self.showHull(polygon, RED)
        self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4 - t3))
