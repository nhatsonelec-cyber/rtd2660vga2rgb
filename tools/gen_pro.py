"""Write hardware/rtd2660vga2rgb.kicad_pro (design rules and net classes)."""
import os, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from design import d, HW

PWR = ['VBUS', '+5V', 'SW_3V3', 'SW_1V8', 'BL_SW', 'BIAS_SW']
RAIL = ['GND', '+3V3', '+1V8', '+3V3A', '+1V8A', 'LCD_3V3', 'LEDA', 'LEDK', 'AVDD', 'VGH', 'VGH_RAW', 'VGL', 'VGL_RAW',
        'VCOM', 'VCOM_BUF', 'CP_H', 'CP_L', 'BL_RS2']
nets = d.netlist()
for n in PWR + RAIL:
    assert n in nets, n

def cls(name, width, clearance=0.15, via=0.5, drill=0.25):
    return {"bus_width": 12, "clearance": clearance, "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25,
            "diff_pair_width": 0.2, "line_style": 0, "microvia_diameter": 0.3, "microvia_drill": 0.1,
            "name": name, "pcb_color": "rgba(0, 0, 0, 0.000)", "schematic_color": "rgba(0, 0, 0, 0.000)",
            "track_width": width, "via_diameter": via, "via_drill": drill, "wire_width": 6}

def write():
    json.dump(pro, open(os.path.join(HW, 'rtd2660vga2rgb.kicad_pro'), 'w'), indent=2)

pro = {
    "board": {
        "3dviewports": [],
        "design_settings": {
            "defaults": {"board_outline_line_width": 0.1, "copper_line_width": 0.2, "copper_text_size_h": 1.0,
                         "copper_text_size_v": 1.0, "copper_text_thickness": 0.15, "silk_line_width": 0.12,
                         "silk_text_size_h": 0.8, "silk_text_size_v": 0.8, "silk_text_thickness": 0.12},
            "diff_pair_dimensions": [],
            "drc_exclusions": [],
            "rules": {"max_error": 0.005, "min_clearance": 0.127, "min_connection": 0.0, "min_copper_edge_clearance": 0.3,
                      "min_hole_clearance": 0.2, "min_hole_to_hole": 0.25, "min_microvia_diameter": 0.2,
                      "min_microvia_drill": 0.1, "min_resolved_spokes": 1, "min_silk_clearance": 0.0,
                      "min_text_height": 0.5, "min_text_thickness": 0.08, "min_through_hole_diameter": 0.2,
                      "min_track_width": 0.127, "min_via_annular_width": 0.1, "min_via_diameter": 0.45,
                      "solder_mask_to_copper_clearance": 0.0, "use_height_for_length_calcs": True},
            "rule_severities": {"lib_footprint_issues": "ignore", "lib_footprint_mismatch": "ignore", "silk_overlap": "ignore",
                                "silk_over_copper": "ignore", "silk_edge_clearance": "ignore", "text_height": "ignore",
                                "text_thickness": "ignore", "courtyards_overlap": "warning"},
            "track_widths": [0.0, 0.15, 0.25, 0.4],
            "via_dimensions": [{"diameter": 0.0, "drill": 0.0}, {"diameter": 0.5, "drill": 0.25}],
            "zones_allow_external_fillets": False
        },
        "layer_presets": [], "viewports": []
    },
    "boards": [],
    "cvpcb": {"equivalence_files": []},
    "libraries": {"pinned_footprint_libs": [], "pinned_symbol_libs": []},
    "meta": {"filename": "rtd2660vga2rgb.kicad_pro", "version": 1},
    "net_settings": {
        "classes": [cls("Default", 0.15), cls("Power", 0.4), cls("Rail", 0.25)],
        "meta": {"version": 3},
        "net_colors": None,
        "netclass_assignments": None,
        "netclass_patterns": [{"netclass": "Power", "pattern": n} for n in PWR] + [{"netclass": "Rail", "pattern": n} for n in RAIL]
    },
    "pcbnew": {"last_paths": {"gencad": "", "idf": "", "netlist": "", "specctra_dsn": "", "step": "", "vrml": ""}, "page_layout_descr_file": ""},
    "schematic": {"legacy_lib_dir": "", "legacy_lib_list": [], "meta": {"version": 1}, "page_layout_descr_file": ""},
    "sheets": [],
    "text_variables": {}
}
if __name__ == '__main__':
    write(); print('wrote kicad_pro')
