"""Symbols, packages and devices used by the RTD2660 driver boards."""
from eaglelib import Package, Symbol, Device, Library, box_symbol, GRID

LIBNAME = "rtd2660_board"


# ----------------------------------------------------------------------------- packages
def chip2(name, pad_dx, pad_dy, pitch, body_w, body_h, desc, names=("1", "2")):
    p = Package(name, desc)
    p.smd(names[0], -pitch / 2, 0, pad_dx, pad_dy)
    p.smd(names[1], pitch / 2, 0, pad_dx, pad_dy)
    p.wire(-body_w / 2, body_h / 2, body_w / 2, body_h / 2, 0.127, 51)
    p.wire(-body_w / 2, -body_h / 2, body_w / 2, -body_h / 2, 0.127, 51)
    p.wire(-body_w / 2, -body_h / 2, -body_w / 2, body_h / 2, 0.127, 51)
    p.wire(body_w / 2, -body_h / 2, body_w / 2, body_h / 2, 0.127, 51)
    p.names(-body_w / 2, body_h / 2 + 0.4, 0.8)
    return p


def pkg_diode(name, pad_dx, pad_dy, pitch, body_w, body_h, desc):
    p = chip2(name, pad_dx, pad_dy, pitch, body_w, body_h, desc, names=("C", "A"))
    # cathode band on silk
    x = -body_w / 2 + 0.35
    p.wire(x, -body_h / 2 - 0.2, x, body_h / 2 + 0.2, 0.3, 21)
    return p


def pkg_sot23():
    p = Package("SOT23", "SOT-23, 3 leads")
    p.smd("1", -0.95, -1.1, 0.8, 0.9)
    p.smd("2", 0.95, -1.1, 0.8, 0.9)
    p.smd("3", 0, 1.1, 0.8, 0.9)
    p.rect_outline(-1.45, -0.65, 1.45, 0.65, 0.127, 51)
    p.wire(-1.5, 0.3, -1.5, -0.3, 0.2, 21)
    p.wire(1.5, 0.3, 1.5, -0.3, 0.2, 21)
    p.names(-1.5, 1.9, 0.8)
    return p


def pkg_sot23_6():
    p = Package("SOT23-6", "SOT-23-6")
    for i, x in enumerate((-0.95, 0, 0.95)):
        p.smd(str(i + 1), x, -1.2, 0.6, 1.0)
    for i, x in enumerate((0.95, 0, -0.95)):
        p.smd(str(i + 4), x, 1.2, 0.6, 1.0)
    p.rect_outline(-1.45, -0.8, 1.45, 0.8, 0.127, 51)
    p.circle(-1.0, -0.35, 0.15, 0.2, 21)
    p.names(-1.5, 2.1, 0.8)
    return p


def pkg_sot223():
    p = Package("SOT223", "SOT-223, 3 leads + tab (tab = pad 4)")
    for i, x in enumerate((-2.3, 0, 2.3)):
        p.smd(str(i + 1), x, -3.15, 1.2, 2.0)
    p.smd("4", 0, 3.15, 3.6, 2.0)
    p.rect_outline(-3.3, -1.8, 3.3, 1.8, 0.2, 21)
    p.names(-3.3, 4.6, 1.0)
    return p


def pkg_to263_5():
    p = Package("TO263-5", "TO-263-5 (D2PAK-5); tab = pad 6")
    for i in range(5):
        p.smd(str(i + 1), (i - 2) * 1.7, -6.5, 1.0, 2.8)
    p.smd("6", 0, 2.4, 10.6, 9.4)
    p.rect_outline(-5.1, -4.9, 5.1, 3.9, 0.2, 51)
    p.names(-5.3, 7.6, 1.0)
    return p


def pkg_soic8():
    p = Package("SOIC8", "SOIC-8, 150 mil")
    for i in range(4):
        p.smd(str(i + 1), -1.905 + i * 1.27, -2.7, 0.6, 1.55)
        p.smd(str(8 - i), -1.905 + i * 1.27, 2.7, 0.6, 1.55)
    p.rect_outline(-2.45, -1.95, 2.45, 1.95, 0.2, 21)
    p.circle(-1.9, -1.3, 0.25, 0.2, 21)
    p.names(-2.5, 4.0, 1.0)
    return p


