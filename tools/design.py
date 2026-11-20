"""Single source of truth for the RTD2660 VGA -> TTL RGB (40/50 pin, 7" 1024x600) board.
Every component, its footprint and the net on every pin are defined here; the
schematic (schgen.py) and the PCB (gen_pcb.py) are generated from this file."""
import os
from schgen import Design

HERE = os.path.dirname(os.path.abspath(__file__))
HW = os.path.join(HERE, '..', 'hardware')

d = Design()
d.extra_libs['rtd2660vga2rgb'] = os.path.join(HW, 'rtd2660vga2rgb.kicad_sym')
d.sheets = [
    ('power', 'power.kicad_sch', 'A3', 'Power input, 3V3 / 1V8 rails, LED backlight driver'),
    ('scaler', 'scaler.kicad_sch', 'A3', 'VGA input, RTD2660 scaler, SPI flash, EEPROM, keys'),
    ('panel', 'panel.kicad_sch', 'A3', 'TTL RGB panel connectors (50 pin / 40 pin), panel power and bias'),
]

# ---------------------------------------------------------------- footprints
# passives: 0603 for resistors and small capacitors, 0805 for bulk / high-voltage capacitors
FP_R = 'Resistor_SMD:R_0603_1608Metric'
FP_C = 'Capacitor_SMD:C_0603_1608Metric'
FP_C6 = 'Capacitor_SMD:C_0805_2012Metric'
FP_C8 = 'Capacitor_SMD:C_0805_2012Metric'
FP_RN = 'Resistor_SMD:R_Array_Convex_4x0603'
FP_L3 = 'Inductor_SMD:L_Taiyo-Yuden_NR-30xx'
FP_L4 = 'Inductor_SMD:L_Taiyo-Yuden_NR-40xx'
FP_FB = 'Inductor_SMD:L_0603_1608Metric'
FP_SOD123 = 'Diode_SMD:D_SOD-123'
FP_SOD323 = 'Diode_SMD:D_SOD-323'
FP_SOT23 = 'Package_TO_SOT_SMD:SOT-23'
FP_SOT235 = 'Package_TO_SOT_SMD:SOT-23-5'
FP_SOT236 = 'Package_TO_SOT_SMD:SOT-23-6'
FP_SOIC8 = 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'
FP_JP3 = 'Jumper:SolderJumper-3_P1.3mm_Bridged12_RoundedPad1.0x1.5mm'
FP_JP2 = 'Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm'

# ---------------------------------------------------------------- helpers
def R(ref, val, a, b, sheet, x, y, dnp=False, fp=FP_R, sym='Device:R'):
    """horizontal 2-pin part: net a on the left pin (1), net b on the right pin (2)."""
    return d.add(ref, sym, val, fp, {1: a, 2: b}, sheet, (x, y), rot=90, dnp=dnp,
                 ref_at=(x, y - 2.3, 0, None), val_at=(x, y + 2.4, 0, None))

def C(ref, val, a, b, sheet, x, y, fp=FP_C, dnp=False):
    return R(ref, val, a, b, sheet, x, y, dnp=dnp, fp=fp, sym='Device:C')

def CV(ref, val, top, bot, sheet, x, y, fp=FP_C, sym='Device:C'):
    """vertical 2-pin part: pin 1 on top."""
    return d.add(ref, sym, val, fp, {1: top, 2: bot}, sheet, (x, y), rot=0,
                 ref_at=(x + 1.6, y - 1.3, 0, 'left'), val_at=(x + 1.6, y + 1.5, 0, 'left'))

def title(sheet, x, y, text, size=2.5):
    d.texts.append((sheet, x, y, text, size))

def note(sheet, x, y, text, size=1.4):
    d.texts.append((sheet, x, y, text, size))

def box(sheet, x1, y1, x2, y2):
    d.boxes.append((sheet, x1, y1, x2, y2))

NC = None

# =====================================================================
#  SHEET 1: POWER
# =====================================================================
S1 = 'power'
box(S1, 20, 28, 185, 118); title(S1, 22, 35, '5V INPUT (USB-C or 2-pin header, 5V / 2A)')
d.add('J5', 'Connector:USB_C_Receptacle_PowerOnly_6P', 'USB-C 5V', 'Connector_USB:USB_C_Receptacle_GCT_USB4125-xx-x_6P_TopMnt_Horizontal',
      {'A9': 'VBUS', 'B9': 'VBUS', 'A5': 'USB_CC1', 'B5': 'USB_CC2', 'A12': 'GND', 'B12': 'GND', 'S1': 'GND'},
      S1, (45.72, 63.5), ref_at=(38.1, 45.5, 0, 'left'), val_at=(38.1, 47.8, 0, 'left'))
R('R1', '5.1k', 'USB_CC1', 'GND', S1, 96.52, 68.58)
R('R2', '5.1k', 'USB_CC2', 'GND', S1, 96.52, 76.2)
d.add('J6', 'Connector_Generic:Conn_01x02', '5V IN', 'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',
      {1: 'VBUS', 2: 'GND'}, S1, (48.26, 99.06), ref_at=(48.26, 94.6, 0, None), val_at=(48.26, 105.6, 0, None))
