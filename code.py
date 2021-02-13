import ipaddress
import ssl
import wifi
import socketpool
import adafruit_requests
import time
from adafruit_magtag.magtag import MagTag

print('Start')
magtag = MagTag()

def display_text(message):
    global magtag
    magtag.add_text(
        text_position=(
            25,
            (magtag.graphics.display.height // 2) - 1,
        ),
        text_scale=2,
    )
    magtag.set_text(message)

def display_time(city):
    if city not in city_names:
        city = city_names[0]
    timezone = city_timezones[city]

    display_text("Fetching: {}\n{}".format(city, timezone))

    TIME_URL = 'https://api.ipgeolocation.io/timezone?apiKey={}&tz={}'.format(secrets['ipgl_key'], timezone)

    response = requests.get(TIME_URL)
    if 'message' in response.json():
        display_text(response.json()['message'])
    else:
        tz_info = response.json()
        tz_offset = tz_info["timezone_offset"] if tz_info["timezone_offset"] <= 0 else "+{}".format(tz_info["timezone_offset"])

        time_to_display = "{} ({})\n{} {}\n{}".format(city, tz_offset, tz_info["time_24"], tz_info["date"], tz_info["timezone"])
        display_text(time_to_display)



    
# Initialise Wifi
display_text("Initialising WiFi ...")
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise
    
wifi.radio.connect(secrets["ssid"], secrets["password"])
pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

display_text("WiFi: {}".format(secrets['ssid']))

button_colors = ((255, 0, 0), (255, 150, 0), (0, 255, 255), (180, 0, 255))
button_tones = (1047, 1318, 1568, 2093)

# These are just timezones I'm interested in
# I've layed them out East to West to match the cycling below
cities = [
    ("Seattle",      "America/Los_Angeles"),
    ("Tucson",       "America/Phoenix"),
    ("Saskatoon",    "Canada/Saskatchewan"),
    ("Edinburgh",    "Europe/Dublin"),
    ("Amsterdam",    "Europe/Amsterdam"),
    ("Kuwait",       "Asia/Kuwait"),
    ("Hyderabad",    "Asia/Kolkata"),
    ("Perth",        "Australia/Perth"),
    ("Melbourne",    "Australia/Victoria"),
    ("Sydney",       "Australia/Sydney")
]

home_city = 'Edinburgh'
city_names = [c[0] for c in cities]
city_timezones = { c[0]: c[1] for c in cities }

# Default city is your home city
current_city_idx = city_names.index(home_city)
display_time(city_names[current_city_idx])

# The main loop
while True:
    for i, b in enumerate(magtag.peripherals.buttons):
        if not b.value:
            # print("Button %c pressed" % chr((ord("A") + i)))
            magtag.peripherals.neopixel_disable = False
            magtag.peripherals.neopixels.fill(button_colors[i])
            
            # magtag.peripherals.play_tone(button_tones[i], 0.25)
            
            # First button - cycle up through the list (e.g. East to West depending on the list)
            if i == 0:
                current_city_idx = current_city_idx - 1 if current_city_idx > 0 else (len(city_names) - 1)
                display_time(city_names[current_city_idx])
            # First button - cycle down through the list of cities 
            if i == 1:
                current_city_idx = current_city_idx + 1 if current_city_idx < (len(city_names) -1) else 0
                display_time(city_names[current_city_idx])
                
            
            break
    else:
        magtag.peripherals.neopixel_disable = True
    time.sleep(0.01)