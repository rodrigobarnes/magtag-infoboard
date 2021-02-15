import board
import analogio


# Based on https://github.com/adafruit/Adafruit_Learning_System_Guides/blob/master/Introducing_Feather_M0_Express/battery_voltage.py
def get_voltage(pin):
    return (pin.value * 3.3) / 65536 * 2

battery_voltage = analogio.AnalogIn(board.VOLTAGE_MONITOR)

print(battery_voltage.value)
print("Voltage: {:.2f}".format(get_voltage(battery_voltage)))
