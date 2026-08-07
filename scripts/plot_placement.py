#!/usr/bin/env python3
"""Plot 3D placement results: bottom die vs top die for gcd."""

import re
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False


def parse_def(def_path):
    cells = []
    diearea = (0, 0, 63080, 57680)
    with open(def_path) as f:
        text = f.read()
    m = re.search(r'DIEAREA\s*\(\s*(\d+)\s+(\d+)\s*\)\s*\(\s*(\d+)\s+(\d+)\s*\)', text)
    if m:
        diearea = tuple(map(int, m.groups()))
    for m in re.finditer(r'-\s+(\S+)\s+(\S+)', text):
        name, ct = m.group(1), m.group(2)
        pm = re.search(r'-\s+' + re.escape(name) + r'\s+' + re.escape(ct) +
                       r'[\s\S]*?\+ PLACED\s*\(\s*(\d+)\s+(\d+)\s*\)', text)
        if pm:
            cells.append((name, int(pm.group(1)), int(pm.group(2)), ct))
    return cells, diearea


def plot_3d(def_3d_path, output_path):
    cells, diearea = parse_def(def_3d_path)
    bottom = [(x, y) for _, x, y, t in cells if t.endswith('_b')]
    top = [(x, y) for _, x, y, t in cells if t.endswith('_t')]
    other = len(cells) - len(bottom) - len(top)

    fig, axes = plt.subplots(1, 2, figsize=(14, 7))

    # Bottom die
    ax = axes[0]
    if bottom:
        xs, ys = zip(*bottom)
        ax.scatter(xs, ys, c='#2E86AB', s=18, alpha=0.65, edgecolors='none')
    ax.set_title(f'Bottom Die  ({len(bottom)} cells)', fontsize=14, fontweight='bold')
    ax.set_xlim(0, diearea[2]); ax.set_ylim(0, diearea[3])
    ax.set_aspect('equal')
    ax.set_xlabel('X (µm)'); ax.set_ylabel('Y (µm)')

    # Top die
    ax = axes[1]
    if top:
        xs, ys = zip(*top)
        ax.scatter(xs, ys, c='#D66853', s=18, alpha=0.65, edgecolors='none')
    ax.set_title(f'Top Die  ({len(top)} cells)', fontsize=14, fontweight='bold')
    ax.set_xlim(0, diearea[2]); ax.set_ylim(0, diearea[3])
    ax.set_aspect('equal')
    ax.set_xlabel('X (µm)'); ax.set_ylabel('Y (µm)')

    stats = (f"Total cells: {len(cells)}  |  Bottom: {len(bottom)}  |  Top: {len(top)}  |  IO/pins: {other}\n"
             f"Each die: {diearea[2]/1000:.0f} x {diearea[3]/1000:.0f} µm  —  same footprint, stacked vertically\n"
             f"Placer: HeteroPlace3D  |  Benchmark: gcd (NanGate45 F2F)  |  Runtime: ~66 s")
    fig.text(0.5, 0.01, stats, ha='center', fontsize=9, family='monospace',
             bbox=dict(boxstyle='round', facecolor='#F5F5F5', alpha=0.8))

    fig.suptitle('gcd — 3D Placement: Bottom vs Top Die', fontsize=16, fontweight='bold', y=0.97)
    plt.tight_layout(rect=[0, 0.06, 1, 0.95])
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved {output_path}")


if __name__ == '__main__':
    import sys
    plot_3d(
        sys.argv[1] if len(sys.argv) > 1 else 'results/gcd/gcd_3d.def',
        sys.argv[2] if len(sys.argv) > 2 else 'docs/gcd_3d_placement.png'
    )
