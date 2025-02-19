# SSD1306 OLED 驅動程式

## 簡介
這是一個基於 I2C 的 SSD1306 OLED 顯示器的 Python 驅動程式。它支持基本功能，例如文字顯示、圖像顯示和畫面清除，並提供自定義的字型和圖形輸出功能。

---

## 功能列表
- 初始化 OLED 顯示器
- 顯示單字元與完整字串
- 清除 OLED 螢幕
- 顯示圖示與圖片

---

## 環境需求
- Python 版本: 3.7 或更高
- 硬體平台: 樹莓派或其他支持 I2C 的裝置
- 安裝的套件:
  - `smbus2`: 用於 I2C 通訊
  
```bash
pip install smbus2
```

---

## 安裝方式
1. 複製本專案代碼:
    ```bash
    git clone https://github.com/LuceZi/Luce_ssd1306.git
    ```
2. 確保安裝依賴環境:
    ```bash
    pip install -r requirements.txt
    ```
3. 準備好硬體並正確接線:
    - I2C 的 SCL 與 SDA 接至 SSD1306 模組相應腳位。

---

## 使用方法

### 1. 初始化 OLED
```python
from ssd1306 import initial_oled
from smbus2 import SMBus

# 使用 I2C 接口 1，初始化 OLED
bus = SMBus(1)
initial_oled(bus)
```

### 2. 清除螢幕
```python
from ssd1306 import oled_clear_display

oled_clear_display()
```

### 3. 顯示文字
#### 單字元顯示
```python
from ssd1306 import print_chr

# 在 page 0, column 10 顯示字母 "A"
print_chr(0, 10, "A")
```

#### 輸出字串
```python
from ssd1306 import display_string

# 在 page 0, column 0 顯示字串 "Hello OLED"
display_string(0, 0, "Hello OLED")
```

### 4. 顯示圖像與圖示
#### 圖示顯示
```python
from ssd1306 import display_icons

# 輸出預設圖示
icon = [[0x00] * 8] * 4  # 示例圖案
start_page = 0
start_col = 0
display_icons(start_page, start_col, icon)
```

#### 顯示圖片
```python
from ssd1306 import display_image

# 定義一個 64x48 的圖片數據
image_data = [0x00] * (64 * 6)  # 示例圖片
start_page = 0
start_col = 0
display_image(start_page, start_col, image_data)
```

---

## 字型說明
本庫使用內建的 5x7 字型，並自帶上下兩倍放大效果。若需擴展字型大小，可在 `font_data.py` 文件中自定義字元數據。

### 字型數據結構
- 字型數據被定義為一個 list，每個字元由 5 個 byte 組成。

#### 擴展字型
若需自定義字型，請修改 `font_data` 模組中的內容。

---

## 注意事項
1. 請確保硬體連線無誤，特別是 I2C 接口。
2. 本驅動程式假設 SSD1306 OLED 的 I2C 地址為 `0x3C`，若地址不同，請修改 `OLED_I2C_ADDR`。
3. 資料分段傳輸時每次不能超過 32 byte，該程式已自動處理分段。

---

## 授權
此程式以 MIT 授權發佈，歡迎自由使用與修改。

---

## 聯絡方式
如有問題，請至 [GitHub Issues](https://github.com/LuceZi/Luce_ssd1306/issues) 進行反饋或聯繫作者。

