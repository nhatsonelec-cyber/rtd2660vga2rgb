# Firmware RTD2660 cho board VGA 12P

RTD2660 không có bộ nhớ chương trình bên trong. Firmware nằm trong flash SPI W25Q40 trên board.
Thư mục này **không chứa mã nguồn của Realtek** vì SDK không kèm giấy phép.
Nó chỉ có script `apply_board.py`, dùng để áp cấu hình của board này lên bản SDK bạn tự tải về.

## 1. Chuẩn bị

- Máy tính Windows có **Keil uVision với C51**. Bản dùng thử của Keil giới hạn 2 KB nên không đủ; cần bản có bản quyền.
- Python 3 để chạy script.
- SDK RTD2660 (project Keil `KR266Xseries.Uv2`), ví dụ:

```bash
git clone https://github.com/danyaPostfactum/RTD2660
```

## 2. Áp cấu hình board

Dùng phiên bản `LVDS` (màn 7" 1024x600). Cấu hình `RGB40` và `RGB50` vẫn còn trong script nhưng tạm chưa dùng.

```bash
python3 apply_board.py RTD2660 LVDS
```

Script làm các việc sau:

- Tạo file board `PCB/PCB_VGA12P.h` từ `PCB800099.h`, rồi chọn nó trong `PCB/Pcb.h`.
- Tạo file màn hình `Panel/PNL_VGA12P_<phiên bản>.h`, rồi chọn nó trong `Panel/Panel.h`.
- Sao lưu mọi file SDK bị sửa thành `*.orig`.

Các thay đổi so với PCB800099:

| Mục | Giá trị cho board này |
|---|---|
| Thạch anh | 27 MHz |
| Nguồn vào | Chỉ VGA (ADC0, DDC1 có EDID) |
| Nguồn panel | Chân 98, P5.4, mức 1 = bật |
| Bật đèn nền | Chân 99, P5.5, mức 1 = bật |
| Độ sáng | Chân 100, PWM4 |
| Phím | Chân 50, ADC0, bàn phím điện trở |
| LED | Chân 52 đỏ (bLED1), chân 53 xanh (bLED2) |
| IR | Chân 113, IrDA |

Màn hình mặc định của từng phiên bản:

| Phiên bản | Màn | Độ phân giải | Tổng H x V | Xung pixel |
|---|---|---|---|---|
| LVDS | 7" IPS 20 chân, 1 kênh, 24 bit | 1024 x 600 | 1344 x 635 | 51.2 MHz |
| RGB40 | AT043TN24, TTL 24 bit | 480 x 272 | 525 x 286 | 9 MHz |
| RGB50 | AT070TN90/92, TTL 24 bit | 800 x 480 | 1056 x 525 | 33.3 MHz |

Nếu dùng màn khác, sửa các giá trị trong bảng `PANELS` của `apply_board.py` rồi chạy lại script.
Các giá trị cần sửa là `_DISP_WID`, `_DISP_LEN`, `_STD_DH_TOTAL`, `_STD_DV_TOTAL`, `_DISP_BIT` và `_DISPLAY_PORT`.

## 3. Biên dịch và tạo file .bin

1. Mở `KR266Xseries.Uv2` bằng Keil uVision.
2. Chọn Project, Rebuild all target files.
3. Chạy `FIRMWARE.BAT` trong thư mục SDK để tạo file `.bin` từ file hex.

## 4. Nạp vào flash

- **Trước khi hàn:** dùng CH341A với kẹp SOIC-8 để ghi file `.bin` vào W25Q40.
- **Sau khi hàn:** nạp qua header J3 (GND, SDA, SCL) bằng RTD ISP Tool và mạch USB-I2C, trong lúc board được cấp nguồn 12 V.

## 5. Nếu hình hiển thị sai

| Hiện tượng | Thử đổi trong file màn |
|---|---|
| Màu đỏ và xanh dương bị đổi chỗ | `_DISP_RB_SWAP` thành `(1 << 5)` |
| Màu sai hoàn toàn, có sọc | `_DISP_ML_SWAP` thành `(1 << 4)` |
| Màn LVDS màu nhạt hoặc sai | `_LVDS_MAP` đổi giữa `_LVDS_MAP1` và `_LVDS_MAP2` |
| Hình rung, chữ nhòe ở màn TTL | `_TTL_DCLK_INVERT` đổi giữa `_ENABLE` và `_DISABLE` |
| Hình bị lệch | `_DH_ACT_STA_POS`, `_DV_ACT_STA_POS` |
| Màn LVDS tối hoàn toàn dù đèn nền sáng | `_DISP_EO_SWAP` thành `(1 << 6)` để xuất ra các cặp O |

## Đã kiểm tra những gì

- Script chạy được trên SDK cho cả ba phiên bản.
- Cả 54 file C của SDK qua được bước tiền xử lý của gcc, các macro board và màn ra đúng giá trị.
- **Chưa biên dịch bằng Keil và chưa chạy trên phần cứng.** Keil chỉ chạy trên Windows và cần bản quyền.
