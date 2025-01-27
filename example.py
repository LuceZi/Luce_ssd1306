import smbus
import Luce_SSD1306
import RPi.GPIO as GPIO
import time 

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)  # 控制 OLED1 的 SCL
GPIO.output(17, GPIO.HIGH)

def main():
    Luce_SSD1306.oled_clear_display()
    Luce_SSD1306.display_string(0,0,"Hello,This is Luce!")
    time.sleep(2)
    Luce_SSD1306.display_string(0,0,"Thanks for download my Luce_SSD1306 driver.")
    time.sleep(5)
    Luce_SSD1306.oled_clear_display()

def startup():
    bus = None
    try:
        bus = smbus.SMBus(1)  # 開啟 I2C
        Luce_SSD1306.initial_oled(bus) 
        main()
    except KeyboardInterrupt:
        print("keyboard end!")
    except Exception as e:
        print(f"\n發生錯誤：{e}")
    finally:
        print("end")
        
if __name__ == "__main__":
    startup()