R('F1', '1.5A PTC', 'VBUS', '+5V', S1, 127.0, 55.88, fp='Fuse:Fuse_1206_3216Metric', sym='Device:Polyfuse')
CV('C1', '22uF', '+5V', 'GND', S1, 149.86, 68.58, fp=FP_C8)
CV('C2', '22uF', '+5V', 'GND', S1, 162.56, 68.58, fp=FP_C8)
d.flags += [(S1, 127.0, 78.74, 'VBUS'), (S1, 139.7, 78.74, '+5V'), (S1, 152.4, 96.52, 'GND')]
note(S1, 22, 114, 'R1/R2: USB-C sink Rd. F1 resettable fuse. Total load about 1 A at 5 V with backlight at 180 mA.')

def buck(ref_u, ref_l, r_top, r_bot, c_in, c_o1, c_o2, rtop_val, vout, sw, fb, ox, oy, text):
    box(S1, ox, oy, ox + 165, oy + 52); title(S1, ox + 2, oy + 7, text)
    ux, uy = ox + 45.72, oy + 22.86
    d.add(ref_u, 'Regulator_Switching:TLV62569DBV', 'TLV62569DBV', FP_SOT235,
          {1: '+5V', 2: 'GND', 3: sw, 4: '+5V', 5: fb}, S1, (ux, uy),
          ref_at=(ux - 5, uy - 7.5, 0, 'left'), val_at=(ux - 5, uy - 5.3, 0, 'left'))
    R(ref_l, '2.2uH', sw, vout, S1, ox + 91.44, oy + 17.78, fp=FP_L3, sym='Device:L')
    R(r_top, rtop_val, vout, fb, S1, ox + 91.44, oy + 27.94)
    R(r_bot, '100k', fb, 'GND', S1, ox + 91.44, oy + 38.1)
    CV(c_in, '10uF', '+5V', 'GND', S1, ox + 15.24, oy + 30.48, fp=FP_C6)
    CV(c_o1, '10uF', vout, 'GND', S1, ox + 127.0, oy + 30.48, fp=FP_C6)
    CV(c_o2, '10uF', vout, 'GND', S1, ox + 142.24, oy + 30.48, fp=FP_C6)

buck('U2', 'L1', 'R3', 'R4', 'C3', 'C4', 'C5', '453k', '+3V3', 'SW_3V3', 'FB_3V3', 20, 122,
     '3.3 V BUCK  Vout = 0.6 V x (1 + 453k/100k) = 3.32 V')
buck('U3', 'L2', 'R5', 'R6', 'C6', 'C7', 'C8', '200k', '+1V8', 'SW_1V8', 'FB_1V8', 20, 178,
     '1.8 V BUCK  Vout = 0.6 V x (1 + 200k/100k) = 1.80 V')
d.flags += [(S1, 172.72, 144.78, '+3V3'), (S1, 172.72, 200.66, '+1V8')]

box(S1, 20, 234, 185, 282); title(S1, 22, 241, 'ANALOG RAILS (ADC / PLL supply filters)')
R('FB1', '600R@100MHz', '+3V3', '+3V3A', S1, 55.88, 254.0, fp=FP_FB, sym='Device:FerriteBead_Small')
CV('C9', '10uF', '+3V3A', 'GND', S1, 86.36, 264.16, fp=FP_C6)
R('FB2', '600R@100MHz', '+1V8', '+1V8A', S1, 121.92, 254.0, fp=FP_FB, sym='Device:FerriteBead_Small')
CV('C10', '10uF', '+1V8A', 'GND', S1, 152.4, 264.16, fp=FP_C6)
d.flags += [(S1, 101.6, 259.08, '+3V3A'), (S1, 167.64, 259.08, '+1V8A')]

box(S1, 200, 28, 400, 150); title(S1, 202, 35, 'LED BACKLIGHT DRIVER (constant current boost, 5 V in, up to 38 V out)')
ux, uy = 289.56, 71.12
d.add('U7', 'Driver_LED:TPS61165DBV', 'TPS61165DBV', FP_SOT236,
      {1: '+5V', 2: 'BL_CTRL', 3: 'BL_SW', 4: 'GND', 5: 'BL_COMP', 6: 'BL_FB'}, S1, (ux, uy),
      ref_at=(ux - 5, uy - 10.5, 0, 'left'), val_at=(ux - 5, uy - 8.3, 0, 'left'))
R('L3', '10uH', '+5V', 'BL_SW', S1, 335.28, 45.72, fp=FP_L4, sym='Device:L')
d.add('D1', 'Device:D_Schottky', 'MBR0540', FP_SOD123, {1: 'LEDA', 2: 'BL_SW'}, S1, (335.28, 55.88),
      ref_at=(335.28, 52.6, 0, None), val_at=(335.28, 58.9, 0, None))
C('C11', '1uF 50V', 'LEDA', 'GND', S1, 335.28, 66.04, fp=FP_C6)
R('R45', '6.8k', 'BL_FB', 'LEDK', S1, 335.28, 76.2)
R('R7', '5.1R 1%', 'LEDK', 'GND', S1, 335.28, 86.36)
R('R8', '2.4R 1%', 'LEDK', 'BL_RS2', S1, 335.28, 93.98)
d.add('JP4', 'Jumper:SolderJumper_2_Open', 'BL HIGH', FP_JP2, {1: 'BL_RS2', 2: 'GND'}, S1, (378.46, 93.98),
      ref_at=(378.46, 90.1, 0, None), val_at=(378.46, 97.2, 0, None))
