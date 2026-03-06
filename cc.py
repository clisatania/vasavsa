import base64
import random
import requests
from seleniumbase import SB

# ---------------------------------------------------------
#  GEOLOCATION & USER DATA
# ---------------------------------------------------------

geo_data = requests.get("http://ip-api.com/json/").json()

latitude = geo_data["lat"]
longitude = geo_data["lon"]
timezone_id = geo_data["timezone"]
language_code = geo_data["countryCode"].lower()

proxy_str = False

# Decode Base64 username
encoded_name = "YnJ1dGFsbGVz"
decoded_name = base64.b64decode(encoded_name).decode("utf-8")

# Target Twitch URL
twitch_url = f"https://www.twitch.tv/{decoded_name}"


# ---------------------------------------------------------
#  MAIN LOOP
# ---------------------------------------------------------

while True:
    with SB(
        uc=True,
        locale="en",
        ad_block=True,
        chromium_arg="--disable-webgl",
        proxy=proxy_str
    ) as browser:

        wait_time = random.randint(450, 800)

        # Activate CDP mode with timezone + geolocation spoofing
        browser.activate_cdp_mode(
            twitch_url,
            tzone=timezone_id,
            geoloc=(latitude, longitude)
        )

        browser.sleep(2)

        # Handle cookie popups
        if browser.is_element_present('button:contains("Accept")'):
            browser.cdp.click('button:contains("Accept")', timeout=4)

        browser.sleep(2)
        browser.sleep(12)

        # Handle "Start Watching" button
        if browser.is_element_present('button:contains("Start Watching")'):
            browser.cdp.click('button:contains("Start Watching")', timeout=4)
            browser.sleep(10)

        # Accept again if needed
        if browser.is_element_present('button:contains("Accept")'):
            browser.cdp.click('button:contains("Accept")', timeout=4)

        # Check if stream is live
        if browser.is_element_present("#live-channel-stream-information"):

            # Accept again if needed
            if browser.is_element_present('button:contains("Accept")'):
                browser.cdp.click('button:contains("Accept")', timeout=4)

            # ---------------------------------------------------------
            #  SECONDARY DRIVER (undetectable)
            # ---------------------------------------------------------
            secondary = browser.get_new_driver(undetectable=True)
            secondary.activate_cdp_mode(
                twitch_url,
                tzone=timezone_id,
                geoloc=(latitude, longitude)
            )

            secondary.sleep(10)

            if secondary.is_element_present('button:contains("Start Watching")'):
                secondary.cdp.click('button:contains("Start Watching")', timeout=4)
                secondary.sleep(10)

            if secondary.is_element_present('button:contains("Accept")'):
                secondary.cdp.click('button:contains("Accept")', timeout=4)

            browser.sleep(10)
            browser.sleep(wait_time)

        else:
            # Stream is offline → exit loop
            break
