#!/usr/bin/env python3
"""Displacement analysis plots."""

import re, math
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.gridspec as gridspec
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

def cells(path):
    with open(path) as f: t = f.read()
    comp = re.search(r'COMPONENTS[^;]*;(.*?)END COMPONENTS', t, re.DOTALL)
    if not comp: return {}
    section = comp.group(1)
    result = {}
    for m in re.finditer(r'- (\S+) (\S+).*?\+ PLACED\s*\(\s*(\d+)\s+(\d+)\s*\)', section, re.DOTALL):
        n, tp, x, y = m.group(1), m.group(2), int(m.group(3)), int(m.group(4))
        die = 1 if tp.endswith('_t') else (0 if tp.endswith('_b') else -1)
        result[n] = (x, y, die, tp)
    return result

c2 = cells('results/gcd/gcd_2d_2A_nat.def')
c3 = cells('results/gcd/gcd_3d.def')

data = []
for name, (x2, y2, _, _) in c2.items():
    if name not in c3: continue
    x3, y3, die, tp3 = c3[name]
    dx = x3 - x2; dy = y3 - y2
    d = math.sqrt(dx*dx + dy*dy)
    data.append((name, x2, y2, x3, y3, die, dx, dy, d, tp3))

fig = plt.figure(figsize=(16, 12))
gs = gridspec.GridSpec(2, 3, hspace=0.35, wspace=0.3)

# 1. Displacement histogram
ax = fig.add_subplot(gs[0, 0])
ds = [r[8]/2000 for r in data]
ax.hist(ds, bins=20, color='steelblue', edgecolor='white', alpha=0.8)
ax.axvline(sum(ds)/len(ds), color='red', linestyle='--', linewidth=1.5, label=f'mean={sum(ds)/len(ds):.1f}um')
ax.set_xlabel('Displacement (um)'); ax.set_ylabel('Count')
ax.set_title('Per-cell Displacement (2D -> 3D)', fontweight='bold')
ax.legend()

# 2. Displacement vs distance from 2D center
ax = fig.add_subplot(gs[0, 1])
w2, h2 = 89220, 81570; cx, cy = w2/2, h2/2
cd = [math.sqrt((r[1]-cx)**2+(r[2]-cy)**2)/2000 for r in data]
ds = [r[8]/2000 for r in data]
ax.scatter(cd, ds, c=ds, cmap='YlOrRd', s=12, alpha=0.6, edgecolors='none')
ax.set_xlabel('Distance from 2D center (um)'); ax.set_ylabel('Displacement (um)')
ax.set_title('r = 0.919: Area compression dominates', fontweight='bold')

# 3. Displacement by die
ax = fig.add_subplot(gs[0, 2])
die0 = [r[8]/2000 for r in data if r[5]==0]
die1 = [r[8]/2000 for r in data if r[5]==1]
bp = ax.boxplot([die0, die1], labels=['Die0 (n=159)', 'Die1 (n=142)'], patch_artist=True)
bp['boxes'][0].set_facecolor('#2E86AB'); bp['boxes'][1].set_facecolor('#D66853')
ax.set_ylabel('Displacement (um)')
ax.set_title('Displacement by Die', fontweight='bold')

# 4. 2D positions colored by die assignment
ax = fig.add_subplot(gs[1, 0])
for r in data:
    color = '#2E86AB' if r[5]==0 else '#D66853'
    ax.scatter(r[1]/2000, r[2]/2000, c=color, s=6, alpha=0.5, edgecolors='none')
ax.scatter([], [], c='#2E86AB', s=12, label=f'-> Die0 ({len(die0)})')
ax.scatter([], [], c='#D66853', s=12, label=f'-> Die1 ({len(die1)})')
ax.legend(loc='upper right', fontsize=8)
ax.set_xlim(0, 89); ax.set_ylim(0, 82)
ax.set_aspect('equal')
ax.set_title('2D Position -> Die Assignment', fontweight='bold')
ax.set_xlabel('X (um)'); ax.set_ylabel('Y (um)')

# 5. Displacement vectors (subsample for clarity)
ax = fig.add_subplot(gs[1, 1])
import random; random.seed(42)
sample = random.sample(data, min(80, len(data)))
for r in sample:
    ax.arrow(r[1]/2000, r[2]/2000, r[6]/2000, r[7]/2000,
             head_width=1.5, head_length=2, fc='gray', ec='gray', alpha=0.4, width=0.3)
    color = '#2E86AB' if r[5]==0 else '#D66853'
    ax.scatter(r[1]/2000, r[2]/2000, c=color, s=15, alpha=0.7, edgecolors='none', zorder=2)
ax.set_xlim(0, 89); ax.set_ylim(0, 82)
ax.set_aspect('equal')
ax.set_title('Displacement Vectors (80 sampled)', fontweight='bold')
ax.set_xlabel('X (um)'); ax.set_ylabel('Y (um)')

# 6. Displacement magnitude map
ax = fig.add_subplot(gs[1, 2])
sc = ax.scatter([r[1]/2000 for r in data], [r[2]/2000 for r in data],
                c=[r[8]/2000 for r in data], cmap='YlOrRd', s=14, alpha=0.6, edgecolors='none')
plt.colorbar(sc, ax=ax, label='Displacement (um)')
ax.set_xlim(0, 89); ax.set_ylim(0, 82)
ax.set_aspect('equal')
ax.set_title('Displacement Magnitude in 2D Space', fontweight='bold')
ax.set_xlabel('X (um)'); ax.set_ylabel('Y (um)')

fig.suptitle('gcd: Per-cell 2D -> 3D Displacement Analysis', fontsize=15, fontweight='bold', y=0.99)
plt.savefig('docs/gcd_displacement.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved")
