from . import font_data 

# SSD1306 I2C 地址
OLED_I2C_ADDR = 0x3C

_oled_bus = None

def initial_oled(bus):
    """
    保存 bus，使其可以在後續操作中直接訪問
    """
    global _oled_bus
    def _initial_commands():
        """初始化 OLED"""
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
            oled_write_command(cmd)

    _oled_bus = bus
    _initial_commands()
    
def oled_write_command(command):
    """
    寫入命令到 OLED
    """
    global _oled_bus
    _oled_bus.write_byte_data(OLED_I2C_ADDR, 0x00, command)

def oled_write_data(data):
    """
    寫入數據到 OLED
    """
    global _oled_bus
    _oled_bus.write_byte_data(OLED_I2C_ADDR, 0x40, data)

def oled_write_page_data(page, column, data):
    """將一組資料寫入某頁"""
    global _oled_bus

    if not data:
        raise ValueError("資料不能為空")  # 或忽略空資料
    
    def oled_set_position(_oled_bus, page, column):
        """
        設置 SSD1306 的顯示位置
        :param _oled_bus: I2C _oled_bus
        :param page: GDDRAM 的頁地址 (0~7)
        :param column: GDDRAM 的列地址 (0~127)
        """
        _oled_bus.write_i2c_block_data(OLED_I2C_ADDR, 0x00, [
            0xB0 | (page & 0x07),         # 設置頁地址
            0x00 | (column & 0x0F),      # 設置列地址低位
            0x10 | (column >> 4 & 0x0F)  # 設置列地址高位
        ])
    oled_set_position(_oled_bus, page, column)

    # 分段傳送資料，防止超過 32 字節
    for i in range(0, len(data), 32):
        _oled_bus.write_i2c_block_data(OLED_I2C_ADDR, 0x40, data[i:i+32])

def oled_clear_display():
    """
    完全清除屏幕
    """
    global _oled_bus
    clear_data = [0x00] * 128

    for i in range(8):  # 每頁清空
        # 設置頁地址
        _oled_bus.write_byte_data(OLED_I2C_ADDR, 0x00, 0xB0 + i)  # Set page address
        # 設置列地址
        _oled_bus.write_i2c_block_data(OLED_I2C_ADDR, 0x00, [0x00, 0x10])  # Set lower and higher column address
        
        # 使用 batch 批量清空每頁 (128 個字元一次發送)
        for j in range(0, 128, 32):
            _oled_bus.write_i2c_block_data(OLED_I2C_ADDR, 0x40, clear_data[j:j + 32])

def print_chr(page, column, data): 
    global _oled_bus
    """
    將字元或數字顯示到螢幕上
    :寫入頁
    :寫入行
    :str or int
    :!!! 輸入只能一個字元 !!!
    """
    if isinstance(data, str):
        data = ord(data) - 0x20 #字庫偏移-32
    elif isinstance(data, int):
        data = data + 0x10 #數字偏移+16
    else:
        raise ValueError("val err QAQ")

    def _expand_font_(font):
        """
        將原始 5×7 字庫擴展成 10×14 字庫。
        font: 一個長度為 7 的陣列，表示 5×7 的字元，格式為每 Byte 控制 5 列。
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
    
    upper_pages, lower_pages = _expand_font_(data)  # 解壓 tuple
    oled_write_page_data (page, column, upper_pages)
    oled_write_page_data (page+1, column, lower_pages)

def display_string(start_page, start_column, text):
    """
    將完整的字串寫入 OLED，字元之間添加字距 (column 單位 1)，有自動換行
    :param start_page: 起始頁
    :param start_column: 起始行（左側列）
    :param text: 要顯示的文字
    """
    column = start_column  # 當前列位置
    page = start_page  # 起始頁位置

    char_width = 10  # 每個字元寬度
    char_spacing = 1  # 每個字元之間的間距（單位為 OLED column）

    for char in text:

        print_chr(page, column, char)
        column += (char_spacing + char_width)

        if column > 118:
            column = start_column
            page += 2

            if page >= 7:
                page = start_page

def display_image(page, col, data):
    global _oled_bus
    """
    顯示 64x48 的圖片
    :param 起始page
    :param 起始colon
    :param 圖片選擇(font data)
    """
    display_per_col = 0
    
    for _p in range (6):
        for _c in range (64):
            oled_write_page_data(page+_p, col+_c, [data[display_per_col]])
            display_per_col += 1

def display_icons(start_page, start_col, icon):
    global _oled_bus
    """
    用於輸出圖示到oled螢幕上
    :param start_page: 起始頁
    :param start_column: 起始行（左側列）
    :param icon: 要顯示的圖示
    """
    oled_write_page_data(start_page, start_col, icon[0])
    oled_write_page_data(start_page, start_col+8, icon[1])
    oled_write_page_data(start_page+1, start_col, icon[2])
    oled_write_page_data(start_page+1, start_col+8, icon[3])