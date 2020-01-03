from PIL import Image
import numpy as np
from PIL import ImageGrab
import win32gui
import win32api
import win32con


def get_window_handle(name):
    winlist = []

    def enum_cb(hwnd, results):
        if len(win32gui.GetWindowText(hwnd)) > 0:
            winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

    win32gui.EnumWindows(enum_cb, [])
    print(winlist)

    firefox = [(hwnd, title) for hwnd, title in winlist if name.lower() in title.lower()]
    return firefox[0][0]


target_dir = "D:\\temp\\Images\\Link.png"
target_divide_factor = 8
threshold_percentage = 0.15
max_results_count = 5
precise_box_side = 15
target_pos = (160, 140)


hwnd = get_window_handle("firefox")
win32gui.SetForegroundWindow(hwnd)
win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)


# if win32gui.IsIconic(hwnd):
#     win32gui.ShowWindow(hwnd, 3)

img = ImageGrab.grab()
img.save("screenshot.png")

monitor_info = win32api.GetMonitorInfo(win32api.MonitorFromPoint((0,0)))
ratio = (monitor_info['Monitor'][2] / img.size[0],  monitor_info['Monitor'][3] / img.size[1] )
reverse_ratio = img.size[0] / monitor_info['Monitor'][2],  img.size[1]/ monitor_info['Monitor'][3]

window_box = win32gui.GetWindowRect(hwnd)
window_box = (window_box[0] * reverse_ratio[0], window_box[1] * reverse_ratio[1], window_box[2] * reverse_ratio[0], window_box[3] * reverse_ratio[1])
print("Client Rect: ", win32gui.GetClientRect(hwnd))
print("Window rect: ", win32gui.GetWindowRect(hwnd))
print("Restored window rect: ", window_box)
img = ImageGrab.grab(window_box)
img.save("Exact window.png")


# target = Image.open("D:\\temp\\Images\\search button.png")
target_original = Image.open(target_dir)
target = Image.open(target_dir)


print("Screenshot size: ", img.size)
print("Target size: ", target.size)

width_divisor = target.size[0] // target_divide_factor
height_divisor = target.size[1] // target_divide_factor

print("Divisors: ", width_divisor, height_divisor)


