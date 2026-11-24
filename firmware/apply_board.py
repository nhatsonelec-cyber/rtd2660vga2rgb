#!/usr/bin/env python3
"""Apply this board's configuration to a Realtek RTD2660 firmware SDK checkout.

The SDK itself is Realtek code and is NOT included in this repository. This script
takes the PCB800099 board file and a panel file from the SDK as templates, writes
new files for this board, and selects them in PCB/Pcb.h and Panel/Panel.h.

usage:
    python3 apply_board.py <sdk_dir> <LVDS|RGB40|RGB50>

Then open KR266Xseries.Uv2 in Keil uVision (C51), build, and run FIRMWARE.BAT /
CreateBin.exe to produce the .bin for the SPI flash.
"""
import os
import re
import shutil
import sys

PCB_NAME = "PCB_VGA12P"
PCB_ID = 20

# --------------------------------------------------------------------- board (all variants)
# GPIO map of this board (see README.md):
#   pin 50  P6.0/ADCA0  KEY_AD0 (keypad ladder)   pin 51 P6.1/ADCA1 KEY_AD1 (spare)
#   pin 52  P6.2        LED red  (bLED1)          pin 53 P6.3       LED green (bLED2)
#   pin 98  P5.4        PANEL_ON, active high     pin 99 P5.5       BL_ON, active high
#   pin 100 PWM4        BL_PWM                    pin 113 IrDA      IR receiver
#   pin 58/59 DDC1      VGA DDC / ISP             crystal 27 MHz
PCB_DEFINES = {
    "_RTD_XTAL": "_XTAL27000K",
    "_KEY_SCAN_TYPE": "_KEY_SCAN_AD",
    "_SOURCE_0_TYPE": "_SOURCE_VGA",
    "_SOURCE_1_TYPE": "_SOURCE_NONE",
    "_SOURCE_2_TYPE": "_SOURCE_NONE",
    "_SOURCE_3_TYPE": "_SOURCE_NONE",
    "_SOURCE_4_TYPE": "_SOURCE_NONE",
    "_SOURCE_5_TYPE": "_SOURCE_NONE",
    "_SOURCE_6_TYPE": "_SOURCE_NONE",
    "_INPUT_PORT_NUM": "1",
    "_NORMAL_SOURCE": "_SOURCE_VGA",
    "_SOURCE_VGA_PORT_TYPE": "_DSUB_A0_PORT",
    "_PANEL_ON": "1",
    "_PANEL_OFF": "0",
    "_LIGHT_ON": "1",
    "_LIGHT_OFF": "0",
    "_PIN_50": "(3 & 0x07)",          # ADCA0  key ladder
    "_PIN_51": "(3 & 0x03)",          # ADCA1  spare key ladder
    "_PIN_52": "(2 & 0x03)",          # P6.2   LED red, push-pull
    "_PIN_53": "(2 & 0x03)",          # P6.3   LED green, push-pull
    "_PIN_58_59_DDC1_ENABLE": "(1 & 0x01)",
    "_PIN_96": "(4 & 0x07)",          # DCLK
    "_PIN_97": "(4 & 0x07)",          # DVS
    "_PIN_98": "(2 & 0x03)",          # P5.4   PANEL_ON, push-pull
    "_PIN_99": "(2 & 0x07)",          # P5.5   BL_ON, push-pull
    "_PIN_100": "(3 & 0x07)",         # PWM4   backlight
    "_PIN_113": "(6 & 0x07)",         # IrDA
    "bPANELPOWER": "(_MCU_PORT54)",
    "bHDMICONNECT": "_NON_CONNECT_PIN",
    "bVGACONNECT": "_NON_CONNECT_PIN",
    "bLED1": "(_MCU_PORT62)",
    "AD_KEY": "MCU_ADC0",
    # 6-bit ADC codes with 10k pull-up: 0R, 1.8k, 3.9k, 8.2k, 22k to GND
    "bAD0_Key_1": "0",                # POWER
    "bAD0_Key_2": "43",               # SOURCE  (22k)
    "bAD0_Key_4": "28",               # LEFT    (8.2k)
    "bAD0_Key_5": "10",               # MENU    (1.8k)
    "bAD0_Key_6": "18",               # RIGHT   (3.9k)
    "_BACKLIGHT_PWM": "_RTD_PWM4",
    "_BACKLIGHT_PWM_INVERSE": "_DISABLE",
    "_MCU_PWM4_SUPPORT": "_ON",
    "_VGA_EDID": "_ON",
}
# sbit lines in the template that must become XDATA port macros on this board
PCB_SBIT = {
    "bLIGHTPOWER": "(_MCU_PORT55)",   # pin 99 P5.5
    "bLED2": "(_MCU_PORT63)",         # pin 53 P6.3
}

