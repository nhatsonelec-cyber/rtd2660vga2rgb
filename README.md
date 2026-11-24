# RTD2660 VGA (header 12P) → LVDS / RGB 40P / RGB 50P

Mạch điều khiển màn hình dùng chip Realtek **RTD2660**, thiết kế theo datasheet có trong repo (`RTD2660.jsp.pdf`).
Đầu vào VGA là **header 12 chân 2.54 mm**, cắm thẳng vào header VGA trên mainboard, không dùng cổng DB15.
Có ba phiên bản đầu ra:

| Phiên bản | Đầu ra | File Eagle |
|---|---|---|
| LVDS | Header 2x15 chân **2.0 mm** (LVDS 1 hoặc 2 kênh) | `eagle/RTD2660_VGA12P_LVDS.sch` / `.brd` |
| RGB40 | FPC 40 chân 0.5 mm, TTL RGB 24 bit (AT043TN24, màn 4.3"-7" 40P) | `eagle/RTD2660_VGA12P_RGB40.sch` / `.brd` |
| RGB50 | FPC 50 chân 0.5 mm, TTL RGB 24 bit (AT070TN90/92, 7" 800x480) | `eagle/RTD2660_VGA12P_RGB50.sch` / `.brd` |

Thư viện linh kiện là `eagle/rtd2660_board.lbr`. BOM của từng bản nằm trong `eagle/*_BOM.csv`.
Bản xem trước PDF (sơ đồ nguyên lý và bố trí board) nằm trong `preview/`.

## Trạng thái

- **Sơ đồ nguyên lý: xong.** Các net được nối bằng nhãn tên. Mỗi bản có 4 trang: nguồn, RTD2660, đầu vào VGA/phím/ISP, đầu ra.
- **Board: mới đặt linh kiện, CHƯA đi dây.** Board 120 x 80 mm, có sẵn polygon GND ở lớp Bottom.
  Linh kiện được xếp sơ bộ theo khối chức năng. Cần chỉnh vị trí và đi dây trong Eagle.
  Cặp LVDS và bus RGB cần đi dây ngắn, đều nhau. Cặp vi sai LVDS 100 Ω.
- Mở file trong Eagle 7.x, 8.x hoặc 9.x (File → Open → `.sch`). File `.brd` cùng tên được mở kèm và đã nhất quán với sơ đồ (F/B annotation).
- Đã kiểm tra: KiCad 7 đọc được cả 3 file `.brd` và netlist khớp 100% từng pad với sơ đồ.
  Script `tools/check_eagle.py` xác nhận mọi chân nằm trên lưới 0.1 inch và mọi dây đều chạm chân.
  DRC không có lỗi chồng linh kiện hay chạm pad.

## Sửa thiết kế

Mọi file được sinh từ script Python, sửa ở script rồi chạy lại:

```bash
pip install lxml matplotlib
python3 tools/gen_eagle.py      # sinh eagle/*.sch, *.brd, *.lbr, BOM
python3 tools/check_eagle.py    # kiểm tra
python3 tools/preview.py        # sinh preview/*.pdf
```

- `tools/circuit.py`: mạch điện, pinout các đầu nối, bảng GPIO
- `tools/parts.py`: ký hiệu, footprint, sơ đồ chân RTD2660
- `tools/gen_eagle.py`: ghi file Eagle và xếp linh kiện trên board
- `firmware/apply_board.py`: áp cấu hình board và màn lên SDK firmware RTD2660

Nếu header VGA trên mainboard có thứ tự chân khác, chỉ cần sửa `VGA12_PINOUT` trong `tools/circuit.py`.

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

Chân 12 (+5V từ mainboard) không dùng. J3 (GND, SDA, SCL) dùng để nạp firmware qua DDC bằng công cụ ISP của Realtek.

**J5 - LVDS 2x15, 2.0 mm (bản LVDS)**

| Chân | Tín hiệu |
|---|---|
| 1 | VLCD |
| 2 | VLCD |
| 3 | VLCD |
| 4 | GND |
| 5 | GND |
| 6 | GND |
| 7 | LVDS_O0- |
| 8 | LVDS_O0+ |
| 9 | LVDS_O1- |
| 10 | LVDS_O1+ |
| 11 | LVDS_O2- |
| 12 | LVDS_O2+ |
| 13 | GND |
| 14 | GND |
| 15 | LVDS_OC- |
| 16 | LVDS_OC+ |
| 17 | LVDS_O3- |
| 18 | LVDS_O3+ |
| 19 | LVDS_E0- |
| 20 | LVDS_E0+ |
| 21 | LVDS_E1- |
| 22 | LVDS_E1+ |
| 23 | LVDS_E2- |
| 24 | LVDS_E2+ |
| 25 | GND |
| 26 | GND |
| 27 | LVDS_EC- |
| 28 | LVDS_EC+ |
| 29 | LVDS_E3- |
| 30 | LVDS_E3+ |

### Cáp cho màn 7" 1024x600 LVDS 20 chân (IPS, 24 bit)

Màn dùng LVDS 1 kênh. Ở chế độ 1 kênh, RTD2660 xuất trên **các cặp E** (J5 chân 19-30), các cặp O không dùng.
Cắm jumper JP1 ở vị trí 1-2 để cấp VDD 3.3 V.

| Chân màn | Tín hiệu màn | Nối vào board |
|---|---|---|
| 1, 2 | VDD 3.3 V | J5 chân 1, 2, 3 (VLCD) |
| 3 | LED_EN | J6 chân 3 (BL_ON) |
| 4, 7, 10, 13, 16 | GND | J5 chân 4, 5, 6, 13, 14, 25, 26 |
| 5 / 6 | RXIN0- / RXIN0+ | J5 chân 19 / 20 (E0- / E0+) |
| 8 / 9 | RXIN1- / RXIN1+ | J5 chân 21 / 22 (E1- / E1+) |
| 11 / 12 | RXIN2- / RXIN2+ | J5 chân 23 / 24 (E2- / E2+) |
| 14 / 15 | CLK- / CLK+ | J5 chân 27 / 28 (EC- / EC+) |
| 17 / 18 | RXIN3- / RXIN3+ | J5 chân 29 / 30 (E3- / E3+) |
| 19 | PWM (độ sáng DC 0.7-1.4 V) | J6 chân 4 (ADJ) |
| 20 | VLED 5-12 V | J6 chân 1 hoặc 2 (+12 V) |

Dây LVDS phải đi theo cặp xoắn: mỗi cặp - và + đi cùng nhau.
Chân ADJ trên J6 ra điện áp DC từ 0 đến 1.41 V. Điện áp này lấy từ xung PWM qua bộ lọc 10k / 7.5k / 1 µF.
Nếu dùng inverter nhận PWM 3.3 V, thay 10k bằng 1k và bỏ 7.5k cùng tụ 1 µF.

**J5 - FPC 40P (bản RGB40)**

| Chân | Tín hiệu |
|---|---|
| 1 | LED_K |
| 2 | LED_A |
| 3 | GND |
| 4 | VLCD |
| 5 | TTL_R0 |
| 13 | TTL_G0 |
| 21 | TTL_B0 |
| 6 | TTL_R1 |
| 14 | TTL_G1 |
| 22 | TTL_B1 |
| 7 | TTL_R2 |
| 15 | TTL_G2 |
| 23 | TTL_B2 |
| 8 | TTL_R3 |
| 16 | TTL_G3 |
| 24 | TTL_B3 |
| 9 | TTL_R4 |
| 17 | TTL_G4 |
| 25 | TTL_B4 |
| 10 | TTL_R5 |
| 18 | TTL_G5 |
| 26 | TTL_B5 |
| 11 | TTL_R6 |
| 19 | TTL_G6 |
| 27 | TTL_B6 |
| 12 | TTL_R7 |
| 20 | TTL_G7 |
| 28 | TTL_B7 |
| 29 | GND |
| 30 | PNL_DCLK |
| 31 | PNL_DISP |
| 32 | TTL_DHS |
| 33 | TTL_DVS |
| 34 | TTL_DEN |
| 35 | NC |
| 36 | GND |
| 37 | TP_XR |
| 38 | TP_YD |
| 39 | TP_XL |
| 40 | TP_YU |

**J5 - FPC 50P (bản RGB50)**

| Chân | Tín hiệu |
|---|---|
| 1 | LED_A |
| 2 | LED_A |
| 3 | LED_K |
| 4 | LED_K |
| 5 | GND |
| 6 | PNL_VCOM |
| 7 | VLCD |
| 8 | PNL_MODE |
| 9 | TTL_DEN |
| 10 | TTL_DVS |
| 11 | TTL_DHS |
| 12 | TTL_B7 |
| 20 | TTL_G7 |
| 28 | TTL_R7 |
| 13 | TTL_B6 |
| 21 | TTL_G6 |
| 29 | TTL_R6 |
| 14 | TTL_B5 |
| 22 | TTL_G5 |
| 30 | TTL_R5 |
| 15 | TTL_B4 |
| 23 | TTL_G4 |
| 31 | TTL_R4 |
| 16 | TTL_B3 |
| 24 | TTL_G3 |
| 32 | TTL_R3 |
| 17 | TTL_B2 |
| 25 | TTL_G2 |
| 33 | TTL_R2 |
| 18 | TTL_B1 |
| 26 | TTL_G1 |
| 34 | TTL_R1 |
| 19 | TTL_B0 |
| 27 | TTL_G0 |
| 35 | TTL_R0 |
| 36 | GND |
| 37 | PNL_DCLK |
| 38 | GND |
| 39 | PNL_LR |
| 40 | PNL_UD |
| 41 | PNL_VGH |
| 42 | PNL_VGL |
| 43 | PNL_AVDD |
| 44 | PNL_RESET |
| 45 | NC |
| 46 | PNL_VCOM |
| 47 | PNL_DITHB |
| 48 | GND |
| 49 | NC |
| 50 | NC |

Các đầu nối khác:

- **J1, nguồn vào 12 V:** 1 = +12V, 2 = GND. Có cầu chì PTC 2 A và diode chống ngược.
- **J4, phím và IR (1x8):** 1 +3V3, 2 GND, 3 KEY_AD0, 4 KEY_AD1, 5 IR, 6 LED_G, 7 LED_R, 8 +5V.
- **J6, bản LVDS, đèn nền (1x6):** 1-2 +12V, 3 BL_ON, 4 ADJ (DC 0-1.41 V từ PWM), 5-6 GND.
- **J6, bản RGB40, cảm ứng điện trở (1x4):** XR, YD, XL, YU.
- **JP1, bản LVDS:** chọn điện áp panel. Nối 1-2 cho 3.3 V, 3-4 cho 5 V, 5-6 cho 12 V. Chỉ cắm MỘT jumper.

## Nguồn

12 V → LM2596S-5.0 → 5 V. Từ 5 V có hai AMS1117-3.3: một cho phần số (PVCC, flash) và một cho phần analog (VDD, VADC).
Từ đó hai AMS1117-1.8 tạo VCCK (lõi) và ADC_VDD.
Nguồn panel được bật bằng MOSFET P qua chân PANEL_ON.

- **Bản RGB:** LED nền dùng boost MT3608 có hồi tiếp dòng. Dòng LED = 0.6 V / R. Mặc định 20 mA cho 40P và 120 mA cho 50P.
- **Bản 50P:** một MT3608 nữa tạo AVDD 10.5 V. Bơm điện tích tạo VGH khoảng 16 V và VGL khoảng -6.8 V. VCOM chỉnh bằng biến trở RV1.

## Gán chân GPIO (firmware phải khớp)

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

## Những điểm cần kiểm tra trước khi đặt mạch

1. **Thạch anh 27 MHz**, giống board tham chiếu PCB800099 của SDK Realtek (`_RTD_XTAL = _XTAL27000K`).
2. **Chân SPI flash.** Tên chân (115 SCLK, 116 SI, 117 SO) và phần mô tả trong datasheet bị lệch nhau ở chân 115/116.
   Mạch đi theo tên chân. Có sẵn cặp điện trở 33R (DNP) để đảo CLK/DI nếu flash không chạy.
3. **Thứ tự chân header VGA 12P.** Phải khớp với mainboard của bạn.
4. **Pinout màn 40P/50P** lấy theo chuẩn phổ biến (AT043TN24, AT070TN92). Dòng LED, mức VGH/VGL/VCOM và các chân MODE/L-R/U-D cần đối chiếu datasheet màn cụ thể.
5. **Footprint.** Footprint FPC, biến trở 3x3 và cuộn cảm là loại chung, cần đối chiếu linh kiện thực tế.
   Pad tản nhiệt của RTD2660 là 7 x 7 mm nối GND; nên thêm via tản nhiệt khi đi dây.
6. **Firmware.** Xem `firmware/README.md`: script áp cấu hình board và màn này lên SDK RTD2660, sau đó biên dịch bằng Keil C51.

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
