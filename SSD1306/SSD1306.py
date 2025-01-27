from . import font_data 

class SSD1306:
    def __init__(self, bus, width=128, height=64, i2c_address=0x3C):
        self.bus = bus
        self.width = width
        self.height = height
        self.i2c_address = i2c_address
        self.buffer = [0x00] * (width * height // 8)  # 緩衝區
        self.oled_init()

        self.display_helper = DisplayHelper(self)  # 傳遞 `SSD1306` 實例
    
    def oled_init(self):
        """
        初始化 OLED
        """
        commands = [
            0xAE,  # Display off
            0xD5, 0x80,  # Set display clock divide ratio/oscillator frequency
            0xA8, 0x3F,  # Set multiplex ratio (1 to 64)
            0xD3, 0x00,  # Set display offset
            0x40,  # Set start line address
            0x8D, 0x14,  # Charge pump
            0x20, 0x00,  # Memory addressing mode: horizontal
            0xA1,  # Segment re-map (mirror horizontally)
            0xC8,  # COM output scan direction
            0xDA, 0x12,  # COM pins hardware configuration
            0x81, 0xCF,  # Set contrast control
            0xD9, 0xF1,  # Set pre-charge period
            0xDB, 0x40,  # Set Vcomh deselect level
            0xA4,  # Entire display ON
            0xA6,  # Set normal display mode
            0xAF,  # Display ON
        ]
        for cmd in commands:
            self.oled_write_command(cmd)

    def oled_write_command(self, command):
        """
        寫入命令到 OLED
        """
        self.bus.write_byte_data(self.i2c_address, 0x00, command)

    def oled_write_data(self, data):
        """
        寫入數據到 OLED        
        """
        self.bus.write_byte_data(self.i2c_address, 0x40, data)

class DisplayHelper:
    def __init__(self, ssd1306):
        """
        初始化顯示輔助類別
        :param ssd1306: SSD1306 實例
        """
        self.ssd1306 = ssd1306

    def oled_set_position(self, page, column):
        """
        設置 SSD1306 的顯示位置
        :param bus: I2C bus
        :param page: GDDRAM 的頁地址 (0~7)
        :param column: GDDRAM 的列地址 (0~127)
        """
        self.ssd1306.bus.write_i2c_block_data(self.ssd1306.i2c_address, 0x00, [
            0xB0 | (page & 0x07),
            0x00 | (column & 0x0F),
            0x10 | (column >> 4 & 0x0F)
        ])

    def oled_clear_display(self):
        """
        清除顯示緩衝區並更新螢幕
        """
        for i in range(8):
            self.oled_set_position(i, 0)  # 設置頁
            for _ in range(self.ssd1306.width):
                self.ssd1306.oled_write_data(0x00)

    def oled_write_page_data(self, page, column, data):
        """
        將一組資料寫入某頁
        確保 `data` 是列表格式。
        """
        if isinstance(data, int):  # 將數字包裝成列表
            data = [data]
        self.oled_set_position(page, column)
        self.ssd1306.bus.write_i2c_block_data(self.ssd1306.i2c_address, 0x40, data)

    def print_oled(self, page, column, data): 
        """
        將字元或數字顯示到螢幕上
        :bus
        :寫入頁
        :寫入行
        :str or int
        :!!! 輸入只能一個字元 !!!
        """
        if isinstance(data, str) and len(data) == 1:
            data = ord(data) - 0x20
        elif isinstance(data, int):
            data = data + 0x10   
        else:
            raise ValueError("val err at print_oled!! QAQ")

        def _expand_font(font):
            """
            將原始 5×(7+1) 字庫擴展成 10×16 字庫。
            font: 一個長度為 8 的陣列，表示 5×8 的字元，格式為每 Byte 控制 5 列。
            回傳兩個 list，分別對應放大後的上半部分和下半部分。
            """
            def expand_4_bits_to_8(data, shift=0):
                bits = (data >> shift) & 0x0F  # 提取高或低 4 位
                result = 0
                for bit in range(4):  # 遍歷 4 位
                    bit_value = (bits >> bit) & 1
                    result |= (bit_value << (bit * 2))       # 第一個複製位
                    result |= (bit_value << (bit * 2 + 1))  # 第二個複製位
                return result

            # 上下各放大兩倍，雙行重複數據
            upper_pages = [
                value for row in font_data.font_5x7[font]
                for value in (expand_4_bits_to_8(row, shift=0), expand_4_bits_to_8(row, shift=0))
            ]
            lower_pages = [
                value for row in font_data.font_5x7[font]
                for value in (expand_4_bits_to_8(row, shift=4), expand_4_bits_to_8(row, shift=4))
            ]

            return upper_pages, lower_pages    
        
        upper_pages, lower_pages = _expand_font(data)  # 解壓 tuple
        self.oled_write_page_data (page, column, upper_pages)
        self.oled_write_page_data (page+1, column, lower_pages)

    def display_icons(self, start_page, start_column, icon):
        """
        用於輸出圖示到oled螢幕上
        :param start_page: 起始頁
        :param start_column: 起始行（左側列）
        :param icon: icon array 
        ! icon array [4][8] !
        """
        self.oled_write_page_data(start_page, start_column, icon[0])
        self.oled_write_page_data(start_page, start_column+8, icon[1])
        self.oled_write_page_data(start_page+1, start_column, icon[2])
        self.oled_write_page_data(start_page+1, start_column+8, icon[3])
    
    def display_image(self, page, column, data):
        """
        顯示 64x48 的圖片
        :param 起始page
        :param 起始column
        :param image array
        """
        display_per_column = 0
        for _p in range (6):
            for _c in range (64):
                self.oled_write_page_data(page+_p, column+_c, [data[display_per_column]])
                display_per_column += 1