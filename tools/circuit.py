"""Circuit description of the RTD2660 driver board and its three output variants.

Input : VGA (analog RGB) on a 1 x 12 pin 2.54 mm header (no DB15).
Output: LVDS on a 2 x 15 pin 2.0 mm header, or TTL RGB 24-bit on a 40-pin / 50-pin 0.5 mm FPC.
"""
from eaglelib import Design
from parts import RTD_PINS

# 1 x 12 pin 2.54 mm VGA header pinout (edit here if the mainboard header differs).
VGA12_PINOUT = {
    1: "VGA_R", 2: "GND", 3: "VGA_G", 4: "GND", 5: "VGA_B", 6: "GND",
    7: "VGA_HS", 8: "VGA_VS", 9: "GND", 10: "VGA_SDA", 11: "VGA_SCL", 12: "VGA_5V",
}

# 1 x 20 pin 2.0 mm LVDS connector: pins 1-18 follow the 7" 1024x600 IPS LVDS panel (Huadi).
# The panel cable brings the backlight (VLED, LED_EN, brightness, GND) out on a separate
# 4-pin plug, so pins 19/20 are not used here; see BL4_PINOUT.
LVDS20_PINOUT = {
    1: "VLCD", 2: "VLCD", 3: "PNL_LED_EN", 4: "GND", 5: "LVDS_E0-", 6: "LVDS_E0+", 7: "GND",
    8: "LVDS_E1-", 9: "LVDS_E1+", 10: "GND", 11: "LVDS_E2-", 12: "LVDS_E2+", 13: "GND",
    14: "LVDS_EC-", 15: "LVDS_EC+", 16: "GND", 17: "LVDS_E3-", 18: "LVDS_E3+",
    19: None, 20: None,
}

# 1 x 4 pin 2.0 mm backlight connector (white 4-pin plug of the panel cable).
# Order is an assumption: check the cable with a multimeter (VLED / EN / PWM / GND).
BL4_PINOUT = {1: "+12V", 2: "PNL_LED_EN", 3: "PNL_BL_ADJ", 4: "GND"}

# 40-pin TTL RGB (AT043TN24 / 4.3"-7" 40P standard pinout)
RGB40_PINOUT = {1: "LED_K", 2: "LED_A", 3: "GND", 4: "VLCD"}
for i in range(8):
    RGB40_PINOUT[5 + i] = "TTL_R%d" % i
    RGB40_PINOUT[13 + i] = "TTL_G%d" % i
    RGB40_PINOUT[21 + i] = "TTL_B%d" % i
RGB40_PINOUT.update({29: "GND", 30: "PNL_DCLK", 31: "PNL_DISP", 32: "TTL_DHS", 33: "TTL_DVS",
                     34: "TTL_DEN", 35: None, 36: "GND", 37: "TP_XR", 38: "TP_YD", 39: "TP_XL",
                     40: "TP_YU", "MP1": "GND", "MP2": "GND"})

# 50-pin TTL RGB (AT070TN90 / AT070TN92 7" 800x480 standard pinout)
RGB50_PINOUT = {1: "LED_A", 2: "LED_A", 3: "LED_K", 4: "LED_K", 5: "GND", 6: "PNL_VCOM",
                7: "VLCD", 8: "PNL_MODE", 9: "TTL_DEN", 10: "TTL_DVS", 11: "TTL_DHS"}
for i in range(8):
    RGB50_PINOUT[12 + i] = "TTL_B%d" % (7 - i)
    RGB50_PINOUT[20 + i] = "TTL_G%d" % (7 - i)
    RGB50_PINOUT[28 + i] = "TTL_R%d" % (7 - i)
RGB50_PINOUT.update({36: "GND", 37: "PNL_DCLK", 38: "GND", 39: "PNL_LR", 40: "PNL_UD",
                     41: "PNL_VGH", 42: "PNL_VGL", 43: "PNL_AVDD", 44: "PNL_RESET", 45: None,
                     46: "PNL_VCOM", 47: "PNL_DITHB", 48: "GND", 49: None, 50: None,
                     "MP1": "GND", "MP2": "GND"})

