from rpi5_ws2812.ws2812 import Color, WS2812SpiDriver
import time
import colorsys
import socket
import threading

led_nums = 220
k = 1
current_id = 0

pinpong_idx = 0
pinpong_k = 1

num_leds = 10
g_colors = [Color(0, 0, 0) for _ in range(num_leds)]

# define IPv4 socket object
sv = socket.socket(socket.AF_INET)
sv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
rasbpi_ip = "192.168.0.156"
rasbpi_port = 5000
sv.bind((rasbpi_ip, rasbpi_port))
sv.listen()

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

def reset():
    strip.clear()
    strip.show()

def start_led(delay = 0):
    strip.show()
    # strip.clear()
    if delay > 0:
        time.sleep(delay)
        
# test
def test_all_pattern():
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
        for led_i in range(48):
            strip.set_pixel_color(led_i, color)
        start_led(1)
        # strip.set_pixel_color(2, Color(255, 255, 255))
    reset()
    start_led(1)


# turn on the LED of the corresponding ID
def set_led(id, status="null", color = Color(255, 0, 0)):
    # size of a plate
    # print(str(id) + " status: " + status)
    length = 6
    start = id * length
    
    colors = [
            Color(0, 0, 0),
            Color(255, 0, 0)
        ]
    
    set_color = colors[0]
    
    """
    if status == "entry":
        set_color = color
    """
    set_color = color

    for i in range(length):
        strip.set_pixel_color(start + i, set_color)
        
    # start_led()

# set fade in out
def set_fade_in_out(id, status="null", color = Color(255, 0, 0), steps=50, delay=0.1):
    if status == "entry":
        g_colors[id - 1] = color
        r_target, g_target, b_target = g_colors[id - 1]

        # fade in
        for step in range(steps + 1):
            r = int(r_target * (step / steps))
            g = int(g_target * (step / steps))
            b = int(b_target * (step / steps))

            set_led(id, status, Color(r, g, b))
            start_led(delay)
    else:
        # fade out
        r_target, g_target, b_target = g_colors[id - 1]
        for step in range(steps + 1):
            r = int(r_target * (1 - (step / steps)))
            g = int(g_target * (1 - (step / steps)))
            b = int(b_target * (1 - (step / steps)))

            set_led(id, status, Color(r, g, b))
            start_led(delay)

# pinpong pattern
def pinpong():
    global pinpong_idx
    global pinpong_k
    
    pinpong_idx += pinpong_k
    
    if (pinpong_idx == 216) or (pinpong_idx == 0):
        pinpong_k *= -1
        
    strip.set_pixel_color(pinpong_idx, Color(255, 0, 0))
    strip.set_pixel_color(pinpong_idx + 1, Color(255, 0, 0))
    strip.set_pixel_color(pinpong_idx + 2, Color(255, 0, 0))
    strip.set_pixel_color(pinpong_idx + 3, Color(255, 0, 0))
    
    start_led()

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

if __name__ == "__main__":
    
    # Initialize the WS2812 strip with 100 leds and SPI channel 0, CE0
    strip = WS2812SpiDriver(spi_bus=0, spi_device=0, led_count=led_nums).get_strip()
    
    #reset()

    # generate_gradient()
    
    while True:
        strip.show()
        
        # test_all_pattern()
        
        # pinpong()
    
        
