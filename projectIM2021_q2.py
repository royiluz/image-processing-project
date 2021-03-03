import cv2
from xlwt import Workbook
import math
import numpy as np
from projectIM2021_q1 import load_images_from_folder, find_circles
from projectIM2021_q1 import canny as q1_canny


def canny(img_, sigma=0.70):
    img_ = cv2.bilateralFilter(img_, 5, 30, 150)

    v = np.median(img_)
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(img_, lower, upper)
    return edged


def get_closet_point(c_corners, point, max_distance_from_point=0):
    closet_point = None
    closet_dist = 100
    for c_ in c_corners:
        cur_dist = math.dist(c_[0], point)
        if max_distance_from_point == 0:
            if cur_dist < closet_dist:
                closet_dist = cur_dist
                closet_point = c_[0]
        else:
            if cur_dist < max_distance_from_point and cur_dist < closet_dist:
                closet_dist = cur_dist
                closet_point = c_[0]

    if closet_point is None:
        return point
    else:
        return closet_point


def write_to_sheet(sorted_points, sheet_):
    for index_, p in enumerate(sorted_points):
        point_index = index_ + 1
        sheet_.write(point_index, 0, str(point_index))
        sheet_.write(point_index, 1, f'{p[0]}')
        sheet_.write(point_index, 2, f'{p[1]}')


def find_7(c_corners, c_hand, avg_finger_thickness_):
    thump = c_hand[0]
    index_finger_row = c_hand[1][1]
    middle_finger_row = c_hand[2][1]
    ring_finger_row = c_hand[3][1]
    little_finger_row = c_hand[4][1]
    little_finger = c_hand[4]

    # Get all points by some conditions:
    p_list = []
    for c_ in c_corners:
        x_, y_ = c_.ravel()
        if x_ < thump[0] and middle_finger_row < y_ < ring_finger_row and math.dist(little_finger,
                                                                                    [x_, y_]) < math.dist(thump, [x_,
                                                                                                                  y_]) and np.abs(
            middle_finger_row - y_) < np.abs(little_finger_row - y_) \
                and 1.5 * np.abs(ring_finger_row - y_) < np.abs(index_finger_row - y_):
            p_list.append([x_, y_])

    # Get right point:
    if len(p_list) == 0:
        return [0, 0]
    point_7 = p_list.pop()
    for c_ in p_list:
        if c_[0] > point_7[0]:
            point_7 = c_.copy()

    # Distance between ring finger and point 7:
    finger_distance = int(math.dist(point_7, c_hand[3]))
    hand_angle = point_7[1] - middle_finger_row - (avg_finger_thickness_ * 0.5)
    return finger_distance, hand_angle, point_7


def find_6(c_corners, c_hand, avg_finger_length, hand_angle):
    index_finger = c_hand[1]
    length = avg_finger_length
    angle = 0

    end_x = int(index_finger[0] + length * math.cos(math.radians(angle)))
    end_y = int(index_finger[1] + length * math.sin(math.radians(angle)))

    if hand_angle > 30:  # The hand is at a downward angle
        end_x = int(index_finger[0] - (hand_angle * 0.5) + length * math.cos(math.radians(angle)))

    approximate_point_6 = [end_x, end_y]
    point_6 = get_closet_point(c_corners, approximate_point_6, 25)

    return point_6, approximate_point_6


def find_4(c_corners, point_6, avg_finger_length):
    length = avg_finger_length // 1.5
    angle = 0

    end_x = int(point_6[0] + length * math.cos(math.radians(angle)))
    end_y = int(point_6[1] + length * math.sin(math.radians(angle)))

    if avg_finger_length > 180:  # Big hand
        end_x = int(point_6[0] + (length / 2) * math.cos(math.radians(angle)))

    approximate_point_4 = [end_x, end_y]
    point_4 = get_closet_point(c_corners, approximate_point_4)

    return point_4, approximate_point_4


def find_8(c_corners, point_7):
    length = 100
    angle = 70
    end_x = int(point_7[0] + length * math.cos(math.radians(angle)))
    end_y = int(point_7[1] + length * math.sin(math.radians(angle)))

    approximate_point_8 = [end_x, end_y]
    point_8 = get_closet_point(c_corners, approximate_point_8, 30)

    return point_8, approximate_point_8


def find_3(c_corners, point_4):
    angle = -15
    length = 70

    end_x = int(point_4[0] + length * math.cos(math.radians(angle)))
    end_y = int(point_4[1] + length * math.sin(math.radians(angle)))

    approximate_point_3 = [end_x, end_y]
    point_3 = get_closet_point(c_corners, approximate_point_3, 30)

    return point_3, approximate_point_3


def find_1(c_corners, point_8, hand_angle):
    angle = -10
    length = 159

    end_x = int(point_8[0] + length * math.cos(math.radians(angle)))
    end_y = int(point_8[1] + length * math.sin(math.radians(angle)))

    if hand_angle > 30:
        end_y = int(point_8[1] + hand_angle * 0.5 + length * math.sin(math.radians(angle)))

    approximate_point_1 = [end_x, end_y]
    point_1 = get_closet_point(c_corners, approximate_point_1, 40)

    return point_1, approximate_point_1