# RTD2660 GPIO usage (firmware must match)
GPIO_MAP = [
    ("50", "P6.0 / A-ADC0", "KEY_AD0", "Keypad resistor ladder 1 (ADC)"),
    ("51", "P6.1 / A-ADC1", "KEY_AD1", "Keypad resistor ladder 2 (ADC)"),
    ("52", "P6.2", "LED_R_DRV", "Red / standby LED, active high"),
    ("53", "P6.3", "LED_G_DRV", "Green / power LED, active high"),
    ("58", "DDCSCL1 (P3.0)", "DDC_SCL", "VGA DDC clock, ISP programming"),
    ("59", "DDCSDA1 (P3.1)", "DDC_SDA", "VGA DDC data, ISP programming"),
    ("98", "P5.4", "PANEL_ON", "Panel power enable, active high"),
    ("99", "P5.5", "BL_ON", "Backlight enable, active high"),
    ("100", "P5.6 / PWM4", "BL_PWM", "Backlight brightness PWM, high = bright"),
    ("113", "P3.6 / IrDA", "IR_IN", "IR receiver input"),
]


class Builder:
    def __init__(self, d):
        self.d = d

    def R(self, val, a, b, sheet, group, dnp=False, dev="R-0603", name=None):
        return self.d.add(dev, val, {"1": a, "2": b}, sheet, group, dnp=dnp, name=name)

    def C(self, val, a, b, sheet, group, dev="C-0603", dnp=False):
        return self.d.add(dev, val, {"1": a, "2": b}, sheet, group, dnp=dnp)

    def CP(self, val, plus, minus, sheet, group):
        return self.d.add("CPOL-D8", val, {"+": plus, "-": minus}, sheet, group)

    def D(self, dev, val, a, c, sheet, group):
        return self.d.add(dev, val, {"A": a, "C": c}, sheet, group)


def rtd_nets(variant):
    """Net for every RTD2660 pin."""
    n = {name: None for name in RTD_PINS.values()}
    for k in ("VDD@1", "VDD@2", "VADC_VDD"):
        n[k] = "+3V3A"
    n["ADC_VDD"] = "+1V8A"
    for k in ("PVCC@1", "PVCC@2", "PVCC@3"):
        n[k] = "+3V3"
    for k in ("VCCK@1", "VCCK@2", "VCCK@3"):
        n[k] = "+1V8"
    for k in ("GND", "ADC_GND", "GNDK", "PGND@1", "PGND@2", "EPAD", "AHS1", "AVS1"):
        n[k] = "GND"
    n.update({"NC_REF": "RTD_REF", "R0+": "ADC_R+", "R0-": "ADC_R-", "G0+": "ADC_G+",
              "G0-": "ADC_G-", "B0+": "ADC_B+", "B0-": "ADC_B-", "SOG0": "ADC_SOG",
              "AHS0": "ADC_HS", "AVS0": "ADC_VS", "XI": "XTAL_I", "XO": "XTAL_O",
              "RESETB": "RESET#", "CEC": "CEC", "SPI_SCLK": "SPI_P115", "SPI_SI": "SPI_P116",
              "SPI_SO": "SPI_P117", "SPI_CEB": "SPI_CS#", "DDCSCL1": "DDC_SCL",
              "DDCSDA1": "DDC_SDA", "P6.0/AADC0": "KEY_AD0", "P6.1/AADC1": "KEY_AD1",
              "P6.2/AADC2": "LED_R_DRV", "P6.3/AADC3": "LED_G_DRV", "P5.4/PWM2": "PANEL_ON",
              "P5.5/PWM3": "BL_ON", "P5.6/PWM4": "BL_PWM", "P3.6/IRDA": "IR_IN"})
    if variant == "LVDS":
        # single-port LVDS uses the E pairs only (pins 86-95); O pairs (74-83) stay unused
        lv = {"TXE1-/R0": "LVDS_E1-", "TXE1+/R1": "LVDS_E1+",
              "TXE2-/R2": "LVDS_E2-", "TXE2+/R3": "LVDS_E2+", "TXEC-/R4": "LVDS_EC-",
              "TXEC+/R5": "LVDS_EC+", "TXE3-/R6": "LVDS_E3-", "TXE3+/R7": "LVDS_E3+",
              "TXE0+/DEN": "LVDS_E0+", "TXE0-/DHS": "LVDS_E0-"}
        n.update(lv)
    else:
        for i in range(8):
            n[[k for k in n if k.endswith("/G%d" % i)][0]] = "TTL_G%d" % i
            n[[k for k in n if k.endswith("/R%d" % i)][0]] = "TTL_R%d" % i
            n[[k for k in n if k.endswith("/B%d" % i)][0]] = "TTL_B%d" % i
        n.update({"TXE0+/DEN": "TTL_DEN", "TXE0-/DHS": "TTL_DHS", "P5.2/DCLK": "TTL_DCLK",
                  "P5.3/DVS": "TTL_DVS"})
    return n