def pkg_lqfp128():
    """Realtek 128LD E-PAD LQFP 14x20 mm, 0.5 mm pitch (datasheet p.400).
    Pins 1-38 on the left (top to bottom), 39-64 bottom, 65-102 right, 103-128 top."""
    p = Package("LQFP128-14X20-EP", "128-lead E-PAD LQFP, body 14 x 20 mm, pitch 0.5 mm, "
                "lead span 16 x 22 mm. Exposed pad = GND.")
    pl, pw = 1.6, 0.28
    for i in range(1, 39):
        p.smd(str(i), -7.65, (19.5 - i) * 0.5, pl, pw)
    for i in range(39, 65):
        p.smd(str(i), (-12.5 + (i - 39)) * 0.5, -10.65, pw, pl)
    for i in range(65, 103):
        p.smd(str(i), 7.65, (-18.5 + (i - 65)) * 0.5, pl, pw)
    for i in range(103, 129):
        p.smd(str(i), (12.5 - (i - 103)) * 0.5, 10.65, pw, pl)
    p.smd("EP", 0, 0, 7.0, 7.0, cream=False)
    p.rect_outline(-7.0, -10.0, 7.0, 10.0, 0.2, 51)
    # silk corners
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.wire(sx * 7.0, sy * 10.0, sx * 7.0, sy * 9.6, 0.2, 21)
            p.wire(sx * 7.0, sy * 10.0, sx * 6.6, sy * 10.0, 0.2, 21)
    p.circle(-8.9, 10.6, 0.35, 0.3, 21)
    p.names(-7.0, 12.2, 1.27)
    return p


def pkg_hc49smd():
    p = Package("HC49SMD", "HC-49/US SMD crystal, 11.4 x 4.7 mm")
    p.smd("1", -4.75, 0, 5.5, 2.0)
    p.smd("2", 4.75, 0, 5.5, 2.0)
    p.rect_outline(-5.7, -2.35, 5.7, 2.35, 0.127, 51)
    p.names(-5.7, 2.9, 1.0)
    return p


def pkg_ind(name, size, pad_dx, pad_dy, pitch, desc):
    p = Package(name, desc)
    p.smd("1", -pitch / 2, 0, pad_dx, pad_dy)
    p.smd("2", pitch / 2, 0, pad_dx, pad_dy)
    h = size / 2
    p.rect_outline(-h, -h, h, h, 0.2, 21)
    p.names(-h, h + 0.5, 1.0)
    return p


def pkg_cpol_d8():
    p = Package("CPOL-D8", "Radial electrolytic capacitor, D 8 mm, pitch 3.5 mm")
    p.pad("+", -1.75, 0, 0.8, 1.6, "square")
    p.pad("-", 1.75, 0, 0.8, 1.6, "round")
    p.circle(0, 0, 4.1, 0.2, 21)
    p.wire(-3.4, 1.6, -3.4, 2.6, 0.2, 21)
    p.wire(-3.9, 2.1, -2.9, 2.1, 0.2, 21)
    p.names(-4.1, 4.6, 1.0)
    return p


