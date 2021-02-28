import cv2
from xlwt import Workbook
import math
import numpy as np
from projectIM2021_q1 import load_images_from_folder, find_circles


def auto_canny(image, sigma=0.70):
    # compute the median of the single channel pixel intensities
    v = np.median(image)
    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)
    # return the edged image
    return edged


def canny(img_):
    img_ = cv2.bilateralFilter(img_, 5, 30, 150)
    return auto_canny(img_)
    # return cv2.Canny(img_, 80, 200)


def find_7(c_corners, c_hand):
    margin_of_safety = 3
    thump = c_hand[0]
    index_finger_row = c_hand[1][1]
    middle_finger_row = c_hand[2][1]
    ring_finger_row = c_hand[3][1]

    # Get all points by some conditions:
    p_list = []
    for c_ in c_corners:
        x_, y_ = c_.ravel()
        if middle_finger_row - margin_of_safety < y_ < ring_finger_row + margin_of_safety and np.abs(
                ring_finger_row - y_) < np.abs(index_finger_row - y_):
            p_list.append([x_, y_])

    # Get the closet column coordinate to thump column coordinate:
    distance = img.shape[1]
    closet_point = None
    for p in p_list:
        if np.abs(p[0] - thump[0]) < distance:
            distance = np.abs(p[0] - thump[0])
            closet_point = p

    # Distance between ring finger and point 7:
    finger_distance = int(math.dist(closet_point, c_hand[3]))
    return finger_distance, closet_point


def find_4(c_corners, c_hand):
    margin_of_safety = 5
    thump_row = c_hand[0][1]
    thump_col = c_hand[0][0]
    index_finger_row = c_hand[1][1]

    # Get all points by some conditions:
    p_list = []
    for c_ in c_corners:
        x_, y_ = c_.ravel()
        if thump_row - margin_of_safety < y_ < index_finger_row + margin_of_safety and 2 * np.abs(
                index_finger_row - y_) < np.abs(thump_row - y_) and thump_col < x_ and 2.4 * np.abs(
            thump_col - x_) < np.abs(img.shape[1] - x_):
            p_list.append([x_, y_])

    # Get right point:
    if len(p_list) == 0:
        return [0, 0]
    point_4 = p_list.pop()
    for c_ in p_list:
        if c_[0] > point_4[0]:
            point_4 = c_.copy()

    return point_4


def find_1(c_corners, c_hand):
    thump_col = c_hand[0][0]
    ring_finger_row = c_hand[3][1]
    little_finger_col = c_hand[4][0]

    # Get all points by some conditions:
    p_list = []
    for c_ in c_corners:
        x_, y_ = c_.ravel()
        if thump_col < x_ < img.shape[1] * 0.85 and ring_finger_row < y_ and np.abs(img.shape[1] - x_) < np.abs(
                little_finger_col - x_):
            p_list.append([x_, y_])

    # Get the highest point from p_list:
    point_1 = p_list.pop()
    for c_ in p_list:
        if c_[1] < point_1[1]:
            point_1 = c_.copy()

    return point_1


def find_3(c_corners, c_hand, point_4):
    thump_row = c_hand[0][1]

    # Get all points by some conditions:
    p_list = []
    for c_ in c_corners:
        x_, y_ = c_.ravel()
        if point_4[0] < x_ and y_ < point_4[1] and 2 * np.abs(y_ - point_4[1]) < np.abs(y_ - thump_row):
            p_list.append([x_, y_])

    # Get the highest point from p_list:
    point_3 = p_list.pop()
    for c_ in p_list:
        if c_[1] < point_3[1]:
            point_3 = c_.copy()

    return point_3


def find_8(c_corners, c_hand, point_7, point_1, avg_finger_length):
    p_list = []

    # Get all points by some conditions:
    for c_ in c_corners:
        x_, y_ = c_.ravel()
        if point_7[0] < x_ and point_1[1] < y_ and np.abs(img.shape[0] - y_) <= np.abs(point_7[1] - y_) and math.dist(
                c_hand[4], [x_, y_]) < avg_finger_length:
            p_list.append([x_, y_])

    # Get left point:
    point_8 = p_list.pop()
    for c_ in p_list:
        if c_[0] > point_8[0]:
            point_8 = c_.copy()

    return point_8