def find_2(c_corners, point_1):
    end_x = int(point_1[0] + 135 * math.cos(math.radians(-73)))
    end_y = int(point_1[1] + 135 * math.sin(math.radians(-73)))

    approximate_point_2 = [end_x, end_y]
    point_2 = get_closet_point(c_corners, approximate_point_2, 50)

    return point_2, approximate_point_2


def find_9(c_corners, point_1, point_8):
    approximate_point_9 = [(point_1[0] + point_8[0]) // 2, (point_1[1] + point_8[1]) // 2]
    point_9 = get_closet_point(c_corners, approximate_point_9, 20)

    return point_9, approximate_point_9


def find_5(c_corners, point_4, point_6):
    approximate_point_5 = [(point_4[0] + point_6[0]) // 2, (point_4[1] + point_6[1]) // 2]
    point_5 = get_closet_point(c_corners, approximate_point_5, 20)

    return point_5, approximate_point_5


def find_all_points(c_corners, c_hand, avg_finger_thickness_, sheet_):
    # Find 7:
    avg_finger_length, hand_angle, point_7 = find_7(c_corners, c_hand, avg_finger_thickness_)

    # Find 6:
    point_6, prx_point_6 = find_6(c_corners, c_hand, avg_finger_length, hand_angle)

    # Find 4:
    point_4, prx_point_4 = find_4(c_corners, point_6, avg_finger_length)

    # Find 8:
    point_8, prx_point_8 = find_8(c_corners, point_7)

    # Find 1:
    point_1, prx_point_1 = find_1(c_corners, point_8, hand_angle)

    # Find 3:
    point_3, prx_point_3 = find_3(c_corners, point_4)

    # Find 9:
    point_9, prx_point_9 = find_9(c_corners, point_1, point_8)

    # Find 2:
    point_2, prx_point_2 = find_2(c_corners, point_1)

    # Find 5:
    point_5, prx_point_5 = find_5(c_corners, point_4, point_6)

    # All Points:
    final_points = [point_1, point_2, point_3, point_4, point_5, point_6, point_7, point_8, point_9]
    approximate_points_ = [prx_point_1, prx_point_2, prx_point_3, prx_point_4, prx_point_5, prx_point_6, prx_point_8,
                           prx_point_9]
    write_to_sheet(final_points, sheet_)

    return final_points, approximate_points_


if __name__ == '__main__':
    # Create csv file:
    wb = Workbook()

    # load all images:
    gray_images, color_images = load_images_from_folder('other_images')

    # Iterate all images:
    for index, img in enumerate(gray_images):
        # add_sheet is used to create sheet.
        sheet = wb.add_sheet(f'image {index + 1}')
        sheet.write(0, 0, 'point')
        sheet.write(0, 1, 'X')
        sheet.write(0, 2, 'Y')

        # Canny:
        canny_img = canny(img)
        cimg = color_images[index]

        # Get fingers from projectIM2021_q1:
        points = find_circles(q1_canny(img))
        if len(points) != 5:
            continue

        # Get average of fingers thickness:
        avg_finger_thickness = 2 * np.mean(points[:, 2])

        coordinates_thumb_to_little_finger = points[points[:, 1].argsort()]  # Sort points by row
        coordinates_thumb_to_little_finger = np.delete(coordinates_thumb_to_little_finger, 2, 1)  # delete third column

        # Get significant points:
        corners = cv2.goodFeaturesToTrack(canny_img, 1000, 0.01, 8)
        corners = np.int0(corners)

        # Draw significant points
        # for i in corners[0:]:
        #     x, y = i.ravel()
        #     cv2.circle(cimg, (x, y), radius=3, color=(255, 0, 0), thickness=4)

        # Find points:
        final_coordinates, approximate_points = find_all_points(corners[0:], coordinates_thumb_to_little_finger,
                                                                avg_finger_thickness,
                                                                sheet)

        # Draw points:
        for c in final_coordinates:
            cv2.circle(cimg, (c[0], c[1]), radius=3, color=(0, 0, 255), thickness=4)

        # Draw lines:
        for i in range(len(final_coordinates) - 1):
            start_point = (final_coordinates[i][0], final_coordinates[i][1])
            end_point = (final_coordinates[i + 1][0], final_coordinates[i + 1][1])
            cimg = cv2.line(cimg, start_point, end_point, color=(0, 0, 255), thickness=3)
            if i + 2 == len(final_coordinates):
                cimg = cv2.line(cimg, end_point, (final_coordinates[0][0], final_coordinates[0][1]), color=(0, 0, 255),
                                thickness=3)

        cv2.imshow('goodFeaturesToTrack', cimg)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    wb.save('Points.xls')
