import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import math

import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



image = cv2.imread('images/test_image.png')

weather_sunny = cv2.imread('weather/weather_0.png')
weather_overcast = cv2.imread('weather/weather_1.png')
weather_rain = cv2.imread('weather/weather_2.png')
weather_thunder = cv2.imread('weather/weather_3.png')
weather_moony = cv2.imread('weather/weather_4.png')
weather_unknown = cv2.imread('weather/weather_5.png')


# create text on canvas
def create_text(text, x, y, size, font):
    font = ImageFont.truetype(font, size=size)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    # Draw the text (Pillow is RGB)
    if x == -1:
        x = (canvas.shape[1] - text_w) // 2

    if x == -2:
        x = (790 - text_w)

    if x == -3:
        x = (662 - text_w)



    draw.text((x, y), text, font=font, fill=(255, 255, 255))



# get weather info
def get_local_weather():
    lat, lon = -33.94939637463558, 151.25811240419085

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        # optionally specify timezone, e.g. "Australia/Sydney"
        "timezone": "Australia/Sydney"
    }

    try:
        # give it a timeout so it won't hang if the network is down
        r = requests.get(url, params=params, timeout=5.0)
        r.raise_for_status()

        payload = r.json()
        data = payload.get("current_weather")
        if not data:
            logger.error("No 'current_weather' in response: %r", payload)
            return None

        return {
            "temperature_c": data["temperature"],
            "windspeed_kmh": data["windspeed"],
            "winddirection_deg": data["winddirection"],
            "weather_code": data["weathercode"]
        }

    except:
        return None

# map weather to code
WMO_TO_CAT = {
    # sunny
    0: 0,   # Clear sky
    1: 0,   # Mainly clear
    2: 0,   # Partly cloudy

    # overcast / other (fog, snow, etc.)
    3: 1,   # Overcast
    45: 1,  # Fog
    48: 1,  # Depositing rime fog
    71: 1,  # Snow fall: Slight
    73: 1,  # Snow fall: Moderate
    75: 1,  # Snow fall: Heavy
    77: 1,  # Snow grains
    85: 1,  # Snow showers: Slight
    86: 1,  # Snow showers: Heavy

    # rain / drizzle / freezing rain
    51: 2,  # Drizzle: Light
    53: 2,  # Drizzle: Moderate
    55: 2,  # Drizzle: Dense
    56: 2,  # Freezing Drizzle: Light
    57: 2,  # Freezing Drizzle: Dense
    61: 2,  # Rain: Slight
    63: 2,  # Rain: Moderate
    65: 2,  # Rain: Heavy
    66: 2,  # Freezing Rain: Light
    67: 2,  # Freezing Rain: Heavy
    80: 2,  # Rain showers: Slight
    81: 2,  # Rain showers: Moderate
    82: 2,  # Rain showers: Violent

    # thunder
    95: 3,  # Thunderstorm: Slight or moderate
    96: 3,  # Thunderstorm with slight hail
    99: 3,  # Thunderstorm with heavy hail

    # unknown
    -1: 4,  # Thunderstorm with heavy hail
}

def categorise_wmo(code: int) -> int:
    return WMO_TO_CAT.get(code, 1)



if image is None:
    print("image could not be found")
else:
    h, w, c = image.shape

    scale = 1
    if w / h >= 15/7:
        scale = 750 / w
    else:
        scale = 350 / h

    w, h = int(w * scale), int(h * scale)
    resized_image = cv2.resize(image, (w,h), interpolation=cv2.INTER_AREA)



    canvas = np.full((480, 800, 3), (30,30,30), dtype=np.uint8)
    x_offset = (800 - w) // 2

    canvas[80 : h + 80, x_offset : x_offset+w] = resized_image

    ltime = datetime.now().strftime("%H:%M")


    local_weather = get_local_weather()
    if local_weather != None:
        temp = f"{math.floor(get_local_weather()['temperature_c'])}°"
        weather_type = categorise_wmo(get_local_weather()['weather_code'])
    else:
        temp = "?°"
        weather_type = categorise_wmo(-1)



    if weather_type == 0:
        if 5 < datetime.now().hour < 18:
            weather_image = weather_sunny
        else:
            weather_image = weather_moony
    elif weather_type == 1:
        weather_image = weather_overcast
    elif weather_type == 2:
        weather_image = weather_rain
    elif weather_type == 3:
        weather_image = weather_thunder
    else:
        weather_image = weather_unknown


    weather_image = cv2.resize(weather_image, (32, 32), interpolation=cv2.INTER_AREA)
    canvas[443 : 475, 670 : 702] = weather_image


    pil_im = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_im)

    create_text("group definition", -1, 20, 36, r"fonts\interb.ttf")

    create_text(ltime, -2, 445, 22, r"fonts\interl.ttf")
    create_text(temp, -3, 445, 22, r"fonts\interl.ttf")
    #create_text("1 of 9 pages", 10, 450, 18, r"fonts\interl.ttf")




    # Back to OpenCV (BGR)
    canvas = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)

    cv2.imshow("mister red", canvas)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