C('C12', '220nF', 'BL_COMP', 'GND', S1, 243.84, 86.36)
CV('C13', '10uF', '+5V', 'GND', S1, 215.9, 66.04, fp=FP_C6)
# on/off: RTD pin 111 low = backlight on (same polarity as PCB800099: inverter stage)
d.add('Q3', 'Transistor_FET:2N7002', '2N7002', FP_SOT23, {1: 'BL_EN_N', 2: 'GND', 3: 'BL_CTRL'}, S1, (238.76, 106.68),
      ref_at=(244.5, 104.7, 0, 'left'), val_at=(244.5, 107.7, 0, 'left'))
R('R9', '10k', 'BL_EN_N', '+3V3', S1, 289.56, 99.06)
R('R10', '10k', 'BL_CTRL', '+3V3', S1, 289.56, 106.68)
R('R11', '1k', 'BL_PWM', 'BL_CTRL', S1, 289.56, 114.3, dnp=True)
# analog dimming: filtered PWM0 (pin 102) summed into FB, as on PCB800099
R('R46', '10k', 'BL_PWM', 'BL_DIM', S1, 335.28, 106.68)
C('C14', '100nF', 'BL_DIM', 'GND', S1, 335.28, 114.3)
R('R47', '100k', 'BL_DIM', 'BL_FB', S1, 378.46, 106.68)
note(S1, 202, 126, 'I_LED(max) = 0.214 V / Rset.  R7 only: 42 mA (JP4 open, default).  JP4 closed (R7 || R8 = 1.63R): 131 mA.')
note(S1, 202, 130, 'Typical 7" 1024x600 50-pin panels: 9.6 V, 120-140 mA (3 LEDs in series x 6-7 strings). Check your panel, then close JP4.')
note(S1, 202, 134, 'BL_EN_N (RTD pin 111) low = on: Q3 releases CTRL.  R9 keeps the backlight off while the RTD2660 is in reset.')
note(S1, 202, 138, 'Dimming: PWM0 (RTD pin 102) is filtered by R46/C14 and summed into FB by R47: higher duty = dimmer, 100 % = off.')
note(S1, 202, 142, 'For direct PWM on CTRL (5-100 kHz) remove R10 and R47 and fit R11.  Open-LED clamp is 38 V: C11, D1 rated >= 40 V.')
for i in range(4):
    d.add('H%d' % (i + 1), 'Mechanical:MountingHole', 'M2', 'MountingHole:MountingHole_2.2mm_M2', {}, S1,
          (220.98 + i * 15.24, 170.18), ref_at=(220.98 + i * 15.24, 165.6, 0, None), val_at=(220.98 + i * 15.24, 174.2, 0, None))
title(S1, 202, 160, 'MOUNTING HOLES')

# =====================================================================
#  SHEET 2: SCALER
# =====================================================================
S2 = 'scaler'
title(S2, 20, 22, 'VGA INPUT + ANALOG FRONT END')
jx, jy = 48.26, 60.96
d.add('J1', 'Connector:DE15_Receptacle_HighDensity_MountingHoles', 'VGA DE-15 F',
      'Connector_Dsub:DSUB-15-HD_Female_Horizontal_P2.29x1.98mm_EdgePinOffset3.03mm_Housed_MountingHolesOffset4.94mm',
      {0: 'GND', 1: 'VGA_R', 2: 'VGA_G', 3: 'VGA_B', 4: NC, 5: 'GND', 6: 'GND', 7: 'GND', 8: 'GND', 9: NC, 10: 'GND',
       11: NC, 12: 'VGA_SDA', 13: 'VGA_HS', 14: 'VGA_VS', 15: 'VGA_SCL'}, S2, (jx, jy),
      ref_at=(jx, jy - 22.5, 0, None), val_at=(jx, jy - 20.2, 0, None))
ax, ay, p = 99.06, 33.02, 7.62
R('R12', '75R', 'VGA_R', 'GND', S2, ax, ay)
R('R13', '75R', 'VGA_G', 'GND', S2, ax, ay + p)
R('R14', '75R', 'VGA_B', 'GND', S2, ax, ay + 2 * p)
R('R50', '100R', 'VGA_R', 'RIN_C', S2, ax, ay + 3 * p)
R('R51', '100R', 'VGA_G', 'GIN_C', S2, ax, ay + 4 * p)
R('R52', '100R', 'VGA_B', 'BIN_C', S2, ax, ay + 5 * p)
R('R53', '100R', 'GND', 'RINN_C', S2, ax, ay + 6 * p)
R('R54', '100R', 'GND', 'GINN_C', S2, ax, ay + 7 * p)
R('R55', '100R', 'GND', 'BINN_C', S2, ax, ay + 8 * p)
C('C26', '1nF', 'VGA_G', 'SOG_IN', S2, ax, ay + 9 * p)
bx = 139.7
C('C20', '47nF', 'RIN_C', 'RIN_P', S2, bx, ay)
C('C21', '47nF', 'RINN_C', 'RIN_N', S2, bx, ay + p)
C('C22', '47nF', 'GIN_C', 'GIN_P', S2, bx, ay + 2 * p)
C('C23', '47nF', 'GINN_C', 'GIN_N', S2, bx, ay + 3 * p)
C('C24', '47nF', 'BIN_C', 'BIN_P', S2, bx, ay + 4 * p)
C('C25', '47nF', 'BINN_C', 'BIN_N', S2, bx, ay + 5 * p)
R('R15', '100R', 'VGA_HS', 'HS_IN', S2, bx, ay + 6 * p)
R('R16', '100R', 'VGA_VS', 'VS_IN', S2, bx, ay + 7 * p)
R('R17', '10k', 'HS_IN', 'GND', S2, bx, ay + 8 * p)
R('R18', '10k', 'VS_IN', 'GND', S2, bx, ay + 9 * p)
R('R19', '33R', 'VGA_SCL', 'DDC_SCL', S2, bx, ay + 10 * p)
R('R20', '33R', 'VGA_SDA', 'DDC_SDA', S2, bx, ay + 11 * p)
R('R21', '4.7k', 'DDC_SCL', '+3V3', S2, bx, ay + 12 * p)
R('R22', '4.7k', 'DDC_SDA', '+3V3', S2, ax, ay + 12 * p)
note(S2, 20, 112, 'RGB: 75R termination, 100R + 47nF AC coupling into the')
note(S2, 20, 115.5, 'differential ADC inputs; negative inputs return to VGA ground.')
note(S2, 20, 119, 'DDC pins 58/59 carry EDID (RTD2660 DDC RAM) and the Realtek')
note(S2, 20, 122.5, 'ISP protocol: firmware can be flashed through the VGA cable.')

