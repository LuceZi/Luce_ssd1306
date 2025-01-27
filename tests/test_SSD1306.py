import unittest
from unittest.mock import MagicMock
from SSD1306.SSD1306 import SSD1306, DisplayHelper

class TestSSD1306(unittest.TestCase):

    def setUp(self):
        # 在每個測試之前，初始化 mock I2C bus
        self.mock_bus = MagicMock()
        self.ssd1306 = SSD1306(self.mock_bus)  # 初始化 SSD1306 實例

    def test_oled_init(self):
        """
        測試 SSD1306 初始化時是否正確發送了初始化命令
        """
        # 檢查是否傳送了 OLED 初始化的命令
        expected_commands = [
            0xAE, 0xD5, 0x80, 0xA8, 0x3F, 0xD3, 0x00,
            0x40, 0x8D, 0x14, 0x20, 0x00, 0xA1, 0xC8,
            0xDA, 0x12, 0x81, 0xCF, 0xD9, 0xF1, 0xDB,
            0x40, 0xA4, 0xA6, 0xAF
        ]
        # 測試初始化過程中會傳送的命令
        self.ssd1306.oled_init()
        # 驗證對應的命令被正確送出
        self.mock_bus.write_byte_data.assert_any_call(self.ssd1306.i2c_address, 0x00, expected_commands[0])
        for command in expected_commands:
            self.mock_bus.write_byte_data.assert_any_call(self.ssd1306.i2c_address, 0x00, command)

    def test_print_oled_char(self):
        """
        測試將字符顯示到屏幕上
        """
        # 使用 'A' 來測試打印功能
        self.ssd1306.display_helper.print_oled(0, 0, 'A')
        
        # 驗證字型擴展後的數據（此部分需要確認擴展字庫是否正確）
        self.mock_bus.write_i2c_block_data.assert_any_call(self.ssd1306.i2c_address, 0x40, [0x7E, 0x11, 0x11, 0x11, 0x7E])

    def test_display_clear(self):
        # 測試清除螢幕
        self.ssd1306.display_helper.oled_clear_display()

        # 確認 `oled_set_position` 被呼叫來設置頁地址（0~7）和列地址（0~127）
        for i in range(8):
            self.ssd1306.display_helper.oled_set_position.assert_any_call(i, 0)

        # 確認寫入命令給 I2C bus，在清除顯示時應該寫入 `0x00`
        # 第一個參數是 I2C 地址，第二個參數是 0x00，第三個是 0x00（清除畫面）
        self.mock_bus.write_byte_data.assert_any_call(self.ssd1306.i2c_address, 0x00, 0xB0 + i)
        self.mock_bus.write_byte_data.assert_any_call(self.ssd1306.i2c_address, 0x00, 0x00)
        self.mock_bus.write_byte_data.assert_any_call(self.ssd1306.i2c_address, 0x00, 0x10)
        self.mock_bus.write_byte_data.assert_any_call(self.ssd1306.i2c_address, 0x40, 0x00)

        # 確認 `oled_write_data` 正確地將資料 0x00 寫入 OLED
        for _ in range(self.ssd1306.width):
            self.mock_bus.write_byte_data.assert_any_call(self.ssd1306.i2c_address, 0x40, 0x00)
    def test_display_image(self):
        """
        測試顯示 64x48 圖片
        """
        data = [0xFF] * (64 * 6)  # 假設要顯示滿版的圖像
        self.ssd1306.display_helper.display_image(0, 0, data)

        # 測試所有對應的數據是否被送出
        for i in range(64 * 6):
            self.mock_bus.write_i2c_block_data.assert_any_call(self.ssd1306.i2c_address, 0x40, [data[i]])


if __name__ == '__main__':
    unittest.main()
