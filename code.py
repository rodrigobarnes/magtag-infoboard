import ipaddress
import ssl
import wifi
import socketpool
import adafruit_requests
import terminalio
import time
import displayio
import board

from adafruit_display_text import label
from adafruit_magtag.magtag import MagTag
from secrets import secrets

# ---------------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------------

# These are just timezones I'm interested in
# I've layed them out East to West to match the cycling below
cities = [
    ("Seattle",      "America/Los_Angeles"),
    ("Tucson",       "America/Phoenix"),
    # ("Saskatoon",    "Canada/Saskatchewan"),
    ("Edinburgh",    "Europe/Dublin"),
    ("Amsterdam",    "Europe/Amsterdam"),
    # ("Kuwait",       "Asia/Kuwait"),
    ("Hyderabad",    "Asia/Kolkata"),
    ("Perth",        "Australia/Perth"),
    # ("Melbourne",    "Australia/Victoria"),
    # ("Sydney",       "Australia/Sydney"),
    # ("Sydney",       "Australia/Brisbane")
]

home_city = 'Edinburgh'
city_names = [c[0] for c in cities]
city_timezones = { c[0]: c[1] for c in cities }

# Future use
button_colors = ((255, 0, 0), (255, 150, 0), (0, 255, 255), (180, 0, 255))
button_tones = (1047, 1318, 1568, 2093)

TIME_URL = 'https://api.ipgeolocation.io/timezone?apiKey={}&tz={}'

# ---------------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------------

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

def initialise_wifi():
    print("Initialising WiFi ...")
    try:
        from secrets import secrets
    except ImportError:
        print("WiFi secrets are kept in secrets.py, please add them there!")
        raise

    wifi.radio.connect(secrets["ssid"], secrets["password"])
    pool = socketpool.SocketPool(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl.create_default_context())
    print("Initialising WiFi ... {} connected".format(secrets['ssid']))
    return(requests)

def get_time_info(cities, city_timezones):
    items = []
    for c in cities:
        if c not in city_timezones:
            print('Error - city not found: {}'.format(c))
        else:
            tz = city_timezones[c]
            print('City - {} - {}'.format(c, tz))
            url = TIME_URL.format(secrets['ipgl_key'], tz)
            response = requests.get(url)
            tz_info = response.json()
            if 'message' in tz_info:
                print('Error - failed request: {}'.format(tz_info['message']))
            else:
                if tz_info["timezone_offset"] <= 0:
                    tz_offset = tz_info["timezone_offset"]
                else:
                    tz_offset = "+{}".format(tz_info["timezone_offset"])

                item = [c, tz_info['date'], tz_info['time_24'], tz_offset]
                print(item)
                items.append(item)
    return items

def display_times(labels):
    city_info = get_time_info(city_names, city_timezones)
    # Add the new ones
    for i in range(len(labels)):
        c_info = city_info[i]
        c_text = "{}\n{} ({})\n{}".format(c_info[0], c_info[2], c_info[3], c_info[1])
        # print(c_text, p)
        labels[i].text= c_text

    magtag.refresh()

# ---------------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------------

# Get on the network
requests = initialise_wifi()

positions = [(10,10), (105,10), (200,10), (10, 70), (105,70), (200, 70)]
labels = []
for i in range(len(positions)):
    p = positions[i]
    l = label.Label(terminalio.FONT, x=p[0], y=p[1], text=" "*150, color=0x000000)
    labels.append(l)
    magtag.splash.append(l)

# Retrieve the city info
display_times(labels)

while True:
    for i, b in enumerate(magtag.peripherals.buttons):
        if i == 0 and not b.value:
            print('Refresh time')
            magtag.peripherals.neopixel_disable = False
            magtag.peripherals.neopixels.fill(button_colors[i])
            display_times(labels)
        else:
            magtag.peripherals.neopixel_disable = True

    time.sleep(0.1)