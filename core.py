import system_tools
import keyboard_input
import time
import objects
import window_tools
from input_tools import move_mouse, paste_to_clipboard
import window_position_finder
import find_image_position_on_window

system_tools.call("C:\\Program Files\\Mozilla Firefox\\firefox.exe")
time.sleep(2)
keyboard_input.type_buttons_simultaneously((
    keyboard_input.VK_LCONTROL,
    keyboard_input.VK_T
))

time.sleep(1)

window = window_tools.get_window_by_name("firefox")
coordinates = window_position_finder.main(window,
                                          objects.Picture(file_path="D:\\Study Projects\\untitled\\mail_steps\\address line.png"),
                                          objects.Coordinates(46,19), safe_images=True, verbose=True, threshold_percentage=0.3, target_divide_factor=(13, 8))

move_mouse(coordinates)
keyboard_input.left_mouse_click()

paste_to_clipboard("gmail.com")
keyboard_input.type_buttons_simultaneously((
    keyboard_input.VK_LCONTROL,
    keyboard_input.VK_V
))
keyboard_input.type_button(keyboard_input.VK_ENTER)
time.sleep(2)

coordinates = find_image_position_on_window.main(window, objects.Picture(file_path="D:\\Study Projects\\untitled\\mail_steps\\gmail_loading.png"), threshold_percentage=0.1)
while coordinates is not None:
    print("Still loading")
    time.sleep(1)
    coordinates = find_image_position_on_window.main(window, objects.Picture(file_path="D:\\Study Projects\\untitled\\mail_steps\\gmail_loading.png"), threshold_percentage=0.1)

coordinates = window_position_finder.main(window, objects.Picture(file_path="D:\\Study Projects\\untitled\\mail_steps\\Write_button.png"), objects.Coordinates(105,116))
move_mouse(coordinates)
keyboard_input.left_mouse_click()

paste_to_clipboard("deyakohail14@gmail.com")
keyboard_input.type_buttons_simultaneously((
    keyboard_input.VK_LCONTROL,
    keyboard_input.VK_V
))

coordinates = window_position_finder.main(window, objects.Picture(file_path="D:\\Study Projects\\untitled\\mail_steps\\mail_body.png"), objects.Coordinates(320,300))
move_mouse(coordinates)
keyboard_input.left_mouse_click()

paste_to_clipboard("Here is some text sent by my python script." + str(time.time()))

keyboard_input.type_buttons_simultaneously((
    keyboard_input.VK_LCONTROL,
    keyboard_input.VK_V
))

coordinates = window_position_finder.main(window, objects.Picture(file_path="D:\\Study Projects\\untitled\\mail_steps\\mail_body.png"), objects.Coordinates(80,620))
move_mouse(coordinates)