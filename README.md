# RTD2660 VGA (header 12P) → LVDS 20P cho màn 7" 1024x600

Mạch điều khiển màn hình dùng chip Realtek **RTD2660**, thiết kế theo datasheet trong repo (`RTD2660.jsp.pdf`).

- **Đầu vào:** VGA trên **header 12 chân 2.54 mm**, cắm thẳng vào header VGA trên mainboard.
- **Đầu ra:** LVDS 1 kênh, 24 bit trên **đầu 20 chân 2.0 mm (J5)**, cùng **đầu đèn nền 4 chân 2.0 mm (J6)**.
  Hai đầu này khớp với cáp của màn 7" IPS 1024x600 LVDS 20 chân (Huadi).
- **Bản RGB 40P/50P tạm bỏ.** Mạch của chúng vẫn còn trong `tools/circuit.py` để làm sau.

| File | Nội dung |
|---|---|
| `eagle/RTD2660_VGA12P_LVDS.sch` | Sơ đồ nguyên lý, 4 trang |
| `eagle/RTD2660_VGA12P_LVDS.brd` | Board 120 x 80 mm, linh kiện đã đặt ở mặt trên, chưa đi dây |
| `eagle/rtd2660_board.lbr` | Thư viện linh kiện |
| `eagle/RTD2660_VGA12P_LVDS_BOM.csv` | Danh sách linh kiện |
| `preview/RTD2660_VGA12P_LVDS_preview.pdf` | Bản xem trước sơ đồ và board |
| `firmware/` | Script cấu hình firmware cho SDK RTD2660 |

## Trạng thái

- **Sơ đồ nguyên lý: xong.** Các net nối bằng nhãn tên.
- **Board: toàn bộ 114 linh kiện đặt ở mặt trên, chưa đi dây.** Có sẵn polygon GND ở mặt dưới.
- Mở bằng Eagle 7.x, 8.x hoặc 9.x. File `.brd` mở kèm và nhất quán với sơ đồ.
- **Đã kiểm tra:** KiCad đọc được file `.brd`, netlist khớp 100% từng pad với sơ đồ. DRC không có linh kiện chồng nhau.
  `tools/check_eagle.py` xác nhận mọi chân nằm trên lưới 0.1 inch.
- Khi đi dây, đi các cặp LVDS thành cặp vi sai 100 Ω, ngắn và bằng chiều dài. Thêm via tản nhiệt dưới pad GND của RTD2660.

## Sơ đồ chân các đầu nối

**J2 - VGA 1x12, 2.54 mm (đầu vào)**

| Chân | Tín hiệu |
|---|---|
| 1 | VGA_R |
| 2 | GND |
| 3 | VGA_G |
| 4 | GND |
| 5 | VGA_B |
| 6 | GND |
| 7 | VGA_HS |
| 8 | VGA_VS |
| 9 | GND |
| 10 | VGA_SDA |
| 11 | VGA_SCL |
| 12 | VGA_5V |

Chân 12 (+5V từ mainboard) không dùng. Nếu header VGA trên mainboard có thứ tự khác, sửa `VGA12_PINOUT` trong `tools/circuit.py`.

**J5 - LVDS 1x20, 2.0 mm (đầu đen của cáp màn)**

| Chân | Tín hiệu |
|---|---|
| 1 | VLCD |
| 2 | VLCD |
| 3 | PNL_LED_EN |
| 4 | GND |
| 5 | LVDS_E0- |
| 6 | LVDS_E0+ |
| 7 | GND |
| 8 | LVDS_E1- |
| 9 | LVDS_E1+ |
| 10 | GND |
| 11 | LVDS_E2- |
| 12 | LVDS_E2+ |
| 13 | GND |
| 14 | LVDS_EC- |
| 15 | LVDS_EC+ |
| 16 | GND |
| 17 | LVDS_E3- |
| 18 | LVDS_E3+ |
| 19 | không dùng |
| 20 | không dùng |

Chân 1-18 giống hệt sơ đồ chân của màn. Ở chế độ 1 kênh, RTD2660 xuất trên các cặp E (chân 86-95 của chip).

**J6 - đèn nền 1x4, 2.0 mm (đầu trắng của cáp màn)**

| Chân | Tín hiệu |
|---|---|
| 1 | +12V |
| 2 | PNL_LED_EN |
| 3 | PNL_BL_ADJ |
| 4 | GND |

**Thứ tự chân J6 là giả định.** Hãy đo cáp bằng đồng hồ: VLED nối chân 20 của màn, PWM nối chân 19, LED_EN nối chân 3.
Nếu khác, sửa `BL4_PINOUT` trong `tools/circuit.py` rồi chạy lại script.

