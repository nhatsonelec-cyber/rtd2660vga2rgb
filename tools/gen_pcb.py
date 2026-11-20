"""Build hardware/rtd2660vga2rgb.kicad_pcb (placement, nets, outline, planes) with the pcbnew API."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew
from design import d, HW
from placement import P, W, H

OX, OY = 100.0, 80.0          # board origin on the KiCad page
FPDIR = '/usr/share/kicad/footprints'
mm = pcbnew.FromMM
def V(x, y): return pcbnew.VECTOR2I(mm(OX + x), mm(OY + y))

def build(out):
    b = pcbnew.BOARD()
    b.SetCopperLayerCount(4)
    b.SetLayerName(pcbnew.In1_Cu, 'In1.Cu'); b.SetLayerName(pcbnew.In2_Cu, 'In2.Cu')
    b.SetLayerType(pcbnew.In1_Cu, pcbnew.LT_POWER)
    b.SetLayerType(pcbnew.In2_Cu, pcbnew.LT_POWER)
    ds = b.GetDesignSettings()
    ds.SetBoardThickness(mm(1.6))
    ds.m_TrackMinWidth = mm(0.127); ds.m_ViasMinSize = mm(0.45); ds.m_MinThroughDrill = mm(0.2)
    ds.m_MinClearance = mm(0.127); ds.m_CopperEdgeClearance = mm(0.3)
    ds.m_HoleClearance = mm(0.2); ds.m_HoleToHoleMin = mm(0.25)
    ds.m_ViasMinAnnularWidth = mm(0.1)
    tb = b.GetTitleBlock(); tb.SetTitle('RTD2660 VGA to TTL RGB (7in 1024x600)'); tb.SetRevision('0.1'); tb.SetDate('2026-11-20')

    nets = {}
    for name in sorted(d.netlist()):
        ni = pcbnew.NETINFO_ITEM(b, name); b.Add(ni); nets[name] = ni
    missing = [c.ref for c in d.comps if c.ref not in P]
    assert not missing, 'no placement for %s' % missing
    for c in d.comps:
        lib, name = c.fp.split(':')
        libdir = os.path.join(HW, lib + '.pretty') if lib == 'rtd2660vga2rgb' else os.path.join(FPDIR, lib + '.pretty')
        fp = pcbnew.FootprintLoad(libdir, name)
        assert fp, c.fp
        fp.SetFPID(pcbnew.LIB_ID(lib, name))
        fp.SetReference(c.ref); fp.SetValue(c.value)
        x, y, rot, side = P[c.ref]
        b.Add(fp)
        fp.SetPosition(V(x, y))
        if side == 'B':
            fp.Flip(fp.GetPosition(), False)
        fp.SetOrientationDegrees(rot)
        if c.dnp:
            fp.SetAttributes(fp.GetAttributes() | getattr(pcbnew, 'FP_DNP', 0) | pcbnew.FP_EXCLUDE_FROM_POS_FILES | pcbnew.FP_EXCLUDE_FROM_BOM)
        if c.sym == 'Mechanical:MountingHole':
            fp.SetAttributes(fp.GetAttributes() | pcbnew.FP_EXCLUDE_FROM_BOM | pcbnew.FP_EXCLUDE_FROM_POS_FILES)
        used = set()
        for pad in fp.Pads():
            num = pad.GetNumber()
            if num in c.pins:
                used.add(num)
                if c.pins[num]:
                    pad.SetNet(nets[c.pins[num]])
        unk = set(c.pins) - used
        assert not unk, '%s: symbol pins without pads: %s' % (c.ref, unk)
        # shrink silkscreen reference text so the dense layout stays readable
        # dense double-sided board: keep reference designators on the fab layers, not on silkscreen
        r = fp.Reference(); r.SetTextSize(pcbnew.VECTOR2I(mm(0.5), mm(0.5))); r.SetTextThickness(mm(0.08))
        r.SetLayer(pcbnew.B_Fab if side == 'B' else pcbnew.F_Fab); r.SetPosition(fp.GetPosition())
        r.SetTextAngleDegrees(0)
        fp.Value().SetVisible(False)

    # outline with 1 mm corner radius
    def seg(x1, y1, x2, y2):
        s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetLayer(pcbnew.Edge_Cuts)
        s.SetStart(V(x1, y1)); s.SetEnd(V(x2, y2)); s.SetWidth(mm(0.1)); b.Add(s)
    def arc(cx, cy, sx, sy, ex, ey):
        s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_ARC); s.SetLayer(pcbnew.Edge_Cuts)
        s.SetCenter(V(cx, cy)); s.SetStart(V(sx, sy)); s.SetEnd(V(ex, ey)); s.SetWidth(mm(0.1)); b.Add(s)
    R = 1.0
    seg(R, 0, W - R, 0); seg(W, R, W, H - R); seg(W - R, H, R, H); seg(0, H - R, 0, R)
    arc(R, R, 0, R, R, 0); arc(W - R, R, W - R, 0, W, R); arc(W - R, H - R, W, H - R, W - R, H); arc(R, H - R, R, H, 0, H - R)

    def zone(net, layer, prio=0, pts=None, name=''):
        z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(nets[net]); z.SetAssignedPriority(prio)
        z.SetZoneName(name or net)
        pts = pts or [(0, 0), (W, 0), (W, H), (0, H)]
        o = z.Outline(); o.NewOutline()
        for (x, y) in pts: o.Append(mm(OX + x), mm(OY + y))
        z.SetLocalClearance(mm(0.2)); z.SetMinThickness(mm(0.2))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetThermalReliefGap(mm(0.25)); z.SetThermalReliefSpokeWidth(mm(0.3))
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        b.Add(z); return z
    zone('GND', pcbnew.In1_Cu, 0, name='GND plane')
    zone('+3V3', pcbnew.In2_Cu, 0, name='+3V3 plane')
    pcbnew.SaveBoard(out, b)
    import gen_pro; gen_pro.write()      # SaveBoard writes a default project file: restore ours
    b = pcbnew.LoadBoard(out)            # reload with the project rules, then fill the inner planes
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(out, b); gen_pro.write()
    return b

if __name__ == '__main__':
    out = os.path.join(HW, 'rtd2660vga2rgb.kicad_pcb')
    b = build(out)
    # courtyard overlap report (per side)
    items = []
    for fp in b.GetFootprints():
        for lay, side in ((pcbnew.F_CrtYd, 'F'), (pcbnew.B_CrtYd, 'B')):
            cy = fp.GetCourtyard(lay)
            if cy.OutlineCount():
                bb = cy.BBox()
                items.append((fp.GetReference(), side, bb.GetX() / 1e6 - OX, bb.GetY() / 1e6 - OY,
                              (bb.GetX() + bb.GetWidth()) / 1e6 - OX, (bb.GetY() + bb.GetHeight()) / 1e6 - OY))
    n = 0
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            a, c = items[i], items[j]
            if a[1] != c[1]: continue
            ox = min(a[4], c[4]) - max(a[2], c[2]); oy = min(a[5], c[5]) - max(a[3], c[3])
            if ox > 0.02 and oy > 0.02:
                n += 1; print('OVERLAP %s %s/%s  %.2f x %.2f' % (a[1], a[0], c[0], ox, oy))
    for it in items:
        if it[0] in ('J1',): continue
        if it[2] < -0.01 or it[3] < -0.01 or it[4] > W + 0.01 or it[5] > H + 0.01:
            print('OUTSIDE', it[0], [round(v, 2) for v in it[2:]])
    print('footprints:', len(b.GetFootprints()), 'courtyard overlaps:', n)
