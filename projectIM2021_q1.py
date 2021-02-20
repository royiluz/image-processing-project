import cv2
import os
import matplotlib.pyplot as plt


# Load all images from folder by folder's name
def load_images_from_folder(folder):
    images_ = []
    for filename in os.listdir(folder):
        img_ = cv2.imread(os.path.join(folder, filename), cv2.IMREAD_GRAYSCALE)
        if img_ is not None:
            images_.append(img_)
    return images_


if __name__ == '__main__':
    # load all images:
    images = load_images_from_folder('images')
    for img in images:
        plt.imshow(img, cmap='gray')
        plt.axis('off')
        plt.show()