title(S2, 20, 140, 'CRYSTAL, RESET, STRAPS')
d.add('Y1', 'Device:Crystal_GND24', '27.000MHz', 'Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm',
      {1: 'XI', 2: 'GND', 3: 'XO', 4: 'GND'}, S2, (48.26, 160.02),
      ref_at=(55.5, 155.2, 0, 'left'), val_at=(55.5, 165.2, 0, 'left'))
C('C27', '22pF', 'XI', 'GND', S2, 99.06, 149.86)
C('C28', '22pF', 'XO', 'GND', S2, 99.06, 157.48)
R('R56', '1M', 'XI', 'XO', S2, 99.06, 165.1)
R('R23', '4.7k', 'RESETB', '+3V3', S2, 99.06, 175.26)
C('C29', '100nF', 'RESETB', 'GND', S2, 99.06, 182.88)
R('R24', '27k', 'CEC', '+3V3', S2, 139.7, 149.86)
R('R25', '1k', 'RTD_REXT', '+3V3A', S2, 139.7, 157.48)
R('R26', '10k', 'FLASH_CS', 'GND', S2, 139.7, 165.1)
note(S2, 20, 193, 'R26: SPI_CEB strap, low at reset = embedded MCU (datasheet pin 118 note).')
note(S2, 20, 196.5, 'R25: pin 2 reference resistor, 1k to VDD as on PCB800099-type boards.')
note(S2, 20, 200, 'R24: CEC pull-up required by the datasheet even when CEC is unused.')
note(S2, 20, 203.5, 'RTD2660 has an internal low-voltage reset; R23/C29 only add a short delay.')

title(S2, 20, 214, 'RTD2660 DECOUPLING (place one 100nF at each supply pin)')
cx, cy = 27.94, 236.22
caps = [('C30', '100nF', '+3V3A'), ('C31', '100nF', '+3V3A'), ('C32', '100nF', '+3V3A'), ('C33', '1uF', '+3V3A'),
        ('C34', '100nF', '+1V8A'), ('C35', '1uF', '+1V8A'),
        ('C36', '100nF', '+1V8'), ('C37', '100nF', '+1V8'), ('C38', '100nF', '+1V8'), ('C39', '10uF', '+1V8'),
        ('C40', '100nF', '+3V3'), ('C41', '100nF', '+3V3'), ('C42', '100nF', '+3V3'), ('C43', '10uF', '+3V3')]