def find_6(c_corners, c_hand, point_7, avg_finger_thickness_):
    p_list = []
    thump_row = c_hand[0][1]
    middle_finger_row = c_hand[2][1]

    point_6 = [point_7[0], int(point_7[1] - 3 * avg_finger_thickness_)]

    # Find point between little finger to ring finger:
    for c_ in c_corners:
        x_, y_ = c_.ravel()
        if thump_row < y_ < middle_finger_row:
            p_list.append([x_, y_])

    # Get closet point from p_list to point_6:
    closest_point = p_list.pop()
    min_distance = math.dist(closest_point, point_6)
    for c_ in p_list:
        dist = math.dist(c_, point_6)
        if dist < min_distance:
            min_distance = dist
            closest_point = c_

    if math.dist(closest_point, point_6) < 10:
        point_6 = closest_point

    return point_6


def find_2(c_corners, c_hand, point_1, avg_finger_thickness_):
    middle_finger_row = c_hand[2][1]

    # Get all points by some conditions:
    p_list = []
    for c_ in c_corners:
        x_, y_ = c_.ravel()
        if y_ < middle_finger_row and np.abs(x_ - point_1[0]) < avg_finger_thickness_:
            p_list.append([x_, y_])

    # Get right point:
    if len(p_list) == 0:
        return [0, 0]
    point_2 = p_list.pop()
    for c_ in p_list:
        if c_[0] > point_2[0]:
            point_2 = c_.copy()

    return point_2


def find_9(c_corners, c_hand, point_1, point_8, point_4):
    middle_finger_row = c_hand[2][1]

    # Get all points by some conditions:
    p_list = []
    for c_ in c_corners:
        x_, y_ = c_.ravel()
        if point_8[0] < x_ < point_1[0] and middle_finger_row < y_ and 2 * np.abs(x_ - point_4[0]) < np.abs(
                x_ - point_1[0]):
            p_list.append([x_, y_])

    # Get right point:
    if len(p_list) == 0:
        return [0, 0]
    point_9 = p_list.pop()
    for c_ in p_list:
        if c_[0] > point_9[0]:
            point_9 = c_.copy()

    return point_9


def find_5(c_corners, point_4, point_6):
    point_5 = [int((point_4[0] + point_6[0]) * 0.5), int((point_4[1] + point_6[1]) * 0.5)]

    # Get all points by some conditions:
    p_list = []
    for c_ in c_corners:
        x_, y_ = c_.ravel()
        if point_6[0] < x_ < point_4[0]:
            p_list.append([x_, y_])

    # Get closet point from p_list to point_6:
    closest_point = p_list.pop()
    min_distance = math.dist(closest_point, point_5)
    for c_ in p_list:
        dist = math.dist(c_, point_5)
        if dist < min_distance:
            min_distance = dist
            closest_point = c_

    if math.dist(closest_point, point_5) < 10:
        point_5 = closest_point

    return point_5


def find_all_points(c_corners, c_hand, avg_finger_thickness_, sheet_):
    final_points = []

    # Find 7:
    avg_finger_length, point_7 = find_7(c_corners, c_hand)
    sheet_.write(7, 0, '7')
    sheet_.write(7, 1, f'{point_7[0]}')
    sheet_.write(7, 2, f'{point_7[1]}')
    final_points.append(point_7)

    # Find 4:
    point_4 = find_4(c_corners, c_hand)
    sheet_.write(4, 0, '4')
    sheet_.write(4, 1, f'{point_4[0]}')
    sheet_.write(4, 2, f'{point_4[1]}')
    final_points.append(point_4)

    # Find 1:
    point_1 = find_1(c_corners, c_hand)
    sheet_.write(1, 0, '1')
    sheet_.write(1, 1, f'{point_1[0]}')
    sheet_.write(1, 2, f'{point_1[1]}')
    final_points.append(point_1)

    # Find 3:
    point_3 = find_3(c_corners, c_hand, point_4)
    sheet_.write(3, 0, '3')
    sheet_.write(3, 1, f'{point_3[0]}')
    sheet_.write(3, 2, f'{point_3[1]}')
    final_points.append(point_3)

    # Find 8:
    point_8 = find_8(c_corners, c_hand, point_7, point_1, avg_finger_length)
    sheet_.write(8, 0, '8')
    sheet_.write(8, 1, f'{point_8[0]}')
    sheet_.write(8, 2, f'{point_8[1]}')
    final_points.append(point_8)

    # Find 6:
    point_6 = find_6(c_corners, c_hand, point_7, avg_finger_thickness_)
    sheet_.write(6, 0, '6')
    sheet_.write(6, 1, f'{point_6[0]}')
    sheet_.write(6, 2, f'{point_6[1]}')
    final_points.append(point_6)

    # Find 2:
    point_2 = find_2(c_corners, c_hand, point_1, avg_finger_thickness_)
    sheet_.write(2, 0, '2')
    sheet_.write(2, 1, f'{point_2[0]}')
    sheet_.write(2, 2, f'{point_2[1]}')
    final_points.append(point_2)

    # Find 9:
    point_9 = find_9(c_corners, c_hand, point_1, point_8, point_4)
    sheet_.write(9, 0, '9')
    sheet_.write(9, 1, f'{point_9[0]}')
    sheet_.write(9, 2, f'{point_9[1]}')
    final_points.append(point_9)

    # Find 5:
    point_5 = find_5(c_corners, point_4, point_6)
    sheet_.write(5, 0, '5')
    sheet_.write(5, 1, f'{point_5[0]}')
    sheet_.write(5, 2, f'{point_5[1]}')
    final_points.append(point_5)

    return final_points


