from rpi5_ws2812.ws2812 import Color, WS2812SpiDriver
import time
import colorsys
import socket
import threading
import random

# shibayama
name_led_nums = 300
back_led_nums = 300

k = 1
current_id = 0

pinpong_idx = 14
pinpong_k = 1

num_leds = 10
g_colors = [Color(0, 0, 0) for _ in range(num_leds)]

# define IPv4 socket object
sv = socket.socket(socket.AF_INET)
sv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
rasbpi_ip = "192.168.0.10"
rasbpi_port = 5000
sv.bind((rasbpi_ip, rasbpi_port))
sv.listen()


class ColorWheel:
    def __init__(self, step=0.05):
        self.hue = 0.0
        self.step = step
        
    def next_color(self):
        r, g, b = colorsys.hsv_to_rgb(self.hue, 1, 1)
        self.hue = (self.hue + self.step) % 1.0
        return Color(r * 255, g * 255, b * 255)

def handle_accept(server_socket):
    while True:
        client, addr = sv.accept()
        data = client.recv(1024)
        
        if len(data) == 0:
            break
        
        data = data.decode("utf-8")
        # print(data)
        
        idx_str, status, str_r, str_g, str_b = data.strip().split(',')
        idx = int(idx_str)
        
        set_color = Color(int(str_r), int(str_g), int(str_b))

        print("id: " + str(idx) + " status: " + status)
        client.close()

        # set_led(idx, status, set_color)
        set_fade_in_out(idx, status, set_color)



# wait for "accept" in thread
accept_thread = threading.Thread(target=handle_accept, args=(sv,))
accept_thread.daemon = True
accept_thread.start()

g_wheel = ColorWheel(step=0.01)

def reset(strip):
    strip.clear()
    strip.show()

def start_led(strip, delay = 0):
    strip.show()
    # strip.clear()
    if delay > 0:
        time.sleep(delay)
        
# test
def test_all_pattern(strip, isMain = 0):
    test_colors = [
            Color(255, 0, 0),
            Color(0, 255, 0),
            Color(0, 0, 255),
            Color(0, 255, 255),
            Color(255, 255, 255)
        ]
    # one color change -> red, gree, blue, yellow, white
    for color in test_colors:
        print(color)
        # strip.set_all_pixels(color)
        
        if (isMain):
            for led_i in range(35):
                strip.set_pixel_color(15 + led_i, color)
        else:
            strip.set_all_pixels(color)
        
        start_led(strip, 1)
        
        # strip.set_pixel_color(2, Color(255, 255, 255))
    
    reset(strip)
    
    start_led(strip, 1)

def test_all_gradiation(strip):
    gradient_color = g_wheel.next_color()
    
    for led_i in range(35):
        strip.set_pixel_color(5 + led_i, gradient_color)
        
    # 2 lines test
#     for i in range(5):
#         strip_name.set_pixel_color(165 + i, gradient_color)
        # strip_name.set_pixel_color(199 + i, gradient_color)
    
    start_led(strip, 0.05)

def test_random(strip, start_idx = 0, end_idx = 1):
    for i in range(end_idx):
        rand_r = random.randint(0, 255)
        rand_g = random.randint(0, 255)
        rand_b = random.randint(0, 255)
        rand_color = Color(rand_r, rand_g, rand_b)
        
        print(rand_color)
        
        set_led(strip, start_idx + i, "null", rand_color)
        
        rand_r = random.randint(0, 255)
        rand_g = random.randint(0, 255)
        rand_b = random.randint(0, 255)
        rand_color = Color(rand_r, rand_g, rand_b)
        
        set_led(strip, 33, "null", rand_color)
    
    
    start_led(strip, 1)

# turn on the LED of the corresponding ID
def set_led(strip, id, status="null", color = Color(255, 0, 0)):
    # size of a plate
    # print(str(id) + " status: " + status)
    length = 5
    start = id * length
    
    colors = [
            Color(0, 0, 0),
            Color(255, 0, 0)
        ]
    
    set_color = colors[0]
    
    print(color)
    
    """
    if status == "entry":
        set_color = color
    """
    set_color = color

    for i in range(length):
        strip.set_pixel_color(5 + start + i, set_color)
        
    # start_led()

