from PIL import ImageGrab
from win32api import GetMonitorInfo, MonitorFromPoint
import numpy as np
import types

def main(window, target_image, target_click_coords, target_divide_factor=8, threshold_percentage=0.3, max_results_count=5,
         precise_box_side=15, safe_images=False, verbose=False):

    if type(target_divide_factor) in (list, set, tuple):
        target_divide_factor = (target_divide_factor[0], target_divide_factor[1])
    else:
        target_divide_factor = (target_divide_factor, target_divide_factor)

    window.set_foreground()
    window.maximize_window()
    monitor_info = GetMonitorInfo(MonitorFromPoint((0, 0)))
    target_pos = target_click_coords.coords
    img = ImageGrab.grab()
    ratio = (monitor_info['Monitor'][2] / img.size[0], monitor_info['Monitor'][3] / img.size[1])
    reverse_ratio = img.size[0] / monitor_info['Monitor'][2], img.size[1] / monitor_info['Monitor'][3]
    window_box = window.get_window_rect()
    window_box = (window_box[0] * reverse_ratio[0], window_box[1] * reverse_ratio[1], window_box[2] * reverse_ratio[0],
                  window_box[3] * reverse_ratio[1])
    img = ImageGrab.grab(window_box)
    target = target_image.image
    width_divisor = target.size[0] // target_divide_factor[0]
    height_divisor = target.size[1] // target_divide_factor[1]
    plane_array = np.array(img.resize((img.size[0] // width_divisor, img.size[1] // height_divisor)))
    target_array = np.array(target.resize((target.size[0] // width_divisor, target.size[1] // height_divisor)))



    if verbose:
        print("width divisor", width_divisor)
        print("height divisor", height_divisor)
        print("Screehshot original size", img.size)
        print("Shrinked image array shape", plane_array.shape)
        print("Target original size", target.size)
        print("Shrinked target array shape", target_array.shape)

    def array_to_grayscale(array):
        return (array[:, :, 0] / 255 + array[:, :, 1] / 255 + array[:, :, 2] / 255) / 3

    def array_to_average(array):
        array = array_to_grayscale(array)
        avg = np.average(array)
        return array > avg

    def find_click_pos():
        x = min(target_pos[0], precise_box_side)
        y = min(target_pos[1], precise_box_side)
        return x, y

    def reduce_arrays(first, array_list, side=2):
        def get_average_color(array, side):
            return_array = []
            lst = array.tolist()
            while len(lst) % side != 0:
                lst.append(lst[len(lst) - 1])
            for i in range(len(lst)):
                while len(lst[i]) % side != 0:
                    lst[i].append(lst[i][len(lst[i]) - 1])
            array = np.array(lst)
            for i in range(0, array.shape[0] - side + 1, 2):
                line = []
                for j in range(0, array.shape[1] - side + 1, 2):
                    sample_array = array[i:i + side, j:j + side]
                    avg = np.average(sample_array)
                    line.append(avg)
                return_array.append(line)
            return np.array(return_array)

        def reduce(array, side):
            return_array = []
            lst = array.tolist()
            while len(lst) % side != 0:
                lst.append(lst[len(lst) - 1])
            for i in range(len(lst)):
                while len(lst[i]) % side != 0:
                    lst[i].append(lst[i][len(lst[i]) - 1])
            array = np.array(lst)
            for i in range(0, array.shape[0] - side + 1, 2):
                line = []
                for j in range(0, array.shape[1] - side + 1, 2):
                    sample_array = array[i:i + side, j:j + side]
                    avg = np.average(sample_array)
                    line.append(avg)
                return_array.append(line)
            return np.array(return_array)

        first = get_average_color(first, side)
        for i in range(len(array_list)):
            array_list[i] = get_average_color(array_list[i], side)
        first = reduce(first, side)
        for i in range(len(array_list)):
            array_list[i] = reduce(array_list[i], side)
        return first, array_list, array_list[0].shape

    def deduce_lookup_box(full, small, coords, side):
        if full[0] == small[0] or full[1] == small[1]:
            return (coords[0], coords[1], coords[0], coords[1])
        added_size = full
        if full[0] % side != 0:
            added_size = (full[0] + (side - full[0] % side), full[1])
        if full[1] % side != 0:
            added_size = (added_size[0], full[1] + (side - full[0] % side))
        small_box = deduce_lookup_box((added_size[0] / side, added_size[1] / side), small, coords, side)
        small_box = (
        small_box[0] * side, small_box[1] * side, small_box[2] * side + side - 1, small_box[3] * side + side - 1)
        return small_box

    plane_array = array_to_average(plane_array)
    target_array = array_to_average(target_array)
    if verbose:
        print("plane array shape", plane_array.shape)
        print("target array shape", target_array.shape)

    results = []
    threshold = target_array.size * threshold_percentage
    if verbose:
        print("Threshold is:", threshold, "for array with size", target_array.size)
    for i in range(plane_array.shape[0] - target_array.shape[0]):
        for j in range(plane_array.shape[1] - target_array.shape[1]):
            box = (i, j, i + target_array.shape[0], j + target_array.shape[1])
            difference = target_array ^ plane_array[box[0]:box[2], box[1]:box[3]]
            difference = difference.sum()
            if difference <= threshold:
                results.append((difference, box))
    results.sort()
    results = results[:min(max_results_count, len(results))]
    if verbose:
        print("Got", len(results), "results")
    if len(results) < 1:
        return None
    for entry in results:
        box = (entry[1][0] * height_divisor, entry[1][1] * width_divisor, entry[1][2] * height_divisor,
               entry[1][3] * width_divisor)
        temp_image = img.crop((box[1], box[0], box[3], box[2]))
        if safe_images:
            temp_image.save("results\\result_" + str(box[0]) + "_" + str(box[1]) + "_dif_" + str(entry[0]) + ".png")
    precise_box = (max(0, target_pos[0] - precise_box_side), max(0, target_pos[1] - precise_box_side),
                   min(target_pos[0] + precise_box_side, target.size[0] - 1),
                   min(target_pos[1] + precise_box_side, target.size[1] - 1))

    precise_target = target.crop(precise_box)
    precise_array = np.array(precise_target)
    precise_array = array_to_grayscale(precise_array)
    process_list = []
    image_array = array_to_grayscale(np.array(img))
    for i in range(len(results)):
        result_box = results[i][1]
        process_list.append(image_array[
                            height_divisor * result_box[0]:height_divisor * result_box[2],
                            width_divisor * result_box[1]:width_divisor * result_box[3]])
    precise_array, process_list, small = reduce_arrays(precise_array, process_list)
    best_match = (precise_array.size, 0)
    for k, entry in enumerate(process_list):
        for i in range(len(entry) - precise_array.shape[0] + 1):
            for j in range(len(entry[i]) - precise_array.shape[1] + 1):
                difference = precise_array - entry[i: i + precise_array.shape[0], j: j + precise_array.shape[1]]
                difference = np.absolute(difference).sum()
                if difference < best_match[0]:
                    best_match = (difference, k, i, j)
    if best_match[0] == precise_array.size:
        return None
    best_result_image = best_match[1]
    result_box = results[best_result_image][1]
    result_x = result_box[1] * width_divisor
    result_y = result_box[0] * height_divisor
    full = (height_divisor * result_box[2] - height_divisor * result_box[0],
            width_divisor * result_box[3] - width_divisor * result_box[1])
    coords = (best_match[2], best_match[3])
    lookup_box = deduce_lookup_box(full, small, coords, 2)
    lookup_box = (lookup_box[0], lookup_box[1], min(lookup_box[2], full[0] - 1), min(lookup_box[3], full[1] - 1))
    result_box_start_pos = (height_divisor * result_box[0], width_divisor * result_box[1])
    lookup_box = (lookup_box[0] + result_box_start_pos[0], lookup_box[1] + result_box_start_pos[1],
                  lookup_box[2] + result_box_start_pos[0], lookup_box[3] + result_box_start_pos[1])
    precise_array = np.array(precise_target)
    precise_array = array_to_grayscale(precise_array)
    best_match = (precise_array.size, 0)
    for i in range(lookup_box[0], lookup_box[2] + 1):
        for j in range(lookup_box[1], lookup_box[3] + 1):
            if image_array.shape[0] > i + precise_array.shape[0] and image_array.shape[1] > j + precise_array.shape[1]:
                difference = np.absolute(
                    image_array[i:i + precise_array.shape[0], j:j + precise_array.shape[1]] - precise_array).sum()
                if difference < best_match[0]:
                    best_match = (difference, i, j)
    x, y = find_click_pos()
    x = x + best_match[2]
    y = y + best_match[1]
    window_box = window.get_window_rect()
    x = x + window_box[0]
    y = y + window_box[1]
    x = int(ratio[0] * x)
    y = int(y * ratio[1])
    # win32api.SetCursorPos((x, y))
    from objects import Coordinates
    return Coordinates(x, y)