if __name__ == '__main__':
    # Create csv file:
    wb = Workbook()

    # load all images:
    gray_images, color_images = load_images_from_folder('images')
    gray_images2, color_images2 = load_images_from_folder('other_images')

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
        points = find_circles(canny_img)

        # Get average of fingers thickness:
        avg_finger_thickness = 2 * np.mean(points[:, 2])

        coordinates_thumb_to_little_finger = points[points[:, 1].argsort()]  # Sort points by row
        coordinates_thumb_to_little_finger = np.delete(coordinates_thumb_to_little_finger, 2, 1)  # delete third column

        # Get significant points:
        corners = cv2.goodFeaturesToTrack(canny_img, 1000, 0.01, 8)
        corners = np.int0(corners)
        for i in corners[0:]:
            x, y = i.ravel()
            # cv2.circle(cimg, (x, y), radius=3, color=(255, 0, 0), thickness=4)
        for c in coordinates_thumb_to_little_finger:
            cv2.circle(cimg, (c[0], c[1]), radius=1, color=(0, 0, 255), thickness=4)

        # Find points:
        final_coordinates = find_all_points(corners[0:], coordinates_thumb_to_little_finger, avg_finger_thickness,
                                            sheet)

        for c in final_coordinates:
            cv2.circle(cimg, (c[0], c[1]), radius=3, color=(0, 255, 0), thickness=4)
        cv2.imshow('goodFeaturesToTrack', cimg)
        cv2.imshow('canny', canny_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    wb.save('My images.xls')

    wb = Workbook()
    # Iterate other images:
    for index, img in enumerate(gray_images2):
        # add_sheet is used to create sheet.
        sheet = wb.add_sheet(f'image {index + 1}')
        sheet.write(0, 0, 'point')
        sheet.write(0, 1, 'X')
        sheet.write(0, 2, 'Y')

        # Canny:
        canny_img = canny(img)
        cimg = color_images[index]

        # Get fingers from projectIM2021_q1:
        points = find_circles(canny_img)

        # Get average of fingers thickness:
        avg_finger_thickness = 2 * np.mean(points[:, 2])

        coordinates_thumb_to_little_finger = points[points[:, 1].argsort()]  # Sort points by row
        coordinates_thumb_to_little_finger = np.delete(coordinates_thumb_to_little_finger, 2, 1)  # delete third column

        # Get significant points:
        corners = cv2.goodFeaturesToTrack(canny_img, 1000, 0.01, 8)
        corners = np.int0(corners)
        for i in corners[0:]:
            x, y = i.ravel()
            # cv2.circle(cimg, (x, y), radius=3, color=(255, 0, 0), thickness=4)
        for c in coordinates_thumb_to_little_finger:
            cv2.circle(cimg, (c[0], c[1]), radius=1, color=(0, 0, 255), thickness=4)

        # Find points:
        final_coordinates = find_all_points(corners[0:], coordinates_thumb_to_little_finger, avg_finger_thickness,
                                            sheet)

        for c in final_coordinates:
            cv2.circle(cimg, (c[0], c[1]), radius=3, color=(0, 255, 0), thickness=4)
        cv2.imshow('goodFeaturesToTrack', cimg)
        cv2.imshow('canny', canny_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    wb.save('Other images.xls')