for i, (ref, val, net) in enumerate(caps):
    CV(ref, val, net, 'GND', S2, cx + (i % 7) * 20.32, cy + (i // 7) * 30.48, fp=FP_C6 if val == '10uF' else FP_C)

# --- RTD2660
U1X, U1Y = 215.9, 149.86
u1 = {
    1: '+3V3A', 20: '+3V3A', 49: '+3V3A', 23: '+1V8A', 60: '+1V8', 73: '+1V8', 120: '+1V8',
    62: '+3V3', 84: '+3V3', 106: '+3V3', 11: 'GND', 38: 'GND', 61: 'GND', 85: 'GND', 107: 'GND', 129: 'GND',
    2: 'RTD_REXT',
    30: 'RIN_P', 29: 'RIN_N', 27: 'GIN_P', 26: 'GIN_N', 28: 'SOG_IN', 25: 'BIN_P', 24: 'BIN_N',
    22: 'HS_IN', 21: 'VS_IN', 39: 'GND', 40: 'GND',
    128: 'XI', 127: 'XO', 125: 'RESETB', 126: 'CEC',
    118: 'FLASH_CS', 115: 'FLASH_CLK', 116: 'FLASH_DI', 117: 'FLASH_DO',
    58: 'DDC_SCL', 59: 'DDC_SDA', 56: 'EE_SCL', 57: 'EE_SDA',
    96: 'T_CLK', 94: 'T_DE', 95: 'T_HS', 97: 'T_VS',
    # TTL data wired like PCB800099 (stock firmware uses RB_SWAP | ML_SWAP):
    66: 'T_R0', 67: 'T_R1', 68: 'T_R2', 69: 'T_R3', 70: 'T_R4', 71: 'T_R5', 74: 'T_R6', 75: 'T_R7',
    76: 'T_G0', 77: 'T_G1', 78: 'T_G2', 79: 'T_G3', 80: 'T_G4', 81: 'T_G5', 82: 'T_G6', 83: 'T_G7',
    86: 'T_B0', 87: 'T_B1', 88: 'T_B2', 89: 'T_B3', 90: 'T_B4', 91: 'T_B5', 92: 'T_B6', 93: 'T_B7',
    102: 'BL_PWM', 110: 'PANEL_ON', 111: 'BL_EN_N',
    53: 'KEY_AD', 52: 'LED1', 65: 'LED2', 64: 'IR_IN',
}
for n in range(1, 130):
    u1.setdefault(n, NC)
d.add('U1', 'rtd2660vga2rgb:RTD2660', 'RTD2660', 'rtd2660vga2rgb:LQFP-128-1EP_14x20mm_P0.5mm_EP7.1x7.1mm', u1, S2, (U1X, U1Y), power_syms=False,
      ref_at=(U1X - 27.94, U1Y - 88.3, 0, 'left'), val_at=(U1X + 17, U1Y + 88.3, 0, 'left'))
note(S2, 150, 26, 'TTL data follows the PCB800099 wiring so stock TTL firmware works: panel R0..R5 = pins 66..71, R6/R7 = 74/75,')
note(S2, 150, 29.5, 'G0..G7 = 76..83, B0..B7 = 86..93, DEN = 94, DHS = 95, DCLK = 96, DVS = 97 (firmware: _DISP_RB_SWAP | _DISP_ML_SWAP, 24-bit).')
note(S2, 150, 33, 'Control pins as PCB800099: 110 = panel power (high = on), 111 = backlight (low = on), 102 = PWM0 dimming, 53 = ADC keys.')

# --- flash / eeprom / keys
title(S2, 290, 22, 'SPI FLASH (firmware)')
fx, fy = 335.28, 50.8
d.add('U4', 'Memory_Flash:W25X40CLSN', 'W25X40CL / W25Q80', FP_SOIC8,
      {1: 'FLASH_CS', 2: 'FLASH_DO', 3: '+3V3', 4: 'GND', 5: 'FLASH_DI', 6: 'FLASH_CLK', 7: '+3V3', 8: '+3V3'},
      S2, (fx, fy), ref_at=(fx + 2, fy - 11.5, 0, 'left'), val_at=(fx + 2, fy + 11.5, 0, 'left'))
CV('C44', '100nF', '+3V3', 'GND', S2, 299.72, 50.8)
d.add('J4', 'Connector_Generic:Conn_01x07', 'FLASH PROG', 'Connector_PinHeader_1.27mm:PinHeader_1x07_P1.27mm_Vertical',
      {1: '+3V3', 2: 'FLASH_CS', 3: 'FLASH_DO', 4: 'FLASH_DI', 5: 'FLASH_CLK', 6: 'GND', 7: 'RESETB'}, S2, (391.16, 45.72),
      ref_at=(391.16, 37.5, 0, None), val_at=(393.5, 58.5, 0, None))
note(S2, 290, 72, 'J4: in-circuit programming of U4 (hold RESETB, pin 7, low while programming).')

title(S2, 290, 84, 'SETTINGS EEPROM (optional, 0xA0)')
ex, ey = 335.28, 104.14
d.add('U5', 'Memory_EEPROM:24LC16', '24C16', FP_SOIC8,
      {1: 'GND', 2: 'GND', 3: 'GND', 4: 'GND', 5: 'EE_SDA', 6: 'EE_SCL', 7: 'GND', 8: '+3V3'}, S2, (ex, ey),
      ref_at=(ex + 2, ey - 9.5, 0, 'left'), val_at=(ex + 2, ey + 9.5, 0, 'left'))
CV('C45', '100nF', '+3V3', 'GND', S2, 299.72, 104.14)

title(S2, 290, 128, 'KEYPAD (ADC ladder) / LED / IR HEADER')
kx, ky = 335.28, 149.86
d.add('J7', 'Connector_Generic:Conn_02x05_Odd_Even', 'KEYPAD', 'Connector_PinHeader_1.27mm:PinHeader_2x05_P1.27mm_Vertical_SMD',
      {1: '+3V3', 2: 'GND', 3: 'KEY_LAD', 4: 'K_MENU', 5: 'K_UP', 6: 'K_DOWN', 7: 'K_SRC', 8: 'LED1', 9: 'LED2', 10: 'IR_IN'},
      S2, (kx, ky), ref_at=(kx + 1.27, ky - 9, 0, None), val_at=(kx + 1.27, ky + 9, 0, None))
R('R27', '4.7k', 'EE_SCL', '+3V3', S2, 383.54, 99.06)
R('R28', '4.7k', 'EE_SDA', '+3V3', S2, 383.54, 106.68)
R('R29', '4.7k', 'KEY_LAD', '+3V3', S2, 302.26, 170.18)
R('R30', '100R', 'KEY_LAD', 'KEY_AD', S2, 302.26, 177.8)
C('C46', '100nF', 'KEY_AD', 'GND', S2, 302.26, 185.42)
R('R57', '1k', 'KEY_LAD', 'K_MENU', S2, 342.9, 170.18)
R('R58', '2k', 'KEY_LAD', 'K_UP', S2, 342.9, 177.8)
R('R59', '3.9k', 'KEY_LAD', 'K_DOWN', S2, 342.9, 185.42)
R('R60', '10k', 'KEY_LAD', 'K_SRC', S2, 342.9, 193.04)
R('R61', '1k', 'LED1', '+3V3', S2, 383.54, 170.18)
R('R62', '1k', 'LED2', '+3V3', S2, 383.54, 177.8)
R('R31', '33R', 'LED1', 'LED_A', S2, 383.54, 185.42)
d.add('D7', 'Device:LED', 'GREEN', 'LED_SMD:LED_0603_1608Metric', {1: 'GND', 2: 'LED_A'}, S2, (383.54, 195.58),
      ref_at=(383.54, 192.1, 0, None), val_at=(383.54, 199.1, 0, None))
R('R63', '10k', 'IR_IN', '+3V3', S2, 302.26, 195.58)
note(S2, 290, 208, 'J7: 1 +3V3  2 GND  3 POWER  4 MENU  5 UP  6 DOWN  7 SOURCE  8 LED1  9 LED2  10 IR')
note(S2, 290, 211.5, 'Keys are plain switches to GND: the PCB800099 ADC ladder (0R / 1k / 2k / 3.9k / 10k')
note(S2, 290, 215, 'against the 4.7k pull-up R29) is on this board, read by RTD pin 53 (A-ADC3).')
note(S2, 290, 218.5, 'LED1 = RTD pin 52, LED2 = pin 65: pin high = LED on (LED from header pin to GND).')
note(S2, 290, 222, 'IR receiver output to pin 10 (RTD pin 64).')

# =====================================================================
#  SHEET 3: PANEL
# =====================================================================
S3 = 'panel'
title(S3, 20, 22, 'TTL SERIES TERMINATION (33R)')
rn = [('RN1', ['R0', 'R1', 'R2', 'R3']), ('RN2', ['R4', 'R5', 'R6', 'R7']),
      ('RN3', ['G0', 'G1', 'G2', 'G3']), ('RN4', ['G4', 'G5', 'G6', 'G7']),
      ('RN5', ['B0', 'B1', 'B2', 'B3']), ('RN6', ['B4', 'B5', 'B6', 'B7']),
      ('RN7', ['DE', 'HS', 'CLK', 'VS'])]
for i, (ref, sig) in enumerate(rn):
    y = 38.1 + i * 17.78
    # rot 90: pins 8,7,6,5 on the left (bottom to top), 1,2,3,4 on the right
    d.add(ref, 'Device:R_Pack04', '33R', FP_RN,
          {8: 'T_' + sig[0], 7: 'T_' + sig[1], 6: 'T_' + sig[2], 5: 'T_' + sig[3],
           1: 'LCD_' + sig[0], 2: 'LCD_' + sig[1], 3: 'LCD_' + sig[2], 4: 'LCD_' + sig[3]},
          S3, (50.8, y), rot=90, ref_at=(50.8, y - 7.3, 0, None), val_at=(50.8, y + 7.6, 0, None))

title(S3, 100, 22, 'J2: 50-PIN FPC (bottom side)')
j2 = {1: 'LEDA', 2: 'LEDA', 3: 'LEDK', 4: 'LEDK', 5: 'GND', 6: 'VCOM', 7: 'LCD_3V3', 8: 'LCD_MODE',
      9: 'LCD_DE', 10: 'LCD_VS', 11: 'LCD_HS',
      36: 'GND', 37: 'LCD_CLK', 38: 'GND', 39: 'LCD_SHLR', 40: 'LCD_UPDN', 41: 'VGH', 42: 'VGL', 43: 'AVDD',
      44: 'LCD_RESET', 45: NC, 46: 'VCOM', 47: 'LCD_DITHB', 48: 'GND', 49: NC, 50: NC, 'MP': 'GND'}
for i in range(8):
    j2[12 + i] = 'LCD_B%d' % (7 - i)
    j2[20 + i] = 'LCD_G%d' % (7 - i)
    j2[28 + i] = 'LCD_R%d' % (7 - i)
d.add('J2', 'Connector_Generic_MountingPin:Conn_01x50_MountingPin', 'FPC-50 0.5mm',
      'Connector_FFC-FPC:Hirose_FH12-50S-0.5SH_1x50-1MP_P0.50mm_Horizontal', j2, S3, (132.08, 96.52),
      ref_at=(133.5, 31.5, 0, None), val_at=(140, 165.5, 0, 'left'))

title(S3, 185, 22, 'J3: 40-PIN FPC (top side)')
j3 = {1: 'LEDK', 2: 'LEDA', 3: 'GND', 4: 'LCD_3V3', 29: 'GND', 30: 'LCD_CLK', 31: 'LCD_DISP', 32: 'LCD_HS',
      33: 'LCD_VS', 34: 'LCD_DE', 35: NC, 36: 'GND', 37: NC, 38: NC, 39: NC, 40: NC, 'MP': 'GND'}
for i in range(8):
    j3[5 + i] = 'LCD_R%d' % i
    j3[13 + i] = 'LCD_G%d' % i
    j3[21 + i] = 'LCD_B%d' % i
d.add('J3', 'Connector_Generic_MountingPin:Conn_01x40_MountingPin', 'FPC-40 0.5mm',
      'Connector_FFC-FPC:Hirose_FH12-40S-0.5SH_1x40-1MP_P0.50mm_Horizontal', j3, S3, (213.36, 83.82),
      ref_at=(214.8, 31.5, 0, None), val_at=(221, 140, 0, 'left'))
note(S3, 100, 176, 'J2 pinout from the panel interface table supplied for this project (VLED+ 1-2, VLED- 3-4, ... DITHB 47).')
note(S3, 100, 179.5, 'J3: common 40-pin RGB pinout (LEDK 1, LEDA 2, VCC 4, R0-R7 5-12, G0-G7 13-20, B0-B7 21-28, CLK 30,')
note(S3, 100, 183, 'DISP 31, HS 32, VS 33, DE 34, touch 37-40 NC). VERIFY against your panel datasheet before use.')
note(S3, 100, 186.5, 'Fit only ONE of J2 / J3.  J3 is on the top side, J2 on the bottom side under it.  Check the FPC contact side of your panel.')

title(S3, 270, 22, 'PANEL STRAPS')
def strap(ref, val, x, y, n1, sig, n3):
    d.add(ref, 'Jumper:SolderJumper_3_Bridged12', val, FP_JP3, {1: n1, 2: sig, 3: n3}, S3, (x, y),
          ref_at=(x - 2, y - 4.8, 0, 'right'), val_at=(x + 2, y - 4.8, 0, 'left'))
strap('JP1', 'MODE', 289.56, 38.1, 'LCD_3V3', 'LCD_MODE', 'GND')
strap('JP2', 'SHLR', 332.74, 38.1, 'LCD_3V3', 'LCD_SHLR', 'GND')
strap('JP3', 'UPDN', 375.92, 38.1, 'GND', 'LCD_UPDN', 'LCD_3V3')
strap('JP5', 'DITHB', 289.56, 68.58, 'GND', 'LCD_DITHB', 'LCD_3V3')
R('R33', '10k', 'LCD_RESET', 'LCD_3V3', S3, 337.82, 66.04)
C('C50', '1uF', 'LCD_RESET', 'GND', S3, 337.82, 73.66)
R('R34', '10k', 'LCD_DISP', 'LCD_3V3', S3, 386.08, 66.04)
note(S3, 270, 92, 'Defaults (bridged pads 1-2): MODE = H (DE mode), SHLR = H, UPDN = L (normal scan), DITHB = L (8-bit).')
note(S3, 270, 95.5, 'Cut the bridged side and solder the other side to change a strap.  R33/C50: panel reset RC.')

title(S3, 270, 106, 'PANEL LOGIC SUPPLY SWITCH')
d.add('Q1', 'Transistor_FET:AO3401A', 'AO3401A', FP_SOT23, {1: 'PANEL_G', 2: '+3V3', 3: 'LCD_3V3'}, S3, (287.02, 124.46),
      ref_at=(292.5, 122.5, 0, 'left'), val_at=(292.5, 125.5, 0, 'left'))
d.add('Q2', 'Transistor_FET:2N7002', '2N7002', FP_SOT23, {1: 'PANEL_ON', 2: 'GND', 3: 'PANEL_SW'}, S3, (287.02, 160.02),
      ref_at=(292.5, 158.0, 0, 'left'), val_at=(292.5, 161.0, 0, 'left'))
R('R35', '100k', 'PANEL_G', '+3V3', S3, 350.52, 114.3)
R('R36', '10k', 'PANEL_SW', 'PANEL_G', S3, 350.52, 121.92)
C('C51', '100nF', 'PANEL_G', '+3V3', S3, 350.52, 129.54)
R('R32', '100k', 'PANEL_ON', 'GND', S3, 350.52, 160.02)
CV('C52', '10uF', 'LCD_3V3', 'GND', S3, 386.08, 121.92, fp=FP_C6)
CV('C53', '100nF', 'LCD_3V3', 'GND', S3, 398.78, 121.92)
d.flags += [(S3, 322.58, 132.08, 'LCD_3V3')]
note(S3, 300, 172, 'PANEL_ON (RTD pin 110) high = panel on, as on PCB800099.')
note(S3, 300, 175.5, 'R36/C51 slow the turn-on (about 1 ms) to limit inrush.')

title(S3, 20, 200, 'PANEL BIAS (50-pin panels only): AVDD boost, VGH / VGL charge pumps, VCOM buffer')
ux, uy = 55.88, 226.06
d.add('U6', 'Regulator_Switching:MT3608', 'MT3608', FP_SOT236,
      {1: 'BIAS_SW', 2: 'GND', 3: 'BIAS_FB', 4: 'BIAS_EN', 5: 'LCD_3V3', 6: NC}, S3, (ux, uy),
      ref_at=(ux - 5, uy - 7.5, 0, 'left'), val_at=(ux - 5, uy - 5.3, 0, 'left'))
R('L4', '10uH', 'LCD_3V3', 'BIAS_SW', S3, 96.52, 210.82, fp=FP_L4, sym='Device:L')
d.add('D2', 'Device:D_Schottky', 'MBR0540', FP_SOD123, {1: 'AVDD', 2: 'BIAS_SW'}, S3, (96.52, 220.98),
      ref_at=(96.52, 217.7, 0, None), val_at=(96.52, 224.0, 0, None))
R('R37', '150k', 'AVDD', 'BIAS_FB', S3, 96.52, 231.14)
R('R38', '10k', 'BIAS_FB', 'GND', S3, 96.52, 238.76)
R('R39', '10k', 'LCD_3V3', 'BIAS_EN', S3, 96.52, 248.92)
C('C54', '100nF', 'BIAS_EN', 'GND', S3, 96.52, 256.54)
CV('C55', '10uF', 'LCD_3V3', 'GND', S3, 27.94, 251.46, fp=FP_C6)
CV('C56', '10uF 25V', 'AVDD', 'GND', S3, 43.18, 251.46, fp=FP_C8)
d.flags += [(S3, 58.42, 248.92, 'AVDD')]
note(S3, 20, 273, 'AVDD = 0.6 V x (1 + R37/R38) = 9.6 V (typical for 1024x600 50-pin panels).  AT070TN92 needs 10.4 V: R37 = 162k.')
note(S3, 20, 276.5, 'U6 runs from the switched LCD_3V3, so AVDD/VGH/VGL are off whenever the panel logic supply is off.')

C('C57', '100nF 50V', 'BIAS_SW', 'CP_H', S3, 152.4, 210.82)
d.add('D3', 'Diode:BAT54S', 'BAT54S', FP_SOT23, {1: 'AVDD', 2: 'VGH_RAW', 3: 'CP_H'}, S3, (152.4, 223.52),
      ref_at=(152.4, 218.7, 0, None), val_at=(160, 227.5, 0, 'left'))
C('C58', '1uF 50V', 'VGH_RAW', 'GND', S3, 152.4, 238.76, fp=FP_C6)
R('R40', '1k', 'VGH_RAW', 'VGH', S3, 152.4, 246.38)
d.add('D4', 'Device:D_Zener', '18V BZT52C18S', FP_SOD323, {1: 'VGH', 2: 'GND'}, S3, (152.4, 254.0),
      ref_at=(152.4, 250.7, 0, None), val_at=(152.4, 257.0, 0, None))
C('C59', '1uF 50V', 'VGH', 'GND', S3, 152.4, 264.16, fp=FP_C6)

C('C60', '100nF 50V', 'BIAS_SW', 'CP_L', S3, 205.74, 210.82)
d.add('D5', 'Diode:BAT54S', 'BAT54S', FP_SOT23, {1: 'VGL_RAW', 2: 'GND', 3: 'CP_L'}, S3, (205.74, 223.52),
      ref_at=(205.74, 218.7, 0, None), val_at=(213.5, 227.5, 0, 'left'))
C('C61', '1uF 50V', 'GND', 'VGL_RAW', S3, 205.74, 238.76, fp=FP_C6)
R('R41', '1k', 'VGL_RAW', 'VGL', S3, 205.74, 246.38)
d.add('D6', 'Device:D_Zener', '6.2V BZT52C6V2S', FP_SOD323, {1: 'GND', 2: 'VGL'}, S3, (205.74, 254.0),
      ref_at=(205.74, 250.7, 0, None), val_at=(205.74, 257.0, 0, None))
C('C62', '1uF 50V', 'GND', 'VGL', S3, 205.74, 264.16, fp=FP_C6)
note(S3, 20, 280, 'VGH = 2 x AVDD - 0.6 V = 18.6 V, clamped by D4 (18 V).  VGL = -(AVDD - 0.6 V), clamped by D6 (-6.2 V).  Change D4/D6 to match the panel.')

R('R42', '20k', 'AVDD', 'VCOM_HI', S3, 259.08, 210.82)
d.add('RV1', 'Device:R_Potentiometer_Trim', '10k', 'Potentiometer_SMD:Potentiometer_Bourns_TC33X_Vertical',
      {1: 'VCOM_HI', 2: 'VCOM_REF', 3: 'VCOM_LO'}, S3, (259.08, 228.6),
      ref_at=(254, 227.5, 0, 'right'), val_at=(254, 230, 0, 'right'))
R('R43', '5.1k', 'VCOM_LO', 'GND', S3, 259.08, 246.38)
C('C63', '100nF', 'VCOM_REF', 'GND', S3, 259.08, 254.0)
ox, oy = 322.58, 228.6
d.add('U8', 'Amplifier_Operational:LMV321', 'LMV321', FP_SOT235,
      {1: 'VCOM_REF', 2: 'GND', 3: 'VCOM_BUF', 4: 'VCOM_BUF', 5: '+5V'}, S3, (ox, oy),
      ref_at=(ox + 2, oy - 6, 0, 'left'), val_at=(ox + 2, oy + 6, 0, 'left'))
R('R44', '22R', 'VCOM_BUF', 'VCOM', S3, 373.38, 220.98)
C('C64', '1uF', 'VCOM', 'GND', S3, 373.38, 228.6)
C('C65', '100nF', '+5V', 'GND', S3, 373.38, 238.76)
note(S3, 20, 283.5, 'VCOM adjustable 1.4 ... 4.1 V with RV1 (typ. 3.2-3.9 V): trim for minimum flicker.')

ROOT_NOTES = [
    'RTD2660 VGA -> TTL RGB controller for 7" 1024x600 TFT (50-pin / 40-pin FPC)',
    '',
    'Sheet 2: 5 V input, 3.3 V and 1.8 V bucks, analog rail filters, LED backlight boost',
    'Sheet 3: VGA connector and analog front end, RTD2660, SPI flash, EEPROM, keypad header',
    'Sheet 4: 33R series arrays, FPC connectors, panel supply switch, AVDD/VGH/VGL/VCOM',
    '',
    'All sheets are connected with global labels.',
    'The schematic and PCB are generated from tools/design.py.',
]
