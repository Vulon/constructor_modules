from PIL import ImageGrab
from win32api import GetMonitorInfo, MonitorFromPoint
import numpy as np

def main(window, target_image, target_divide_factor=8, threshold_percentage=0.15):
    window.set_foreground()
    window.maximize_window()
    monitor_info = GetMonitorInfo(MonitorFromPoint((0, 0)))
    img = ImageGrab.grab()
    ratio = (monitor_info['Monitor'][2] / img.size[0], monitor_info['Monitor'][3] / img.size[1])
    reverse_ratio = img.size[0] / monitor_info['Monitor'][2], img.size[1] / monitor_info['Monitor'][3]
    window_box = window.get_window_rect()
    window_box = (window_box[0] * reverse_ratio[0], window_box[1] * reverse_ratio[1], window_box[2] * reverse_ratio[0],
                  window_box[3] * reverse_ratio[1])
    img = ImageGrab.grab(window_box)
    target = target_image.image
    width_divisor = target.size[0] // target_divide_factor
    height_divisor = target.size[1] // target_divide_factor
    plane_array = np.array(img.resize((img.size[0] // width_divisor, img.size[1] // height_divisor)))
    target_array = np.array(target.resize((target.size[0] // width_divisor, target.size[1] // height_divisor)))

    def array_to_grayscale(array):
        return (array[:, :, 0] / 255 + array[:, :, 1] / 255 + array[:, :, 2] / 255) / 3

    def array_to_average(array):
        array = array_to_grayscale(array)
        avg = np.average(array)
        return array > avg

    plane_array = array_to_average(plane_array)
    target_array = array_to_average(target_array)

    results = []
    threshold = target_array.size * threshold_percentage
    for i in range(plane_array.shape[0] - target_array.shape[0]):
        for j in range(plane_array.shape[1] - target_array.shape[1]):
            box = (i, j, i + target_array.shape[0], j + target_array.shape[1])
            difference = target_array ^ plane_array[box[0]:box[2], box[1]:box[3]]
            difference = difference.sum()
            if difference <= threshold:
                results.append((difference, box))
    results.sort()
    if len(results) == 0:
        return None

    box = results[0][1]
    del results
    box = (box[0] * height_divisor, box[1] * width_divisor, box[2] * height_divisor, box[3] * width_divisor)
    image_array = array_to_grayscale(np.array(img))
    target_array = array_to_grayscale(np.array(target))
    best_match = (target_array.size, (0,0))
    for i in range(box[0], box[0] + height_divisor):
        for j in range(box[1], box[1] + width_divisor):
            array_box = (i, j, i + target_array.shape[0], j + target_array.shape[1])
            difference = np.absolute(image_array[array_box[0]:array_box[2],array_box[1]:array_box[3]] - target_array).sum()
            if difference < best_match[0]:
                best_match = (difference, array_box)
    from objects import Coordinates
    return Coordinates(array_box[1], array_box[0])

