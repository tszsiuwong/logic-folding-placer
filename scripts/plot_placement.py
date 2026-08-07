#!/usr/bin/env python3
"""Plot 2D(2A, natural) vs 3D (Bottom + Top)."""

import re
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

def parse(path):
    cells = []; diearea = (0,0,63080,57680)
    with open(path) as f: t = f.read()
    m = re.search(r'DIEAREA\s*\(\s*(\d+)\s+(\d+)\s*\)\s*\(\s*(\d+)\s+(\d+)\s*\)', t)
    if m: diearea = tuple(map(int, m.groups()))
    for m in re.finditer(r'-\s+(\S+)\s+(\S+)[\s\S]*?\+ PLACED\s*\(\s*(\d+)\s+(\d+)\s*\)', t):
        cells.append((m.group(1), int(m.group(3)), int(m.group(4)), m.group(2)))
    return cells, diearea

d2d, da2d = parse('results/gcd/gcd_2d_2A_nat.def')
d3d, da3d = parse('results/gcd/gcd_3d.def')
bot = [(x,y) for _,x,y,t in d3d if t.endswith('_b')]
top = [(x,y) for _,x,y,t in d3d if t.endswith('_t')]

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

ax = axes[0]
xs = [x for _,x,y,_ in d2d]; ys = [y for _,x,y,_ in d2d]
ax.scatter(xs, ys, c='steelblue', s=6, alpha=0.5, edgecolors='none')
ax.set_title(f'2D (Area=2A, natural density)  {len(d2d)} cells', fontsize=12, fontweight='bold')
ax.set_xlim(0, da2d[2]); ax.set_ylim(0, da2d[3]); ax.set_aspect('equal')

ax = axes[1]
if bot:
    xs, ys = zip(*bot)
    ax.scatter(xs, ys, c='#2E86AB', s=18, alpha=0.65, edgecolors='none')
ax.set_title(f'3D Bottom Die  {len(bot)} cells', fontsize=12, fontweight='bold')
ax.set_xlim(0, da3d[2]); ax.set_ylim(0, da3d[3]); ax.set_aspect('equal')

ax = axes[2]
if top:
    xs, ys = zip(*top)
    ax.scatter(xs, ys, c='#D66853', s=18, alpha=0.65, edgecolors='none')
ax.set_title(f'3D Top Die  {len(top)} cells', fontsize=12, fontweight='bold')
ax.set_xlim(0, da3d[2]); ax.set_ylim(0, da3d[3]); ax.set_aspect('equal')

fig.text(0.5, 0.01,
    "2D(2A,nat)=7.00M  |  3D(2A)=5.53M  |  3D/2D=79%  ->  3D saves 21% HPWL",
    ha='center', fontsize=9, family='monospace',
    bbox=dict(boxstyle='round', facecolor='#F5F5F5', alpha=0.8))

fig.suptitle('gcd: 2D vs 3D — same silicon budget, natural density', fontsize=14, fontweight='bold')
plt.tight_layout(rect=[0, 0.05, 1, 0.95])
plt.savefig('docs/gcd_2d_vs_3d.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved")