def pkg_hdr(cols, rows, pitch, name, desc, drill=1.0, dia=1.7):
    """Pin 1 at origin; odd pins row 0, even pins row 1 (for 2-row); pins advance in +x."""
    p = Package(name, desc)
    for k in range(1, cols * rows + 1):
        if rows == 1:
            x, y = (k - 1) * pitch, 0
        else:
            x, y = ((k - 1) // 2) * pitch, -((k - 1) % 2) * pitch
        p.pad(str(k), x, y, drill, dia, "square" if k == 1 else "round")
    x2 = (cols - 1) * pitch
    y2 = -(rows - 1) * pitch
    m = pitch / 2
    p.rect_outline(-m, y2 - m, x2 + m, m, 0.2, 21)
    p.names(-m, m + 0.6, 1.0)
    return p


def pkg_fpc(n, name):
    p = Package(name, "%d-pin 0.5 mm pitch FPC/FFC ZIF connector, SMD. Pin 1 on the left." % n)
    span = (n - 1) * 0.5
    for k in range(1, n + 1):
        p.smd(str(k), -span / 2 + (k - 1) * 0.5, 0, 0.3, 1.4)
    for i, sx in enumerate((-1, 1)):
        p.smd("MP%d" % (i + 1), sx * (span / 2 + 2.3), -3.0, 2.0, 2.6)
    p.rect_outline(-span / 2 - 3.4, -4.8, span / 2 + 3.4, 1.2, 0.2, 51)
    p.circle(-span / 2 - 0.9, 0.9, 0.25, 0.25, 21)
    p.names(-span / 2, 1.6, 1.0)
    return p


def pkg_trim3():
    p = Package("TRIM-3X3", "3 x 3 mm SMD trimmer potentiometer (TC33X / 3313J style)")
    p.smd("1", -1.0, -1.45, 1.2, 1.4)
    p.smd("3", 1.0, -1.45, 1.2, 1.4)
    p.smd("2", 0, 1.45, 1.6, 1.4)
    p.rect_outline(-1.7, -1.7, 1.7, 1.7, 0.127, 51)
    p.names(-1.8, 2.6, 0.8)
    return p


def pkg_hole():
    p = Package("HOLE3.2", "M3 mounting hole, 3.2 mm drill")
    p.hole(0, 0, 3.2)
    p.circle(0, 0, 3.0, 0.2, 21)
    return p


# ----------------------------------------------------------------------------- symbols
def sym_2pin(name, kind):
    s = Symbol(name)
    a, b = ("1", "2")
    if kind in ("D", "Z", "LED"):
        a, b = ("A", "C")
    if kind == "CP":
        a, b = ("+", "-")
    s.pin(a, -5.08, 0, "short", 0)
    s.pin(b, 5.08, 0, "short", 180)
    if kind == "R":
        s.rect(-2.54, -0.889, 2.54, 0.889)
    elif kind == "F":
        s.rect(-2.54, -0.889, 2.54, 0.889)
        s.wire(-2.54, 0, 2.54, 0, 0.1524)
    elif kind == "L":
        s.rect(-2.54, -0.762, 2.54, 0.762)
        s.wire(-2.54, 0.762, 2.54, 0.762, 0.6)
    elif kind in ("C", "CP"):
        s.wire(-2.54, 0, -0.508, 0, 0.1524)
        s.wire(0.508, 0, 2.54, 0, 0.1524)
        s.wire(-0.508, -1.778, -0.508, 1.778, 0.4064)
        if kind == "C":
            s.wire(0.508, -1.778, 0.508, 1.778, 0.4064)
        else:
            s.wire(0.508, -1.778, 0.508, 1.778, 0.8)
            s.text("+", -2.3, 0.5, 1.27, 94)
    elif kind in ("D", "Z", "LED"):
        s.wire(-2.54, 0, -1.27, 0, 0.1524)
        s.wire(1.27, 0, 2.54, 0, 0.1524)
        s.polys.append([(-1.27, 1.27), (-1.27, -1.27), (1.27, 0)])
        s.wire(1.27, -1.27, 1.27, 1.27, 0.254)
        if kind == "Z":
            s.wire(1.27, 1.27, 0.762, 1.27, 0.254)
            s.wire(1.27, -1.27, 1.778, -1.27, 0.254)
        if kind == "LED":
            s.wire(0, 1.524, 0.762, 2.54, 0.1524)
            s.wire(0.762, 1.524, 1.524, 2.54, 0.1524)
    elif kind == "XTAL":
        s.wire(-2.54, 0, -1.524, 0, 0.1524)
        s.wire(1.524, 0, 2.54, 0, 0.1524)
        s.wire(-1.524, -1.778, -1.524, 1.778, 0.254)
        s.wire(1.524, -1.778, 1.524, 1.778, 0.254)
        s.rect(-0.762, -1.524, 0.762, 1.524)
    s.text(">NAME", -2.54, 2.032, 1.778, 95)
    s.text(">VALUE", -2.54, -3.81, 1.778, 96)
    return s


def sym_hole():
    s = Symbol("HOLE")
    s.circles.append((0, 0, 1.27, 0.254))
    s.text(">NAME", -2.54, 2.032, 1.778, 95)
    s.pins = []
    s.wire(-1.27, 0, 1.27, 0, 0.1)
    return s


# RTD2660 pin table: pad -> pin name (names follow the Realtek datasheet; for dual-function
# output pins the name shows LVDS and 24-bit TTL functions, e.g. "TXE1-/R0").
RTD_PINS = {
    1: "VDD@1", 2: "NC_REF", 3: "V8_0", 4: "V8_1", 5: "V8_2", 6: "V8_3", 7: "V8_4", 8: "V8_5",
    9: "V8_6", 10: "V8_7", 11: "GND", 12: "NC@12", 13: "NC@13", 14: "NC@14", 15: "NC@15",
    16: "NC@16", 17: "NC@17", 18: "NC@18", 19: "NC@19", 20: "VDD@2", 21: "AVS0", 22: "AHS0",
    23: "ADC_VDD", 24: "B0-", 25: "B0+", 26: "G0-", 27: "G0+", 28: "SOG0", 29: "R0-", 30: "R0+",
    31: "B1-", 32: "B1+", 33: "G1-", 34: "G1+", 35: "SOG1", 36: "R1-", 37: "R1+", 38: "ADC_GND",
    39: "AHS1", 40: "AVS1", 41: "VIN0+", 42: "VIN0-", 43: "VIN1+", 44: "VIN1-", 45: "VIN2+",
    46: "VIN2-", 47: "VIN3+", 48: "VIN3-", 49: "VADC_VDD", 50: "P6.0/AADC0", 51: "P6.1/AADC1",
    52: "P6.2/AADC2", 53: "P6.3/AADC3", 54: "P6.4/AADC4", 55: "P6.5/BADC0", 56: "P6.6/BADC1",
    57: "P6.7/BADC2", 58: "DDCSCL1", 59: "DDCSDA1", 60: "VCCK@1", 61: "GNDK", 62: "PVCC@1",
    63: "NC@63", 64: "P1.0/IRDA", 65: "P1.1/WS", 66: "P1.2/B7", 67: "P1.3/B6", 68: "P1.4/B5",
    69: "P1.5/B4", 70: "P1.6/B3", 71: "P1.7/B2", 72: "NC@72", 73: "VCCK@2", 74: "TXO3+/B1",
    75: "TXO3-/B0", 76: "TXOC+/G7", 77: "TXOC-/G6", 78: "TXO2+/G5", 79: "TXO2-/G4",
    80: "TXO1+/G3", 81: "TXO1-/G2", 82: "TXO0+/G1", 83: "TXO0-/G0", 84: "PVCC@2", 85: "PGND@1",
    86: "TXE3+/R7", 87: "TXE3-/R6", 88: "TXEC+/R5", 89: "TXEC-/R4", 90: "TXE2+/R3",
    91: "TXE2-/R2", 92: "TXE1+/R1", 93: "TXE1-/R0", 94: "TXE0+/DEN", 95: "TXE0-/DHS",
    96: "P5.2/DCLK", 97: "P5.3/DVS", 98: "P5.4/PWM2", 99: "P5.5/PWM3", 100: "P5.6/PWM4",
    101: "P5.7/PWM5", 102: "P7.6/PWM0", 103: "P7.5/PWM1", 104: "P7.4", 105: "P8.0",
    106: "PVCC@3", 107: "PGND@2", 108: "P8.1", 109: "P3.2", 110: "P3.3", 111: "P3.4",
    112: "P3.5", 113: "P3.6/IRDA", 114: "P3.7", 115: "SPI_SCLK", 116: "SPI_SI", 117: "SPI_SO",
    118: "SPI_CEB", 119: "NC@119", 120: "VCCK@3", 121: "DDCSCL3", 122: "DDCSDA3",
    123: "DDCSDA2", 124: "DDCSCL2", 125: "RESETB", 126: "CEC", 127: "XO", 128: "XI", "EP": "EPAD",
}

RTD_LEFT = [
    "VDD@1", "VDD@2", "VADC_VDD", "ADC_VDD", "PVCC@1", "PVCC@2", "PVCC@3", "VCCK@1", "VCCK@2",
    "VCCK@3", None, "R0+", "R0-", "G0+", "G0-", "B0+", "B0-", "SOG0", "AHS0", "AVS0", None,
    "R1+", "R1-", "G1+", "G1-", "B1+", "B1-", "SOG1", "AHS1", "AVS1", None,
    "VIN0+", "VIN0-", "VIN1+", "VIN1-", "VIN2+", "VIN2-", "VIN3+", "VIN3-", None,
    "V8_0", "V8_1", "V8_2", "V8_3", "V8_4", "V8_5", "V8_6", "V8_7", None,
    "XI", "XO", "RESETB", "NC_REF", "CEC", None,
    "GND", "ADC_GND", "GNDK", "PGND@1", "PGND@2", "EPAD",
]
RTD_RIGHT = [
    "TXO0-/G0", "TXO0+/G1", "TXO1-/G2", "TXO1+/G3", "TXO2-/G4", "TXO2+/G5", "TXOC-/G6",
    "TXOC+/G7", "TXO3-/B0", "TXO3+/B1", "P1.7/B2", "P1.6/B3", "P1.5/B4", "P1.4/B5", "P1.3/B6",
    "P1.2/B7", "TXE1-/R0", "TXE1+/R1", "TXE2-/R2", "TXE2+/R3", "TXEC-/R4", "TXEC+/R5",
    "TXE3-/R6", "TXE3+/R7", "TXE0+/DEN", "TXE0-/DHS", "P5.2/DCLK", "P5.3/DVS", None,
    "SPI_SCLK", "SPI_SI", "SPI_SO", "SPI_CEB", None,
    "DDCSCL1", "DDCSDA1", "DDCSCL2", "DDCSDA2", "DDCSCL3", "DDCSDA3", None,
    "P6.0/AADC0", "P6.1/AADC1", "P6.2/AADC2", "P6.3/AADC3", "P6.4/AADC4", "P6.5/BADC0",
    "P6.6/BADC1", "P6.7/BADC2", "P1.0/IRDA", "P1.1/WS", "P5.4/PWM2", "P5.5/PWM3", "P5.6/PWM4",
    "P5.7/PWM5", "P7.6/PWM0", "P7.5/PWM1", "P7.4", "P8.0", "P8.1", "P3.2", "P3.3", "P3.4",
    "P3.5", "P3.6/IRDA", "P3.7",
]
RTD_NC_ROW = ["NC@12", "NC@13", "NC@14", "NC@15", "NC@16", "NC@17", "NC@18", "NC@19", "NC@63",
              "NC@72", "NC@119"]


def build_library():
    lib = Library(LIBNAME, "Parts for the RTD2660 VGA to LVDS / TTL RGB driver boards "
                  "(generated by tools/gen_eagle.py).")
    S = {k: sym_2pin(k, k) for k in ("R", "C", "CP", "L", "D", "Z", "LED", "F", "XTAL")}
    two = {"1": "1", "2": "2"}
    dio = {"A": "A", "C": "C"}

    p0603 = chip2("0603", 0.9, 1.0, 1.6, 1.6, 0.8, "0603 (1608 metric) chip")
    p0805 = chip2("0805", 1.2, 1.4, 1.9, 2.0, 1.25, "0805 (2012 metric) chip")
    p1206 = chip2("1206", 1.6, 1.8, 3.0, 3.2, 1.6, "1206 (3216 metric) chip")
    lib.add(Device("R-0603", "R", S["R"], p0603, two, "Resistor 0603"))
    lib.add(Device("C-0603", "C", S["C"], p0603, two, "Ceramic capacitor 0603"))
    lib.add(Device("C-0805", "C", S["C"], p0805, two, "Ceramic capacitor 0805"))
    lib.add(Device("C-1206", "C", S["C"], p1206, two, "Ceramic capacitor 1206"))
    lib.add(Device("FUSE-1206", "F", S["F"], p1206, two, "Resettable fuse 1206"))
    lib.add(Device("CPOL-D8", "C", S["CP"], pkg_cpol_d8(), {"+": "+", "-": "-"},
                   "Electrolytic capacitor, radial D8"))
    lib.add(Device("L-12X12", "L", S["L"], pkg_ind("IND-12X12", 12.0, 3.0, 5.0, 9.8,
                   "Shielded power inductor 12 x 12 mm (SRR1260 / CD123 style)"), two,
                   "Power inductor 12 x 12 mm"))
    lib.add(Device("L-4X4", "L", S["L"], pkg_ind("IND-4X4", 4.0, 1.4, 3.6, 3.3,
                   "Power inductor 4 x 4 mm (CD43 / SWPA4020 style)"), two,
                   "Power inductor 4 x 4 mm"))
    lib.add(Device("D-SMA", "D", S["D"], pkg_diode("SMA", 2.0, 1.8, 4.2, 4.4, 2.6,
                   "DO-214AC (SMA), cathode = pad C"), dio, "Schottky diode SMA (SS34)"))
    sod = pkg_diode("SOD123", 1.0, 1.2, 3.3, 2.8, 1.6, "SOD-123, cathode = pad C")
    lib.add(Device("D-SOD123", "D", S["D"], sod, dio, "Diode SOD-123"))
    lib.add(Device("Z-SOD123", "D", S["Z"], sod, dio, "Zener diode SOD-123"))
    lib.add(Device("LED-0603", "LED", S["LED"], chip2("LED0603", 0.9, 1.0, 1.6, 1.6, 0.8,
                   "LED 0603, pad A = anode", names=("C", "A")), dio, "LED 0603"))
    lib.add(Device("XTAL-HC49SMD", "Y", S["XTAL"], pkg_hc49smd(), two, "Crystal HC-49/US SMD"))

    sot23 = pkg_sot23()
    lib.add(Device("PMOS-SOT23", "Q", box_symbol("PMOS", ["G"], ["S", "D"], width=10.16),
                   sot23, {"G": "1", "S": "2", "D": "3"}, "P-channel MOSFET SOT-23 (AO3401A / AO3407A)"))
    lib.add(Device("NPN-SOT23", "Q", box_symbol("NPN", ["B"], ["C", "E"], width=10.16),
                   sot23, {"B": "1", "E": "2", "C": "3"}, "NPN transistor SOT-23 (MMBT3904)"))
    lib.add(Device("BAT54-SOT23", "D", box_symbol("BAT54", ["A"], ["K"], width=10.16),
                   sot23, {"A": "1", "K": "3"}, "Schottky diode BAT54, SOT-23 (pin 2 NC)"))
    lib.add(Device("BAT54S-SOT23", "D", box_symbol("BAT54S", ["A1"], ["K2", "COM"], width=10.16),
                   sot23, {"A1": "1", "K2": "2", "COM": "3"},
                   "Dual series Schottky BAT54S: pin1 = A of D1, pin2 = K of D2, pin3 = K1/A2"))
    lib.add(Device("AMS1117", "U", box_symbol("LDO", ["VIN"], ["VOUT", "TAB"], bottom=["GND"],
                   width=15.24), pkg_sot223(), {"GND": "1", "VOUT": "2", "VIN": "3", "TAB": "4"},
                   "AMS1117 LDO, SOT-223 (tab = VOUT)"))
    lib.add(Device("LM2596S", "U", box_symbol("LM2596", ["VIN", "ON/OFF"], ["OUT", "FB"],
                   bottom=["GND", "TAB"], width=15.24), pkg_to263_5(),
                   {"VIN": "1", "OUT": "2", "GND": "3", "FB": "4", "ON/OFF": "5", "TAB": "6"},
                   "LM2596S buck regulator, TO-263-5 (tab = GND)"))
    lib.add(Device("MT3608", "U", box_symbol("MT3608", ["IN", "EN"], ["SW", "FB"],
                   bottom=["GND", "NC"], width=15.24), pkg_sot23_6(),
                   {"SW": "1", "GND": "2", "FB": "3", "EN": "4", "IN": "5", "NC": "6"},
                   "MT3608 2 A boost converter, SOT-23-6, VFB = 0.6 V"))
    lib.add(Device("SPIFLASH-SOIC8", "U", box_symbol("SPIFLASH", ["/CS", "CLK", "DI", "DO"],
                   ["VCC", "/WP", "/HOLD", "GND"], width=15.24), pkg_soic8(),
                   {"/CS": "1", "DO": "2", "/WP": "3", "GND": "4", "DI": "5", "CLK": "6",
                    "/HOLD": "7", "VCC": "8"}, "SPI NOR flash 25-series, SOIC-8 (W25Q40 / MX25L4006)"))
    lib.add(Device("TRIM-3X3", "RV", box_symbol("TRIM", ["1", "3"], ["W"], width=10.16),
                   pkg_trim3(), {"1": "1", "W": "2", "3": "3"}, "Trimmer potentiometer 3 x 3 mm"))

    # RTD2660
    rtd_sym = box_symbol("RTD2660", RTD_LEFT, RTD_RIGHT, width=35.56,
                         bottom=RTD_NC_ROW)
    lib.add(Device("RTD2660", "U", rtd_sym, pkg_lqfp128(),
                   {name: str(pad) for pad, name in RTD_PINS.items()},
                   "Realtek RTD2660 flat panel display controller, 128-pin E-PAD LQFP 14 x 20 mm"))

    # connectors
    def conn_sym(name, n, label_pins=None):
        return box_symbol(name, [str(i) for i in range(1, n + 1)], [], width=7.62)

    for n in (2, 3, 4, 6, 8, 12):
        pk = pkg_hdr(n, 1, 2.54, "HDR1X%d-2.54" % n, "1 x %d pin header, 2.54 mm pitch" % n)
        lib.add(Device("HDR-1X%d" % n, "J", conn_sym("CONN-%d" % n, n), pk,
                       {str(i): str(i) for i in range(1, n + 1)}, "1 x %d pin header 2.54 mm" % n))
    pk = pkg_hdr(3, 2, 2.54, "HDR2X3-2.54", "2 x 3 pin header, 2.54 mm pitch")
    s23 = box_symbol("CONN-2X3", ["1", "3", "5"], ["2", "4", "6"], width=7.62)
    lib.add(Device("HDR-2X3", "JP", s23, pk, {str(i): str(i) for i in range(1, 7)},
                   "2 x 3 pin header 2.54 mm (jumper)"))
    pk = pkg_hdr(15, 2, 2.0, "HDR2X15-2.0", "2 x 15 pin header, 2.0 mm pitch (LVDS)",
                 drill=0.8, dia=1.3)
    s215 = box_symbol("CONN-2X15", [str(i) for i in range(1, 31, 2)],
                      [str(i) for i in range(2, 31, 2)], width=7.62)
    lib.add(Device("HDR-2X15-2.0", "J", s215, pk, {str(i): str(i) for i in range(1, 31)},
                   "2 x 15 pin header 2.0 mm, LVDS output"))
    for n in (40, 50):
        pk = pkg_fpc(n, "FPC%d-0.5" % n)
        sy = box_symbol("FPC-%d" % n, [str(i) for i in range(1, n + 1)], ["MP1", "MP2"], width=7.62)
        cmap = {str(i): str(i) for i in range(1, n + 1)}
        cmap.update({"MP1": "MP1", "MP2": "MP2"})
        lib.add(Device("FPC-%dP" % n, "J", sy, pk, cmap,
                       "%d-pin 0.5 mm FPC connector for TTL RGB panel" % n))
    lib.add(Device("HOLE-M3", "H", sym_hole(), pkg_hole(), {}, "M3 mounting hole"))
    return lib