def build(variant, lib):
    titles = {"LVDS": "RTD2660 VGA(12P) -> LVDS 20P 2.0mm (7in 1024x600)",
              "RGB40": "RTD2660 VGA(12P) -> TTL RGB 40P",
              "RGB50": "RTD2660 VGA(12P) -> TTL RGB 50P"}
    d = Design(titles[variant], lib)
    b = Builder(d)
    sh_pwr = d.sheet("POWER")
    sh_core = d.sheet("SCALER RTD2660")
    sh_in = d.sheet("VGA INPUT / KEYPAD / ISP")
    sh_out = d.sheet("OUTPUT " + variant)

    # ------------------------------------------------------------------ power
    g = "12V input"
    d.add("HDR-1X2", "12V IN", {"1": "+12V_IN", "2": "GND"}, sh_pwr, g, name="J1")
    d.add("FUSE-1206", "2A PTC", {"1": "+12V_IN", "2": "+12V_F"}, sh_pwr, g)
    b.D("D-SMA", "SS34", "+12V_F", "+12V", sh_pwr, g)
    b.CP("220uF/25V", "+12V", "GND", sh_pwr, g)
    b.C("10uF/25V", "+12V", "GND", sh_pwr, g, dev="C-1206")
    g = "5V buck"
    d.add("LM2596S", "LM2596S-5.0", {"VIN": "+12V", "OUT": "SW5V", "GND": "GND", "TAB": "GND",
                                       "FB": "+5V", "ON/OFF": "GND"}, sh_pwr, g)
    b.D("D-SMA", "SS34", "GND", "SW5V", sh_pwr, g)
    d.add("L-12X12", "33uH/3A", {"1": "SW5V", "2": "+5V"}, sh_pwr, g)
    b.CP("220uF/10V", "+5V", "GND", sh_pwr, g)
    b.C("10uF", "+5V", "GND", sh_pwr, g, dev="C-0805")
    g = "LDOs"
    for out, inp, val in (("+3V3", "+5V", "AMS1117-3.3"), ("+3V3A", "+5V", "AMS1117-3.3"),
                          ("+1V8", "+3V3", "AMS1117-1.8"), ("+1V8A", "+3V3A", "AMS1117-1.8")):
        d.add("AMS1117", val, {"VIN": inp, "VOUT": out, "TAB": out, "GND": "GND"}, sh_pwr, g)
        b.C("10uF", inp, "GND", sh_pwr, g, dev="C-0805")
        b.C("22uF", out, "GND", sh_pwr, g, dev="C-1206")
    b.R("1k", "+3V3", "PWR_LED", sh_pwr, g)
    d.add("LED-0603", "GREEN", {"A": "PWR_LED", "C": "GND"}, sh_pwr, g)
    g = "Mounting"
    for i in range(4):
        d.add("HOLE-M3", "M3", {}, sh_pwr, g)

    # ------------------------------------------------------------------ scaler core
    g = "RTD2660"
    d.add("RTD2660", "RTD2660", rtd_nets(variant), sh_core, g, name="U1")
    g = "Decoupling"
    for net, n100 in (("+3V3A", 3), ("+1V8A", 1), ("+1V8", 3), ("+3V3", 3)):
        for _ in range(n100):
            b.C("100nF", net, "GND", sh_core, g)
        b.C("10uF", net, "GND", sh_core, g, dev="C-0805")
    g = "Clock / reset / bias"
    d.add("XTAL-HC49SMD", "27MHz", {"1": "XTAL_I", "2": "XTAL_O"}, sh_core, g)
    b.C("22pF", "XTAL_I", "GND", sh_core, g)
    b.C("22pF", "XTAL_O", "GND", sh_core, g)
    b.R("10k", "+3V3", "RESET#", sh_core, g)
    b.C("4.7uF", "RESET#", "GND", sh_core, g, dev="C-0805")
    b.D("D-SOD123", "1N4148W", "RESET#", "+3V3", sh_core, g)
    b.R("1k 1%", "RTD_REF", "GND", sh_core, g)
    b.R("27k", "CEC", "+3V3", sh_core, g)
    g = "SPI flash"
    d.add("SPIFLASH-SOIC8", "W25Q40", {"/CS": "SPI_CS#", "CLK": "FLASH_CLK", "DI": "FLASH_DI",
                                        "DO": "FLASH_DO", "VCC": "+3V3", "/WP": "+3V3",
                                        "/HOLD": "+3V3", "GND": "GND"}, sh_core, g)
    b.C("100nF", "+3V3", "GND", sh_core, g)
    b.R("10k", "SPI_CS#", "GND", sh_core, g)   # CEB strap low = internal MCU (datasheet)
    b.R("33R", "SPI_P115", "FLASH_CLK", sh_core, g)
    b.R("33R", "SPI_P116", "FLASH_DI", sh_core, g)
    b.R("33R", "SPI_P117", "FLASH_DO", sh_core, g)
    b.R("33R", "SPI_P115", "FLASH_DI", sh_core, g, dnp=True)   # swap option CLK <-> DI
    b.R("33R", "SPI_P116", "FLASH_CLK", sh_core, g, dnp=True)
    d.notes[sh_core] += [
        "Crystal 27 MHz = _RTD_XTAL _XTAL27000K in the Realtek RTD2660 SDK (PCB800099 reference).",
        "SPI: pin 115 = SCLK, 116 = SI, 117 = SO per pin names. The datasheet text swaps",
        "115/116; fit the DNP 33R pair instead if the flash does not respond.",
        "CEB (pin 118) pulled low by 10k = internal MCU boot from SPI flash.",
    ]

    # ------------------------------------------------------------------ VGA input
    g = "VGA 12P header"
    d.add("HDR-1X12", "VGA 12P 2.54", {str(k): v for k, v in VGA12_PINOUT.items()
                                        if v != "VGA_5V"}, sh_in, g, name="J2")
    d.add("HDR-1X3", "ISP DDC", {"1": "GND", "2": "VGA_SDA", "3": "VGA_SCL"}, sh_in, g, name="J3")
    g = "Analog front end"
    for col in ("R", "G", "B"):
        b.R("75R 1%", "VGA_" + col, "GND", sh_in, g)
        b.R("33R", "VGA_" + col, "AFE_%s+" % col, sh_in, g)
        b.C("47nF", "AFE_%s+" % col, "ADC_%s+" % col, sh_in, g)
        b.R("33R", "GND", "AFE_%s-" % col, sh_in, g)
        b.C("47nF", "AFE_%s-" % col, "ADC_%s-" % col, sh_in, g)
    b.R("470R", "VGA_G", "AFE_SOG", sh_in, g)
    b.C("1nF", "AFE_SOG", "ADC_SOG", sh_in, g)
    g = "Sync / DDC"
    for s in ("HS", "VS"):
        b.R("100R", "VGA_" + s, "ADC_" + s, sh_in, g)
        b.C("22pF", "ADC_" + s, "GND", sh_in, g)
        b.R("10k", "ADC_" + s, "GND", sh_in, g)
    b.R("100R", "VGA_SDA", "DDC_SDA", sh_in, g)
    b.R("100R", "VGA_SCL", "DDC_SCL", sh_in, g)
    b.R("10k", "DDC_SDA", "+3V3", sh_in, g)
    b.R("10k", "DDC_SCL", "+3V3", sh_in, g)
    g = "Keypad / IR"
    d.add("HDR-1X8", "KEY/IR", {"1": "+3V3", "2": "GND", "3": "KEY_AD0", "4": "KEY_AD1",
                                 "5": "IR_HDR", "6": "LED_G", "7": "LED_R", "8": "+5V"},
          sh_in, g, name="J4")
    b.R("10k", "KEY_AD0", "+3V3", sh_in, g)
    b.R("10k", "KEY_AD1", "+3V3", sh_in, g)
    b.R("100R", "IR_HDR", "IR_IN", sh_in, g)
    b.R("10k", "IR_IN", "+3V3", sh_in, g)
    b.R("1k", "LED_G_DRV", "LED_G", sh_in, g)
    b.R("1k", "LED_R_DRV", "LED_R", sh_in, g)
    d.notes[sh_in] += [
        "J2 VGA 1x12 2.54: 1 R, 2 GND, 3 G, 4 GND, 5 B, 6 GND, 7 HS, 8 VS, 9 GND,",
        "10 DDC_SDA, 11 DDC_SCL, 12 +5V (not used). Check against the mainboard header.",
        "J3: ISP over DDC (Realtek ISP tool). J4 keypad: KEY_AD0 resistor ladder to GND",
        "(10k pull-up on board): POWER 0R, MENU 1.8k, RIGHT 3.9k, LEFT 8.2k, SOURCE 22k.",
    ]

    # ------------------------------------------------------------------ output
    if variant == "LVDS":
        g = "LVDS 20P 2.0mm"
        d.add("HDR-1X20-2.0", "LVDS 20P 2.0", {str(k): v for k, v in LVDS20_PINOUT.items()
                                                 if v}, sh_out, g, name="J5")
        g = "Panel power"
        d.add("AMS1117", "AMS1117-3.3", {"VIN": "+5V", "VOUT": "+3V3_PNL", "TAB": "+3V3_PNL",
                                          "GND": "GND"}, sh_out, g)
        b.C("10uF", "+5V", "GND", sh_out, g, dev="C-0805")
        b.C("22uF", "+3V3_PNL", "GND", sh_out, g, dev="C-1206")
        d.add("PMOS-SOT23", "AO3401A", {"S": "+3V3_PNL", "D": "VLCD", "G": "VLCD_G"}, sh_out, g)
        b.R("10k", "+3V3_PNL", "VLCD_G", sh_out, g)
        b.R("1k", "VLCD_G", "VLCD_Q", sh_out, g)
        d.add("NPN-SOT23", "MMBT3904", {"B": "PNL_ON_B", "C": "VLCD_Q", "E": "GND"}, sh_out, g)
        b.R("4.7k", "PANEL_ON", "PNL_ON_B", sh_out, g)
        b.R("10k", "PNL_ON_B", "GND", sh_out, g)
        b.C("10uF", "VLCD", "GND", sh_out, g, dev="C-0805")
        b.C("100nF", "VLCD", "GND", sh_out, g)
        g = "Backlight control"
        d.add("HDR-1X4-2.0", "BL 4P 2.0", {str(k): v for k, v in BL4_PINOUT.items()},
              sh_out, g, name="J6")
        b.R("1k", "BL_ON", "PNL_LED_EN", sh_out, g)
        b.R("10k", "PNL_LED_EN", "GND", sh_out, g)
        # PWM -> DC 0..1.41 V (panel brightness input 0.7-1.4 V DC)
        b.R("10k", "BL_PWM", "PNL_BL_ADJ", sh_out, g)
        b.R("7.5k", "PNL_BL_ADJ", "GND", sh_out, g)
        b.C("1uF", "PNL_BL_ADJ", "GND", sh_out, g)
        b.C("10uF/25V", "+12V", "GND", sh_out, g, dev="C-1206")
        d.notes[sh_out] += [
            "J5 = 20-pin LVDS plug of the 7in 1024x600 IPS panel cable: 1,2 VDD 3.3V, 3 LED_EN, 4 GND,",
            "5/6 RXIN0-/+, 8/9 RXIN1-/+, 11/12 RXIN2-/+, 14/15 CLK-/+, 17/18 RXIN3-/+, 7,10,13,16 GND, 19,20 NC.",
            "J6 = 4-pin backlight plug: 1 VLED +12V, 2 LED_EN, 3 brightness DC 0-1.41V, 4 GND (check cable).",
            "Single-port LVDS = E pairs of the RTD2660 (pins 86-95). Route as 100R differential pairs.",
            "Firmware: LVDS, single port, 24-bit, 1024x600 (firmware/apply_board.py LVDS).",
        ]
        return d

    # TTL RGB variants
    pin = RGB40_PINOUT if variant == "RGB40" else RGB50_PINOUT
    n = 40 if variant == "RGB40" else 50
    g = "RGB %dP connector" % n
    d.add("FPC-%dP" % n, "FPC %dP 0.5mm" % n,
          {str(k): v for k, v in pin.items() if v is not None}, sh_out, g, name="J5")
    b.R("33R", "TTL_DCLK", "PNL_DCLK", sh_out, g)
    if variant == "RGB40":
        b.R("10k", "VLCD", "PNL_DISP", sh_out, g)
        d.add("HDR-1X4", "TOUCH", {"1": "TP_XR", "2": "TP_YD", "3": "TP_XL", "4": "TP_YU"},
              sh_out, g, name="J6")
    g = "Panel power"
    d.add("PMOS-SOT23", "AO3401A", {"S": "+5V", "D": "PNL_5V", "G": "PNL_G"}, sh_out, g)
    b.R("10k", "+5V", "PNL_G", sh_out, g)
    b.R("1k", "PNL_G", "PNL_Q", sh_out, g)
    d.add("NPN-SOT23", "MMBT3904", {"B": "PNL_ON_B", "C": "PNL_Q", "E": "GND"}, sh_out, g)
    b.R("4.7k", "PANEL_ON", "PNL_ON_B", sh_out, g)
    b.R("10k", "PNL_ON_B", "GND", sh_out, g)
    b.C("10uF", "PNL_5V", "GND", sh_out, g, dev="C-0805")
    d.add("AMS1117", "AMS1117-3.3", {"VIN": "PNL_5V", "VOUT": "VLCD", "TAB": "VLCD",
                                      "GND": "GND"}, sh_out, g)
    b.C("22uF", "VLCD", "GND", sh_out, g, dev="C-1206")
    b.C("100nF", "VLCD", "GND", sh_out, g)

    g = "LED backlight driver"
    d.add("MT3608", "MT3608", {"IN": "PNL_5V", "EN": "LED_EN", "SW": "LED_SW", "FB": "LED_K",
                                "GND": "GND", "NC": None}, sh_out, g)
    b.C("10uF", "PNL_5V", "GND", sh_out, g, dev="C-0805")
    d.add("L-4X4", "22uH/1A", {"1": "PNL_5V", "2": "LED_SW"}, sh_out, g)
    b.D("D-SMA", "SS34", "LED_SW", "LED_A", sh_out, g)
    b.C("4.7uF/50V", "LED_A", "GND", sh_out, g, dev="C-1206")
    if variant == "RGB40":
        b.R("30R 1%", "LED_K", "GND", sh_out, g)     # 0.6 V / 30R = 20 mA
        zval = "24V"
    else:
        b.R("10R 1%", "LED_K", "GND", sh_out, g)     # two 10R in parallel = 5R = 120 mA
        b.R("10R 1%", "LED_K", "GND", sh_out, g)
        zval = "18V"
    d.add("Z-SOD123", "MMSZ %s" % zval, {"C": "LED_A", "A": "LED_OVP"}, sh_out, g)
    b.R("1k", "LED_OVP", "LED_K", sh_out, g)
    b.R("10k", "BL_ON", "LED_EN", sh_out, g)
    d.add("BAT54-SOT23", "BAT54", {"A": "LED_EN", "K": "BL_PWM"}, sh_out, g)
    b.R("100k", "LED_EN", "GND", sh_out, g)

    if variant == "RGB40":
        d.notes[sh_out] += [
            "J5 40P: 1 LED-, 2 LED+, 3 GND, 4 VCC 3.3V, 5-12 R0-R7, 13-20 G0-G7, 21-28 B0-B7,",
            "29 GND, 30 DCLK, 31 DISP, 32 HSYNC, 33 VSYNC, 34 DE, 35 NC, 36 GND, 37-40 XR YD XL YU.",
            "LED current = 0.6 V / R(LED_K): 30R = 20 mA. Zener clamps LED+ at about 24 V if open.",
            "Backlight on only when BL_ON = 1 and BL_PWM = 1 (diode AND into MT3608 EN).",
            "Firmware: DISP_TYPE = TTL (CR8C-00[1:0] = 00), 24-bit, 1 pixel/clock.",
        ]
        return d

    g = "Panel straps"
    b.R("10k", "VLCD", "PNL_MODE", sh_out, g)
    b.R("10k", "PNL_MODE", "GND", sh_out, g, dnp=True)
    b.R("10k", "VLCD", "PNL_LR", sh_out, g)
    b.R("10k", "PNL_LR", "GND", sh_out, g, dnp=True)
    b.R("10k", "VLCD", "PNL_UD", sh_out, g, dnp=True)
    b.R("10k", "PNL_UD", "GND", sh_out, g)
    b.R("10k", "VLCD", "PNL_DITHB", sh_out, g)
    b.R("10k", "PNL_DITHB", "GND", sh_out, g, dnp=True)
    b.R("10k", "VLCD", "PNL_RESET", sh_out, g)
    b.C("1uF", "PNL_RESET", "GND", sh_out, g)
    g = "Panel bias AVDD VGH VGL VCOM"
    d.add("MT3608", "MT3608", {"IN": "PNL_5V", "EN": "BIAS_EN", "SW": "BIAS_SW", "FB": "BIAS_FB",
                                "GND": "GND", "NC": None}, sh_out, g)
    b.C("10uF", "PNL_5V", "GND", sh_out, g, dev="C-0805")
    b.R("100k", "PNL_5V", "BIAS_EN", sh_out, g)
    b.C("1uF", "BIAS_EN", "GND", sh_out, g)
    d.add("L-4X4", "22uH/1A", {"1": "PNL_5V", "2": "BIAS_SW"}, sh_out, g)
    b.D("D-SMA", "SS34", "BIAS_SW", "PNL_AVDD", sh_out, g)
    b.C("10uF/25V", "PNL_AVDD", "GND", sh_out, g, dev="C-1206")
    b.R("165k 1%", "PNL_AVDD", "BIAS_FB", sh_out, g)   # 0.6 * (1 + 165/10) = 10.5 V
    b.R("10k 1%", "BIAS_FB", "GND", sh_out, g)
    # VGH: charge pump doubler from SW node, zener regulated
    b.C("100nF/50V", "BIAS_SW", "CP_H", sh_out, g, dev="C-0805")
    d.add("BAT54S-SOT23", "BAT54S", {"A1": "PNL_AVDD", "COM": "CP_H", "K2": "VGH_RAW"}, sh_out, g)
    b.C("1uF/50V", "VGH_RAW", "GND", sh_out, g, dev="C-0805")
    b.R("2.2k", "VGH_RAW", "PNL_VGH", sh_out, g)
    d.add("Z-SOD123", "MMSZ 16V", {"C": "PNL_VGH", "A": "GND"}, sh_out, g)
    b.C("1uF/50V", "PNL_VGH", "GND", sh_out, g, dev="C-0805")
    # VGL: inverting charge pump, zener regulated
    b.C("100nF/50V", "BIAS_SW", "CP_L", sh_out, g, dev="C-0805")
    d.add("BAT54S-SOT23", "BAT54S", {"A1": "VGL_RAW", "COM": "CP_L", "K2": "GND"}, sh_out, g)
    b.C("1uF/50V", "GND", "VGL_RAW", sh_out, g, dev="C-0805")
    b.R("2.2k", "PNL_VGL", "VGL_RAW", sh_out, g)
    d.add("Z-SOD123", "MMSZ 6.8V", {"C": "GND", "A": "PNL_VGL"}, sh_out, g)
    b.C("1uF/50V", "GND", "PNL_VGL", sh_out, g, dev="C-0805")
    # VCOM: adjustable divider from AVDD
    b.R("47k", "PNL_AVDD", "VCOM_T", sh_out, g)
    d.add("TRIM-3X3", "10k", {"1": "VCOM_T", "3": "VCOM_B", "W": "PNL_VCOM"}, sh_out, g)
    b.R("22k", "VCOM_B", "GND", sh_out, g)
    b.C("1uF", "PNL_VCOM", "GND", sh_out, g)
    d.notes[sh_out] += [
        "J5 50P (AT070TN90/92): 1,2 LED+, 3,4 LED-, 5 GND, 6 VCOM, 7 DVDD 3.3V, 8 MODE, 9 DE,",
        "10 VS, 11 HS, 12-19 B7-B0, 20-27 G7-G0, 28-35 R7-R0, 36 GND, 37 DCLK, 38 GND, 39 L/R,",
        "40 U/D, 41 VGH, 42 VGL, 43 AVDD, 44 RESET, 46 VCOM, 47 DITHB, 48 GND, 45/49/50 NC.",
        "Bias: AVDD 10.5 V, VGH about 16 V, VGL about -6.8 V, VCOM 2.9-4.3 V (set with RV1).",
        "LED current = 0.6 V / 5R = 120 mA. Zener clamps LED+ at about 18 V if open.",
        "Straps (fitted): MODE = H (DE mode), L/R = H, U/D = L, DITHB = H. Swap the DNP 10k to invert.",
        "Firmware: DISP_TYPE = TTL (CR8C-00[1:0] = 00), 24-bit, 1 pixel/clock.",
    ]
    return d