# set fade in out
def set_fade_in_out(id, status="null", color = Color(255, 0, 0), steps=5, delay=0.01):
    if status == "entry":
        g_colors[id - 1] = color
        r_target, g_target, b_target = g_colors[id - 1]

        # set_led(id, status, Color(r_target, g_target, b_target))
        # fade in
        
        for step in range(steps + 1):
            r = int(r_target * (step / steps))
            g = int(g_target * (step / steps))
            b = int(b_target * (step / steps))

            set_led(strip_name, id, status, Color(r, g, b))
            start_led(strip_name, delay)
        
    else:
        # fade out
        
        r_target, g_target, b_target = g_colors[id - 1]
        for step in range(steps + 1):
            r = int(r_target * (1 - (step / steps)))
            g = int(g_target * (1 - (step / steps)))
            b = int(b_target * (1 - (step / steps)))

            set_led(strip_name, id, status, Color(r, g, b))
            start_led(strip_name, delay)
        
        # set_led(id, status, Color(0, 0, 0))

# pinpong pattern
def pinpong(strip):
    global pinpong_idx
    global pinpong_k
    pinpong_color = Color(0, 255, 255)
    
    pinpong_idx += pinpong_k
    
    strip.clear()
    
    pinpong_color = Color(255, 255, 255) #g_wheel.next_color() #Color(100, 255, 100)
    
    if (pinpong_idx == 299) or (pinpong_idx == 0):
        pinpong_k *= -1
        
    strip.set_pixel_color(pinpong_idx, pinpong_color)
    #strip.set_pixel_color(pinpong_idx + 1, pinpong_color)
    #strip.set_pixel_color(pinpong_idx + 2, pinpong_color)
    #strip.set_pixel_color(pinpong_idx + 3, pinpong_color)
    
    start_led(strip)

def interpolate_rgb(start, end, steps):
    gradient = []
    for i in range(steps):
        r = int(start[0] + (end[0] - start[0]) * i / steps)
        g = int(start[1] + (end[1] - start[1]) * i / steps)
        b = int(start[2] + (end[2] - start[2]) * i / steps)
        gradient.append(Color(r, g, b))
    return gradient

def generate_gradient():
    steps_per_transition = 20
    colors = [
        (255, 0, 0),
        (255, 0, 255),
        (0, 0, 255),
        (0, 255, 0),
    ]
    gradient = []
    for i in range(len(colors) - 1):
        start = colors[i]
        end = colors[i + 1]
        gradient += interpolate_rgb(start, end, steps_per_transition)
    
    for i, color in enumerate(gradient):
        strip.set_pixel_color(i, color)
        
def dual_light(main_strip, sub_strip):
    # for i in range(5):
        # strip_name.set_pixel_color(15 + i, Color(0, 255, 255))
            
    for i in range(10):
        strip_back.set_pixel_color(i, Color(0, 200, 200))

if __name__ == "__main__":
    
    # Initialize the WS2812 strip with 100 leds and SPI channel 0, CE0
    strip_name = WS2812SpiDriver(spi_bus=0, spi_device=0, led_count=name_led_nums).get_strip()
    strip_back = WS2812SpiDriver(spi_bus=1, spi_device=0, led_count=back_led_nums).get_strip()
    
    reset(strip_name)
    reset(strip_back)

    # generate_gradient()
    # set_led(17, "entry", Color(0, 255, 255))
    # set_led(9, "entry", Color(0, 255, 255))
    
    while True:
        # strip_name.set_pixel_color(5, Color(240, 240, 180))
        # strip_back.set_pixel_color(5, Color(240, 0, 0))
        strip_name.show()
        strip_back.show()
        
        # dual_light(strip_name, strip_back)

        # 2 lines test
#        for i in range(35):
#             strip_name.set_pixel_color(5 + i, Color(255, 255, 255))            
            
        cherry = Color(200, 40, 50);
        leaves = Color(140, 200, 180);
        white = Color(255, 255, 255);
        
        for i in range(0):
#             strip_back.set_pixel_color(5 + i, white);
            strip_name.set_pixel_color(i, white);
        strip_name.show();
        time.sleep(1000);
        
#         for i in range(5):
#             strip_back.set_pixel_color(25 + i, cherry);

        # strip_name.set_pixel_color(3, Color(255, 0, 0))
        # strip_back.set_pixel_color(3, Color(255, 0, 0))
        
#         test_all_pattern(strip_back, 0)
#         test_all_pattern(strip_name, 0)
        # strip_name.set_all_pixels(Color(0, 255, 200))
#         test_all_pattern(strip_back, 0)
      #  test_all_gradiation(strip_name)

        # shakou
        #test_all_gradiation(strip_back)

        # test_random(strip_name, 3, 8)
        
        # 2 lines test
         # test_random(strip_name, 40, 1^ ^pinpong(strip_back)
#         pinpong(strip_name)