# --------------------------------------------------------------------- panels
PANELS = {
    "LVDS": dict(
        template="PNL_A089SW01.h", guard="_PNL_LVDS_A089SW01", name="_PNL_VGA12P_LVDS", id=20,
        comment="Generic 1024x768 LVDS, single port, 6-bit (VESA 1024x768@60, 65 MHz)",
        defines={
            "_PANEL_LR_UD_FUNC": "_OFF", "_OUTPUT_BUS": "_PANEL_LVDS",
            "_DISP_BIT": "_DISP_18_BIT", "_DISP_EO_SWAP": "0", "_DISP_RB_SWAP": "0",
            "_DISP_ML_SWAP": "0", "_DISPLAY_PORT": "_DISP_SINGLE_PORT",
            "_DISP_WID": "1024", "_DISP_LEN": "768",
            "_DH_ACT_STA_POS": "296", "_DV_ACT_STA_POS": "35",
            "_STD_DH_TOTAL": "1344", "_STD_DV_TOTAL": "806",
            "_HSYNC_WIDTH": "136", "_VSYNC_HEIGHT": "6",
        }),
    "RGB40": dict(
        template="PNL_AT102TN03.h", guard="_PNL_AT102TN03", name="_PNL_VGA12P_RGB40", id=21,
        comment="40-pin TTL RGB 480x272 (AT043TN24), 24-bit, DE mode, 9 MHz",
        defines={
            "_PANEL_LR_UD_FUNC": "_OFF", "_OUTPUT_BUS": "_PANEL_TTL",
            "_DISP_BIT": "_DISP_24_BIT", "_DISP_EO_SWAP": "0", "_DISP_RB_SWAP": "0",
            "_DISP_ML_SWAP": "0", "_DISPLAY_PORT": "_DISP_SINGLE_PORT",
            "_DISP_WID": "480", "_DISP_LEN": "272",
            "_DH_ACT_STA_POS": "43", "_DV_ACT_STA_POS": "12",
            "_STD_DH_TOTAL": "525", "_STD_DV_TOTAL": "286",
            "_HSYNC_WIDTH": "41", "_VSYNC_HEIGHT": "10",
        }),
    "RGB50": dict(
        template="PNL_AT102TN03.h", guard="_PNL_AT102TN03", name="_PNL_VGA12P_RGB50", id=22,
        comment="50-pin TTL RGB 800x480 (AT070TN90/92), 24-bit, DE mode, 33.3 MHz",
        defines={
            "_PANEL_LR_UD_FUNC": "_OFF", "_OUTPUT_BUS": "_PANEL_TTL",
            "_DISP_BIT": "_DISP_24_BIT", "_DISP_EO_SWAP": "0", "_DISP_RB_SWAP": "0",
            "_DISP_ML_SWAP": "0", "_DISPLAY_PORT": "_DISP_SINGLE_PORT",
            "_DISP_WID": "800", "_DISP_LEN": "480",
            "_DH_ACT_STA_POS": "46", "_DV_ACT_STA_POS": "23",
            "_STD_DH_TOTAL": "1056", "_STD_DV_TOTAL": "525",
            "_HSYNC_WIDTH": "20", "_VSYNC_HEIGHT": "10",
        }),
}


def read(path):
    with open(path, "rb") as fh:
        return fh.read().decode("latin-1")


def write(path, text):
    if os.path.exists(path) and not os.path.exists(path + ".orig"):
        shutil.copy2(path, path + ".orig")
    with open(path, "wb") as fh:
        fh.write(text.replace("\r\n", "\n").replace("\n", "\r\n").encode("latin-1"))


