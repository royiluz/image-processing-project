import cv2
import os
import numpy as np


# Load all images from folder by folder's name
def load_images_from_folder(folder):
    gray_images_, color_images_ = [], []
    for filename in os.listdir(folder):
        img_ = cv2.imread(os.path.join(folder, filename), cv2.IMREAD_GRAYSCALE)
        if img_ is not None:
            gray_images_.append(img_)
            color_images_.append(cv2.cvtColor(img_, cv2.COLOR_GRAY2BGR))
    return gray_images_, color_images_


def auto_canny(image, sigma=0.60):
    v = np.median(image)

    # Apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)

    return edged


def canny(img_):
    return auto_canny(img_)
    # return cv2.Canny(img_, 80, 200)


def find_circles(img_):
    right_quarter_col = (img_.shape[1] / 4) * 3
    circles_ = cv2.HoughCircles(img_, cv2.HOUGH_GRADIENT, 1, 40,
                                param1=50, param2=12, minRadius=5, maxRadius=25)
    # Cast to int:
    circles_ = np.uint16(np.around(circles_))[0]

    indices_to_remove = []
    # Remove circles from the right quarter and circle in the middle of the finger:
    for ind, c in enumerate(circles_):
        col, row, radios = c[0], c[1], c[2]
        # circles from the right quarter
        if col > right_quarter_col:
            indices_to_remove.append(ind)
            continue

        # circle in the middle of the finger:
        left_coordinates_from_center = [img_[row, col - i_] for i_ in range(int(radios * 1.5)) if col - i_ > 0]
        if 255 not in left_coordinates_from_center:
            indices_to_remove.append(ind)

    # Delete un-relevant circles:
    circles_ = np.delete(circles_, indices_to_remove, 0)

    return circles_


if __name__ == '__main__':
    # load all images:
    gray_images, color_images = load_images_from_folder('images')
    gray_images2, color_images2 = load_images_from_folder('images2')

    # My images:
    for index, img in enumerate(gray_images):
        # img = cv2.bilateralFilter(img, 5, 30, 50)
        canny_img = canny(img)
        circles = find_circles(canny_img)
        if len(circles) != 0:
            cimg = color_images[index]
            for c in circles:
                # draw the outer circle
                # cv2.circle(cimg, (c[0], c[1]), c[2], (0, 255, 0), 2)

                # draw the center of the circle
                cv2.circle(cimg, (c[0], c[1]), radius=1, color=(0, 0, 255), thickness=4)

            # Show image after canny and image with circles
            cv2.imshow('detected top finger', cimg)
            # cv2.imshow('canny', canny_img)
            # cv2.imshow('bilateral', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    # Other images:
    for index, img in enumerate(gray_images2):
        # img = cv2.bilateralFilter(img, 5, 30, 50)
        canny_img = canny(img)
        circles = find_circles(canny_img)
        if len(circles) != 0:
            cimg = color_images2[index]
            for i in circles:
                # draw the outer circle
                # cv2.circle(cimg, (i[0], i[1]), i[2], (0, 255, 0), 2)
                # draw the center of the circle
                cv2.circle(cimg, (i[0], i[1]), radius=1, color=(0, 0, 255), thickness=4)

            # Show image after canny and image with circles
            cv2.imshow('detected circles', cimg)
            # cv2.imshow('canny', canny_img)
            # cv2.imshow('canny', canny_img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
