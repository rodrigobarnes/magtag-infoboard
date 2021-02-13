# MagTag Infoboard

A personal project to turn an [Adafruit MagTag](https://www.adafruit.com/magtag) into a useful information board you can keep on your desk.

## World times

The first feature is to display current time at different cities of interest. Press the first and second button to ccyle through a list of interesting cities and see their current time, time zone, and offset from GMT.

This uses the [ipgeolocation API](https://ipgeolocation.io/documentation.html) to get information, taking advantage of the MagTag's built in WiFi.

## Configuration

In addition to your WiFi network and password. Make sure [`secrets.py`](./secrets.py) also has the API key for ipgeolocation.