def set_define(text, name, value, where):
    pat = re.compile(r"^([ \t]*#define[ \t]+%s)([ \t]+)([^\r\n]*?)([ \t]*(//[^\r\n]*)?)$"
                     % re.escape(name), re.M)
    hits = pat.findall(text)
    if len(hits) != 1:
        raise SystemExit("%s: expected exactly one '#define %s', found %d" % (where, name, len(hits)))
    return pat.sub(lambda m: "%s%s%s    // VGA12P (was: %s)" % (m.group(1), m.group(2), value,
                                                              m.group(3).strip()), text)


def sbit_to_define(text, name, value, where):
    pat = re.compile(r"^[ \t]*sbit[ \t]+%s[ \t]*=[^\r\n;]*;[^\r\n]*$" % re.escape(name), re.M)
    if len(pat.findall(text)) != 1:
        raise SystemExit("%s: expected exactly one 'sbit %s'" % (where, name))
    return pat.sub("#define %s %s    // VGA12P: XDATA port pin" % (name, value), text)


def select(text, kind, new_name, new_id, include, where):
    """Add '#define <new_name> <id>' + include block and make it the selected type."""
    sel = "_PCB_TYPE" if kind == "pcb" else "_PANEL_TYPE"
    if "#define %s" % new_name not in text:
        anchor = re.search(r"^[ \t]*#define[ \t]+%s\b" % sel, text, re.M)
        text = text[:anchor.start()] + "#define %s %d    // VGA12P board\r\n" % (new_name, new_id) + text[anchor.start():]
        text += "\r\n#if(%s == %s)\r\n#include \"%s\"\r\n#endif\r\n" % (sel, new_name, include)
    text = set_define(text, sel, new_name, where)
    return text


def main():
    if len(sys.argv) != 3 or sys.argv[2] not in PANELS:
        raise SystemExit(__doc__)
    sdk, variant = sys.argv[1], sys.argv[2]
    for p in ("PCB/Pcb.h", "PCB/PCB800099.h", "Panel/Panel.h"):
        if not os.path.exists(os.path.join(sdk, p)):
            raise SystemExit("not an RTD2660 SDK directory (missing %s)" % p)

    # board file
    src = os.path.join(sdk, "PCB", "PCB800099.h")
    text = read(src + ".orig" if os.path.exists(src + ".orig") else src)
    for k, v in PCB_DEFINES.items():
        text = set_define(text, k, v, "PCB800099.h")
    for k, v in PCB_SBIT.items():
        text = sbit_to_define(text, k, v, "PCB800099.h")
    text = "// Board: RTD2660 VGA 12P header (generated by apply_board.py from PCB800099.h)\r\n" + text
    write(os.path.join(sdk, "PCB", PCB_NAME + ".h"), text)
    pcb_sel = os.path.join(sdk, "PCB", "Pcb.h")
    write(pcb_sel, select(read(pcb_sel), "pcb", "_" + PCB_NAME, PCB_ID,
                          "pcb\\%s.h" % PCB_NAME, "Pcb.h"))

    # panel file
    pn = PANELS[variant]
    ptext = read(os.path.join(sdk, "Panel", pn["template"]))
    for k, v in pn["defines"].items():
        ptext = set_define(ptext, k, v, pn["template"])
    if ptext.count(pn["guard"]) != 1:
        raise SystemExit("%s: panel guard %s not found once" % (pn["template"], pn["guard"]))
    ptext = ptext.replace(pn["guard"], pn["name"])
    fname = pn["name"].lstrip("_").replace("PNL_", "PNL_") + ".h"
    ptext = "// Panel: %s (generated by apply_board.py from %s)\r\n" % (pn["comment"], pn["template"]) + ptext
    write(os.path.join(sdk, "Panel", fname), ptext)
    pnl_sel = os.path.join(sdk, "Panel", "Panel.h")
    write(pnl_sel, select(read(pnl_sel), "panel", pn["name"], pn["id"], "Panel\\%s" % fname, "Panel.h"))

    print("Board  : PCB/%s.h  (selected in PCB/Pcb.h)" % PCB_NAME)
    print("Panel  : Panel/%s  (selected in Panel/Panel.h)" % fname)
    print("Backups: *.orig next to every modified SDK file")
    print("Next   : open KR266Xseries.Uv2 in Keil uVision, Rebuild, then run FIRMWARE.BAT")


if __name__ == "__main__":
    main()
