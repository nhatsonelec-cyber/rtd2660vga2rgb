"""Project library: RTD2660 symbol (pin table from the Realtek RTD2660 datasheet,
rev 1.00 2007/6, 128-pin E-PAD LQFP 14x20 mm) and its footprint with exposed pad."""
import os
from sexp import Sym as S, dump

# pin number -> (name, electrical type)
PINS = {
    1: ('VDD', 'power_in'), 2: ('NC/REF', 'passive'),
    3: ('V8_0', 'input'), 4: ('V8_1', 'input'), 5: ('V8_2', 'input'), 6: ('V8_3', 'input'),
    7: ('V8_4', 'input'), 8: ('V8_5', 'input'), 9: ('V8_6', 'input'), 10: ('V8_7', 'input'),
    11: ('GND', 'power_in'),
    12: ('NC', 'no_connect'), 13: ('NC', 'no_connect'), 14: ('NC', 'no_connect'), 15: ('NC', 'no_connect'),
    16: ('NC', 'no_connect'), 17: ('NC', 'no_connect'), 18: ('NC', 'no_connect'), 19: ('NC', 'no_connect'),
    20: ('VDD', 'power_in'), 21: ('AVS0', 'input'), 22: ('AHS0', 'input'), 23: ('ADC_VDD', 'power_in'),
    24: ('B0-', 'input'), 25: ('B0+', 'input'), 26: ('G0-', 'input'), 27: ('G0+', 'input'),
    28: ('SOG0', 'input'), 29: ('R0-', 'input'), 30: ('R0+', 'input'),
    31: ('B1-/V8_7', 'input'), 32: ('B1+/V8_6', 'input'), 33: ('G1-/V8_5', 'input'), 34: ('G1+/V8_4', 'input'),
    35: ('SOG1/V8_3', 'input'), 36: ('R1-/V8_2', 'input'), 37: ('R1+/V8_1', 'input'),
    38: ('ADC_GND', 'power_in'), 39: ('AHS1/V8_0', 'input'), 40: ('AVS1/VCLK', 'input'),
    41: ('VIN+0', 'input'), 42: ('VIN-0', 'input'), 43: ('VIN+1', 'input'), 44: ('VIN-1', 'input'),
    45: ('VIN+2', 'input'), 46: ('VIN-2', 'input'), 47: ('VIN+3', 'input'), 48: ('VIN-3', 'input'),
    49: ('VADC_VDD', 'power_in'),
    50: ('A-ADC0/P6.0', 'bidirectional'), 51: ('A-ADC1/P6.1', 'bidirectional'), 52: ('A-ADC2/P6.2', 'bidirectional'),
    53: ('A-ADC3/P6.3', 'bidirectional'), 54: ('A-ADC4/P6.4', 'bidirectional'),
    55: ('B-ADC0/PWM1/P6.5', 'bidirectional'), 56: ('B-ADC1/IICSCL/P6.6', 'bidirectional'),
    57: ('B-ADC2/IICSDA/P6.7', 'bidirectional'),
    58: ('DDCSCL1/P3.0', 'bidirectional'), 59: ('DDCSDA1/P3.1', 'bidirectional'),
    60: ('VCCK', 'power_in'), 61: ('GNDK', 'power_in'), 62: ('PVCC', 'power_in'), 63: ('NC', 'no_connect'),
    64: ('IrDA/P1.0', 'bidirectional'), 65: ('WS/PWM1/P1.1', 'bidirectional'),
    66: ('BLU7/P1.2', 'bidirectional'), 67: ('BLU6/P1.3', 'bidirectional'), 68: ('BLU5/P1.4', 'bidirectional'),
    69: ('BLU4/P1.5', 'bidirectional'), 70: ('BLU3/P1.6', 'bidirectional'), 71: ('BLU2/P1.7', 'bidirectional'),
    72: ('NC', 'no_connect'), 73: ('VCCK', 'power_in'),
    74: ('BLU1/TXO3+', 'bidirectional'), 75: ('BLU0/TXO3-', 'bidirectional'),
    76: ('GRN7/TXOC+', 'bidirectional'), 77: ('GRN6/TXOC-', 'bidirectional'),
    78: ('GRN5/TXO2+', 'bidirectional'), 79: ('GRN4/TXO2-', 'bidirectional'),
    80: ('GRN3/TXO1+', 'bidirectional'), 81: ('GRN2/TXO1-', 'bidirectional'),
    82: ('GRN1/TXO0+', 'bidirectional'), 83: ('GRN0/TXO0-', 'bidirectional'),
    84: ('PVCC', 'power_in'), 85: ('PGND', 'power_in'),
    86: ('RED7/TXE3+', 'output'), 87: ('RED6/TXE3-', 'output'), 88: ('RED5/TXEC+', 'output'),
    89: ('RED4/TXEC-', 'output'), 90: ('RED3/TXE2+', 'output'), 91: ('RED2/TXE2-', 'output'),
    92: ('RED1/TXE1+', 'output'), 93: ('RED0/TXE1-', 'output'),
    94: ('DENA/TXE0+', 'output'), 95: ('DHS/TXE0-', 'output'),
    96: ('DCLK/PWM0/P5.2', 'bidirectional'), 97: ('DVS/PWM1/P5.3', 'bidirectional'),
    98: ('PWM2/P5.4', 'bidirectional'), 99: ('PWM3/P5.5', 'bidirectional'),
    100: ('PWM4/P5.6', 'bidirectional'), 101: ('PWM5/P5.7', 'bidirectional'),
    102: ('PWM0/P7.6', 'bidirectional'), 103: ('IICSCL/PWM1/P7.5', 'bidirectional'),
    104: ('IICSDA/IRQB/P7.4', 'bidirectional'), 105: ('GPIO/P8.0', 'bidirectional'),
    106: ('PVCC', 'power_in'), 107: ('PGND', 'power_in'),
    108: ('MCK/P8.1', 'bidirectional'), 109: ('SCK/P3.2', 'bidirectional'), 110: ('WS/P3.3', 'bidirectional'),
    111: ('SD0/P3.4', 'bidirectional'), 112: ('SD1/P3.5', 'bidirectional'), 113: ('IrDA/P3.6', 'bidirectional'),
    114: ('VCLK/P3.7', 'bidirectional'),
    115: ('SPI_SCLK', 'bidirectional'), 116: ('SPI_SI', 'bidirectional'), 117: ('SPI_SO', 'bidirectional'),
    118: ('SPI_CEB', 'bidirectional'), 119: ('NC', 'no_connect'), 120: ('VCCK', 'power_in'),
    121: ('DDCSCL3/P7.3', 'bidirectional'), 122: ('DDCSDA3/P7.2', 'bidirectional'),
    123: ('DDCSDA2/P7.1', 'bidirectional'), 124: ('DDCSCL2', 'bidirectional'),
    125: ('RESETB', 'input'), 126: ('CEC', 'bidirectional'), 127: ('XO', 'output'), 128: ('XI', 'input'),
    129: ('EPAD', 'power_in'),
}
assert len(PINS) == 129

