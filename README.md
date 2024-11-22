# Raspberry Pico Time-to-Turkey Thermocouple Thermometer (RPT<sup>5</sup>)
This repository contains the code for a Raspberry Pico-based thermocouple thermometer that can be used to monitor the temperature of a turkey while it is cooking. The thermometer uses Type K thermocouple and a MAX31855 thermocouple amplifier. 

The thermometer provides a micro-webserver to display the current temperature, temperature history, projection and estimated time to completion. The thermometer can be accessed via a web browser on a computer, tablet or smartphone by entering the IP address of the Raspberry Pico. The temperature history is stored in a circular buffer and is displayed as a graph on the web page, which is updated every 5 seconds and stores longer-term temperature history in the browser's local storage. 

The projection is calculated using a 1D Kalman filter with position (temperature), velocity (temp per time), and acceleration (temp per time^2) states. The estimated time to completion is calculated by extrapolating the moving average rate of change of the temperature to the desired temperature. The rate of change is calculated as a exponential moving average of the temperature history.

# Materials
- [Raspberry Pico](https://www.raspberrypi.com/products/raspberry-pi-pico/)
- Type K probe thermocouple [Amazon](https://www.amazon.com/gp/product/B07PJNRBKG/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)
- Type K Thermocouple [Amazon](https://www.amazon.com/HiLetgo-MAX6675-Thermocouple-Temperature-Arduino/dp/B01HT871SO?crid=3QW9LRR5YXBG6&dib=eyJ2IjoiMSJ9.hdWC_-c5v-buXstxZxYlcDZ7tDdsbYpgocHQ7M2yuJDP7qdvNvN2987X4dtrQfedXl3rS4VF7pDAXsOTzWua6whifliDE793xs2xu9yz3ewBiXFTMHox-zilOgUMI-ifK8nErLbNb1H8D3qdbxBpBObSE1CCezp2iAhz12k9SNT1ClCHJlXMjULCzafIdSOakaWYtlCd4fD9Qk_Z1XeJYpOAnWctSwkquUiVSHSgh765SL9uSqAK_bO5RiAYt317sveZkl75WTE5YH1sg_m2ZCF-q-qroXV7UvKr5limOSY.UQAWeB2cxULGkaoUmwUU3MvPF25mq14xqb2EOq9nkKU&dib_tag=se&keywords=max6675&qid=1732252048&s=industrial&sprefix=max6675%2Cindustrial%2C156&sr=1-6https://www.amazon.com/HiLetgo-MAX6675-Thermocouple-Temperature-Arduino/dp/B01HT871SO?crid=3QW9LRR5YXBG6&dib=eyJ2IjoiMSJ9.hdWC_-c5v-buXstxZxYlcDZ7tDdsbYpgocHQ7M2yuJDP7qdvNvN2987X4dtrQfedXl3rS4VF7pDAXsOTzWua6whifliDE793xs2xu9yz3ewBiXFTMHox-zilOgUMI-ifK8nErLbNb1H8D3qdbxBpBObSE1CCezp2iAhz12k9SNT1ClCHJlXMjULCzafIdSOakaWYtlCd4fD9Qk_Z1XeJYpOAnWctSwkquUiVSHSgh765SL9uSqAK_bO5RiAYt317sveZkl75WTE5YH1sg_m2ZCF-q-qroXV7UvKr5limOSY.UQAWeB2cxULGkaoUmwUU3MvPF25mq14xqb2EOq9nkKU&dib_tag=se&keywords=max6675&qid=1732252048&s=industrial&sprefix=max6675%2Cindustrial%2C156&sr=1-6)
- I2C LED display [Amazon](https://www.amazon.com/gp/product/B07Q2S8LZL/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)
- Project box [Amazon](https://www.amazon.com/gp/product/B07Q2S8LZL/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)
- Water proof glands [Amazon](https://www.amazon.com/Waterproof-Adjustable-Connectors-Plastic-Protectors/dp/B085NVDC3K?crid=3BQ32O92PBDG4&dib=eyJ2IjoiMSJ9.fWhsZaEQxeM_DX5U6Mjc8-ameXa5-rzGA8VhAcgy0IvMdejNZakByAgbXZeM675xz75vXXHXszqc5g0xZzYUZQ3QgZV-YpAiOMwHTDdeK6QXGLEpztecVMHAVqH-YOviHRzUAHgSExehCF-zAWUMqd1lb612Odihycqsq3B53_aUOLeGDEaths4PJJFtcv6ohY27REEaBOiUk9dqBTjwQu2nA9XgcOKUL77BPZh_czX5igaHxYZ7nDkZy5dzQBRRLWoNlkEaL5Sb-CcLSJA3zuieSLZd2et9RWwambRHFXI.mCAuUDxU0kGe46CTlDGJbXRaXgpqZm_a8IZMyg1MI68&dib_tag=se&keywords=water+proof+glands&qid=1732252498&s=industrial&sprefix=water+proof+glands%2Cindustrial%2C164&sr=1-3)
- On/Off switch [Amazon](https://www.amazon.com/gp/product/B09BKXVCQ8/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)
- USB battery pack (I had one laying around that I deconstructed)

# Usage

1. Create a `env.py` file in the root directory of the project with the following content:
    ```
    SSID='your wife'
    PASSWORD='your_password'
    ```

2. Upload the code to the Raspberry Pico using Thonny or your favorite editor.

3. Turn on the Raspberry Pi Pico. 

The Raspberry Pi Pico will connect to your WiFi network and display the IP address on the LED display. You can access the thermometer by entering the IP address in a web browser.


