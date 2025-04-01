# Smart Irrigation System

This project implements a smart irrigation system that uses weather data from the [AccuWeather API](https://developer.accuweather.com/) to determine whether to activate irrigation. The system ensures efficient water usage by considering the following criteria:
1. It is not currently raining.
2. It has not rained a significant amount the previous day.
3. It will not rain a significant amount the next day.

## Features
- Fetches real-time weather data using the AccuWeather API.
- Saves weather data to JSON files for local processing.
- Controls an irrigation relay using a Raspberry Pi GPIO pin.
- Displays system status on an LCD screen.

## Requirements
- Python 3.x
- Raspberry Pi with GPIO support
- [gpiozero](https://gpiozero.readthedocs.io/) library
- [I2C_LCD_driver](https://github.com/the-raspberry-pi-guy/lcd) for LCD control
- `requests` library for API calls
- AccuWeather API key

## Installation
1. Clone this repository to your Raspberry Pi.
2. Install the required Python libraries:
   ```bash
   pip install requests gpiozero