G = None  # gap marker
LEFT = [30, 29, 27, 26, 28, 25, 24, G, 22, 21, G, 37, 36, 34, 33, 35, 32, 31, 39, 40, G,
        41, 42, 43, 44, 45, 46, 47, 48, G, 3, 4, 5, 6, 7, 8, 9, 10, G,
        128, 127, 125, G, 118, 115, 116, 117, G, 58, 59, 56, 57, 126, 2, G,
        12, 13, 14, 15, 16, 17, 18, 19, 63, 72, 119]
RIGHT = [96, 94, 95, 97, G, 86, 87, 88, 89, 90, 91, 92, 93, G, 76, 77, 78, 79, 80, 81, 82, 83, G,
         66, 67, 68, 69, 70, 71, 74, 75, G,
         98, 99, 100, 101, 102, 103, 104, 105, G, 108, 109, 110, 111, 112, 113, 114, G,
         121, 122, 123, 124, G, 64, 65, G, 50, 51, 52, 53, 54, 55]
TOP = [1, 20, 49, G, 23, G, 60, 73, 120, G, 62, 84, 106]
BOTTOM = [11, 38, 61, 85, 107, 129]
assert sorted([p for p in LEFT + RIGHT + TOP + BOTTOM if p]) == list(range(1, 130))

def eff(size=1.27, hide=False, justify=None):
    e = [S('effects'), [S('font'), [S('size'), size, size]]]
    if justify: e.append([S('justify'), S(justify)])
    if hide: e.append(S('hide'))
    return e