plane = img.resize((img.size[0] // width_divisor, img.size[1] // height_divisor))
target = target.resize((target.size[0] // width_divisor, target.size[1] // height_divisor))

print("New plane size: ", plane.size)
print("New target size: ", target.size)
plane.save("Plane.png")
target.save("Target.png")
plane_array = np.array(plane)
target_array = np.array(target)

def array_to_grayscale(array):
    return (array[:, :, 0] / 255 + array[:, :, 1] / 255 + array[:, :, 2] / 255) / 3
def array_to_average(array):
    array = array_to_grayscale(array)
    avg = np.average(array)
    return array > avg

plane_array = array_to_average(plane_array)


target_array = array_to_average(target_array)

print("Plane array shape: ", plane_array.shape)
print("Target array shape: ", target_array.shape)

results = []
threshold = target_array.size * threshold_percentage
total = 0

for i in range(plane_array.shape[0] - target_array.shape[0]):
    for j in range(plane_array.shape[1] - target_array.shape[1]):
        box = (i, j, i + target_array.shape[0], j + target_array.shape[1])
        difference = target_array ^ plane_array[box[0]:box[2], box[1]:box[3]]
        difference = difference.sum()
        total += 1
        if difference <= threshold:
            results.append((difference, box))
print("Total ", total, " results: ", len(results))

results.sort()

results = results[:min(max_results_count, len(results))]
# array_list = []
for entry in results:
    box = (entry[1][0] * height_divisor, entry[1][1] * width_divisor, entry[1][2] * height_divisor, entry[1][3] * width_divisor)
    temp_image = img.crop((box[1],box[0], box[3], box[2]))
    temp_image.save("results\\result_" + str(box[0]) + "_" + str(box[1]) + "_dif_" + str(entry[0]) + ".png")
    # arr = np.array(temp_image)
    # arr = array_to_grayscale(arr)
    # array_list.append(arr)

print("Target pos:", target_pos)
print("precise box side: ", precise_box_side)
print("Target size: ", target_original.size)

precise_box = (max(0, target_pos[0] - precise_box_side), max(0, target_pos[1] - precise_box_side),
               min(target_pos[0] + precise_box_side, target_original.size[0] - 1), min(target_pos[1] + precise_box_side, target_original.size[1] - 1))
print("Precise box: ", precise_box)
def find_click_pos():
    x = min(target_pos[0], precise_box_side)
    y = min(target_pos[1], precise_box_side)
    return x, y

precise_target = target_original.crop(precise_box)
precise_target.save("Precise.png")
precise_array = np.array(precise_target)
precise_array = array_to_grayscale(precise_array)

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
    print("Before average: ", first.shape, array_list[0].shape)

    first = get_average_color(first, side)
    for i in range(len(array_list)):
        array_list[i] = get_average_color(array_list[i], side)
    print("After average: ", first.shape, array_list[0].shape)
    flag = True
    first = reduce(first, side)
    for i in range(len(array_list)):
        array_list[i] = reduce(array_list[i], side)

    # while first.shape[0] > side * 2 and first.shape[1] > side * 2 and flag:
    #     first = reduce(first, side)
    #     shrink_ratio = shrink_ratio * side
    #     for i in range(len(array_list)):
    #         array_list[i] = reduce(array_list[i], side)
    #         if array_list[i].shape[0] <= side * 2 or array_list[i].shape[1] <= side * 2:
    #             print("Broke at ", i)
    #             flag = False
    #     print("Reduce cycle: ", first.shape, array_list[0].shape)
    return first, array_list, array_list[0].shape

process_list = []
print("Results ", results)
image_array = np.array(img)
image_array = array_to_grayscale(image_array)
print("Image array shape: ", image_array.shape)
for i in range(len(results)):
    result_box = results[i][1]
    process_list.append(image_array[
                        height_divisor * result_box[0]:height_divisor * result_box[2],
                        width_divisor * result_box[1]:width_divisor * result_box[3]])
    print("Result box", result_box)
    print("New array shape: ", process_list[len(process_list) - 1].shape)

precise_array, process_list, small= reduce_arrays(precise_array, process_list)

print("Reduced size: ", precise_array.shape, " list: ", process_list[0].shape)

best_match = (precise_array.size, 0)
for k, entry in enumerate(process_list):
    for i in range(len(entry) - precise_array.shape[0] + 1):
        for j in range(len(entry[i]) - precise_array.shape[1] + 1):
            difference = precise_array - entry[i : i + precise_array.shape[0], j: j + precise_array.shape[1]]
            difference = np.absolute(difference).sum()
            if difference < best_match[0]:
                best_match = (difference, k, i, j)


def deduce_lookup_box(full, small, coords, side):
    print("Deduce lookup box", full, small, coords, side)
    if full[0] == small[0] or full[1] == small[1]:
        return (coords[0], coords[1], coords[0], coords[1])
    added_size = full
    if full[0] % side != 0:
        added_size = (full[0] + (side - full[0] % side), full[1])
    if full[1] % side != 0:
        added_size = (added_size[0], full[1] + (side - full[0] % side))
    small_box = deduce_lookup_box((added_size[0] / side, added_size[1] / side), small, coords, side)
    small_box = (small_box[0] * side, small_box[1] * side, small_box[2] * side + side - 1, small_box[3] * side + side - 1)
    return small_box



print("Best match: ", best_match)
best_result_image = best_match[1]
result_box = results[best_result_image][1]
print("Result box:", result_box)

result_x = result_box[1] * width_divisor
result_y = result_box[0] * height_divisor
print("Result x, y", result_x, result_y)
full = (height_divisor * result_box[2] - height_divisor * result_box[0], width_divisor * result_box[3] - width_divisor * result_box[1])
coords = (best_match[2], best_match[3])
lookup_box = deduce_lookup_box(full, small, coords, 2)
lookup_box = (lookup_box[0], lookup_box[1], min(lookup_box[2], full[0] - 1), min(lookup_box[3], full[1] - 1) )
print("Bounded lookup box", lookup_box)

result_box_start_pos = (height_divisor * result_box[0], width_divisor * result_box[1])
lookup_box = (lookup_box[0] + result_box_start_pos[0], lookup_box[1] + result_box_start_pos[1],
              lookup_box[2] + result_box_start_pos[0], lookup_box[3] + result_box_start_pos[1])
print("Global coords lookup box", lookup_box)

precise_array = np.array(precise_target)
precise_array = array_to_grayscale(precise_array)

best_match = (precise_array.size, 0)
for i in range(lookup_box[0], lookup_box[2] + 1):
    for j in range(lookup_box[1], lookup_box[3] + 1):
        if image_array.shape[0] > i + precise_array.shape[0] and image_array.shape[1] > j + precise_array.shape[1]:
            difference = np.absolute(image_array[i:i + precise_array.shape[0], j:j + precise_array.shape[1]] - precise_array).sum()
            if difference < best_match[0]:
                best_match = (difference, i, j)

print("Precise best match", best_match)

x, y = find_click_pos()
print("Found click pos: ", find_click_pos())
x = x + best_match[2]
y = y + best_match[1]
print("Coords relative to window", x, y)
window_box = win32gui.GetWindowRect(hwnd)
x = x + window_box[0]
y = y + window_box[1]
print("Final image coords:", x, y)
x = int(ratio[0] * x)
y = int(y * ratio[1])

print("Screen coords", x, y)


win32api.SetCursorPos((x, y))