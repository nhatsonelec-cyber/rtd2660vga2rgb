import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rtdlib
from design import d, HW, ROOT_NOTES
import schgen

rtdlib.write_symlib(os.path.join(HW, 'rtd2660vga2rgb.kicad_sym'))
rtdlib.write_footprint(os.path.join(HW, 'rtd2660vga2rgb.pretty'))
schgen.write_all(d, HW, '2026-11-20', '0.1', 'RTD2660 VGA to TTL RGB (7in 1024x600)', ROOT_NOTES)
open(os.path.join(HW, 'sym-lib-table'), 'w').write(
    '(sym_lib_table\n  (version 7)\n  (lib (name "rtd2660vga2rgb")(type "KiCad")(uri "${KIPRJMOD}/rtd2660vga2rgb.kicad_sym")(options "")(descr "Project symbols"))\n)\n')
open(os.path.join(HW, 'fp-lib-table'), 'w').write(
    '(fp_lib_table\n  (version 7)\n  (lib (name "rtd2660vga2rgb")(type "KiCad")(uri "${KIPRJMOD}/rtd2660vga2rgb.pretty")(options "")(descr "Project footprints"))\n)\n')
json.dump(d.netlist(), open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'netlist_expected.json'), 'w'), indent=1, sort_keys=True)
print('components:', len(d.comps), 'nets:', len(d.netlist()))
single = {n: v for n, v in d.netlist().items() if len(v) < 2}
print('single-pin nets:', single)