def make_symbol():
    rows = max(len(LEFT), len(RIGHT))
    half_h = (rows + 3) * 2.54 / 2
    half_h = round(half_h / 2.54) * 2.54
    hw = 27.94
    top_y = half_h
    pins = []
    def pin(num, x, y, ang):
        name, et = PINS[num]
        return [S('pin'), S(et), S('line'), [S('at'), round(x, 2), round(y, 2), ang], [S('length'), 5.08],
                [S('name'), name, eff()], [S('number'), str(num), eff()]]
    y = top_y - 5.08
    for p in LEFT:
        if p: pins.append(pin(p, -hw - 5.08, y, 0))
        y -= 2.54
    y = top_y - 5.08
    for p in RIGHT:
        if p: pins.append(pin(p, hw + 5.08, y, 180))
        y -= 2.54
    x = -22.86
    for p in TOP:
        if p: pins.append(pin(p, x, top_y + 5.08, 270))
        x += 3.81
    x = -6.35 - 0.0
    x = -12.7
    for p in BOTTOM:
        pins.append(pin(p, x, -top_y - 5.08, 90)); x += 5.08
    sym = [S('symbol'), 'RTD2660', [S('in_bom'), S('yes')], [S('on_board'), S('yes')],
           [S('property'), 'Reference', 'U', [S('at'), -hw, top_y + 3.5, 0], eff(justify='left')],
           [S('property'), 'Value', 'RTD2660', [S('at'), 5.08, -top_y - 2.0, 0], eff(justify='left')],
           [S('property'), 'Footprint', 'rtd2660vga2rgb:LQFP-128-1EP_14x20mm_P0.5mm_EP7.1x7.1mm', [S('at'), 0, 0, 0], eff(hide=True)],
           [S('property'), 'Datasheet', 'http://aitendo3.sakura.ne.jp/aitendo_data/product_img/lcd_controller/Xs/RTD2660.jsp.pdf', [S('at'), 0, 0, 0], eff(hide=True)],
           [S('property'), 'ki_keywords', 'Realtek LCD controller scaler VGA TTL LVDS 8051', [S('at'), 0, 0, 0], eff(hide=True)],
           [S('property'), 'ki_description', 'Realtek RTD2660 flat panel display controller (VGA/YPbPr ADC, video decoder, scaler, OSD, embedded 8051, TTL/LVDS out), E-PAD LQFP-128 14x20mm', [S('at'), 0, 0, 0], eff(hide=True)],
           [S('property'), 'ki_fp_filters', 'LQFP*14x20mm*P0.5mm*', [S('at'), 0, 0, 0], eff(hide=True)],
           [S('symbol'), 'RTD2660_0_1',
            [S('rectangle'), [S('start'), -hw, top_y], [S('end'), hw, -top_y],
             [S('stroke'), [S('width'), 0.254], [S('type'), S('default')]], [S('fill'), [S('type'), S('background')]]]],
           [S('symbol'), 'RTD2660_1_1'] + pins]
    return sym

def write_symlib(path):
    lib = [S('kicad_symbol_lib'), [S('version'), 20220914], [S('generator'), S('rtd2660vga2rgb_tools')], make_symbol()]
    open(path, 'w').write(dump(lib) + '\n')

def write_footprint(pretty_dir):
    os.makedirs(pretty_dir, exist_ok=True)
    name = 'LQFP-128-1EP_14x20mm_P0.5mm_EP7.1x7.1mm'
    src = open('/usr/share/kicad/footprints/Package_QFP.pretty/LQFP-128_14x20mm_P0.5mm.kicad_mod').read()
    src = src.replace('(footprint LQFP-128_14x20mm_P0.5mm', '(footprint ' + name, 1)
    src = src.replace('fp_text value LQFP-128_14x20mm_P0.5mm', 'fp_text value ' + name)
    src = src.replace('(descr "LQFP, 128 Pin', '(descr "E-PAD LQFP, 128 Pin, 14x20mm, 0.5mm pitch, 7.1x7.1mm exposed pad (Realtek RTD2660, SPIL DB128-SW2; EP 7.11 or 8.26 REF)')
    extra = ['  (pad "129" smd rect (at 0 0) (size 7.1 7.1) (layers "F.Cu" "F.Mask"))']
    for ix in (-1, 1):
        for iy in (-1, 1):
            extra.append('  (pad "" smd roundrect (at %g %g) (size 2.9 2.9) (layers "F.Paste") (roundrect_rratio 0.1))' % (ix * 1.75, iy * 1.75))
    for ix in (-2.5, 0, 2.5):
        for iy in (-2.5, 0, 2.5):
            extra.append('  (pad "129" thru_hole circle (at %g %g) (size 0.6 0.6) (drill 0.3) (layers "*.Cu") (zone_connect 2))' % (ix, iy))
    i = src.rstrip().rfind(')')
    j = src.rfind('(model')
    cut = j if j > 0 else i
    out = src[:cut] + '\n'.join(extra) + '\n  ' + src[cut:] if j > 0 else src[:i] + '\n'.join(extra) + '\n)\n'
    open(os.path.join(pretty_dir, name + '.kicad_mod'), 'w').write(out)
    return name

if __name__ == '__main__':
    import sys
    root = sys.argv[1]
    write_symlib(os.path.join(root, 'rtd2660vga2rgb.kicad_sym'))
    print(write_footprint(os.path.join(root, 'rtd2660vga2rgb.pretty')))