- Chân độ sáng ra điện áp DC từ 0 đến 1.41 V, lấy từ PWM4 qua bộ lọc 10k / 7.5k / 1 µF. Màn nhận 0.7 đến 1.4 V.
- LED_EN lấy từ BL_ON qua 1k, có 10k kéo xuống.
- VLED lấy thẳng từ +12 V. Màn nhận 5 đến 12 V.

Các đầu nối khác:

- **J1, nguồn vào 12 V:** 1 = +12V, 2 = GND. Có cầu chì PTC 2 A và diode chống ngược.
- **J3, nạp firmware qua DDC:** GND, SDA, SCL.
- **J4, phím và IR (1x8):** 1 +3V3, 2 GND, 3 KEY_AD0, 4 KEY_AD1, 5 IR, 6 LED_G, 7 LED_R, 8 +5V.

## Nguồn

12 V → LM2596S-5.0 → 5 V. Từ 5 V có hai AMS1117-3.3: một cho phần số (PVCC, flash) và một cho phần analog (VDD, VADC).
Từ đó hai AMS1117-1.8 tạo VCCK (lõi) và ADC_VDD.
VDD 3.3 V của màn lấy từ một AMS1117-3.3 riêng, được bật bằng MOSFET AO3401A theo chân PANEL_ON.

## Bàn phím (J4)

SDK đọc phím bằng một kênh ADC 6 bit (KEY_AD0, chân 50). Trên board đã có điện trở kéo lên 10k.
Trên bo phím, mỗi nút nối KEY_AD0 xuống GND qua một điện trở:

| Nút | Điện trở xuống GND | Mã ADC |
|---|---|---|
| POWER | 0 Ω | 0 |
| MENU | 1.8k | 10 |
| RIGHT | 3.9k | 18 |
| LEFT | 8.2k | 28 |
| SOURCE | 22k | 43 |

## Gán chân GPIO

| Chân | Chức năng chip | Net | Dùng cho |
|---|---|---|---|
| 50 | P6.0 / A-ADC0 | KEY_AD0 | Keypad resistor ladder 1 (ADC) |
| 51 | P6.1 / A-ADC1 | KEY_AD1 | Keypad resistor ladder 2 (ADC) |
| 52 | P6.2 | LED_R_DRV | Red / standby LED, active high |
| 53 | P6.3 | LED_G_DRV | Green / power LED, active high |
| 58 | DDCSCL1 (P3.0) | DDC_SCL | VGA DDC clock, ISP programming |
| 59 | DDCSDA1 (P3.1) | DDC_SDA | VGA DDC data, ISP programming |
| 98 | P5.4 | PANEL_ON | Panel power enable, active high |
| 99 | P5.5 | BL_ON | Backlight enable, active high |
| 100 | P5.6 / PWM4 | BL_PWM | Backlight brightness PWM, high = bright |
| 113 | P3.6 / IrDA | IR_IN | IR receiver input |

## Firmware

RTD2660 cần firmware trong flash W25Q40. Xem `firmware/README.md`.
Script áp cấu hình board và màn 1024x600 lên SDK RTD2660, sau đó biên dịch bằng Keil C51.

## Những điểm cần kiểm tra

1. **Thạch anh 27 MHz**, giống board tham chiếu PCB800099 của SDK.
2. **Chân SPI flash.** Tên chân (115 SCLK, 116 SI, 117 SO) và phần mô tả trong datasheet lệch nhau ở chân 115/116.
   Mạch theo tên chân. Có sẵn cặp điện trở 33R (không hàn) để đảo CLK/DI nếu flash không chạy.
3. **Thứ tự chân header VGA 12P và đầu đèn nền 4 chân.** Phải khớp với mainboard và cáp màn.
4. **Timing màn** (tổng 1344 x 635, 51.2 MHz) là giá trị phổ biến của màn 7" 1024x600. Nếu có datasheet màn, đối chiếu lại.

## Sửa thiết kế

```bash
pip install lxml matplotlib
python3 tools/gen_eagle.py      # sinh file Eagle và BOM
python3 tools/check_eagle.py    # kiểm tra
python3 tools/preview.py        # sinh bản xem trước PDF
```

- `tools/circuit.py`: mạch điện, sơ đồ chân các đầu nối, bảng GPIO
- `tools/parts.py`: ký hiệu, footprint, sơ đồ chân RTD2660
- `tools/gen_eagle.py`: ghi file Eagle và đặt linh kiện trên board
- `firmware/apply_board.py`: áp cấu hình board và màn lên SDK firmware RTD2660
