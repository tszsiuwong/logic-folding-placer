#!/usr/bin/env python3
"""Generate individual displacement analysis figures."""

import re, math, random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
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

ds = [r[8]/2000 for r in data]
w2, h2 = 89220, 81570; cx, cy = w2/2, h2/2
cd = [math.sqrt((r[1]-cx)**2+(r[2]-cy)**2)/2000 for r in data]
die0d = [r[8]/2000 for r in data if r[5]==0]
die1d = [r[8]/2000 for r in data if r[5]==1]

# 1. Histogram
fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(ds, bins=20, color='steelblue', edgecolor='white', alpha=0.85)
ax.axvline(sum(ds)/len(ds), color='crimson', linestyle='--', linewidth=2,
           label=f'Mean = {sum(ds)/len(ds):.1f} um')
ax.set_xlabel('Displacement (um)', fontsize=12)
ax.set_ylabel('Cell count', fontsize=12)
ax.set_title('Per-cell Displacement Distribution (2D -> 3D)', fontsize=13, fontweight='bold')
ax.legend(fontsize=11)
plt.tight_layout(); plt.savefig('figures/gcd_disp_hist.png', dpi=150); plt.close()

# 2. Correlation
fig, ax = plt.subplots(figsize=(7, 7))
ax.scatter(cd, ds, c=ds, cmap='YlOrRd', s=14, alpha=0.65, edgecolors='none')
ax.set_xlabel('Distance from 2D die center (um)', fontsize=12)
ax.set_ylabel('Displacement (um)', fontsize=12)
ax.set_title('r = 0.919 — Area compression dominates displacement', fontsize=13, fontweight='bold')
plt.tight_layout(); plt.savefig('figures/gcd_disp_corr.png', dpi=150); plt.close()

# 3. By die boxplot
fig, ax = plt.subplots(figsize=(6, 5))
bp = ax.boxplot([die0d, die1d], labels=['Die0 (n=159)', 'Die1 (n=142)'],
                patch_artist=True, widths=0.5)
bp['boxes'][0].set_facecolor('#2E86AB'); bp['boxes'][1].set_facecolor('#D66853')
for i, dd in enumerate([die0d, die1d]):
    mean_val = sum(dd)/len(dd)
    ax.text(i+1.2, mean_val, f'{mean_val:.1f}', va='center', fontsize=10, fontweight='bold')
ax.set_ylabel('Displacement (um)', fontsize=12)
ax.set_title('Displacement by Die Assignment', fontsize=13, fontweight='bold')
plt.tight_layout(); plt.savefig('figures/gcd_disp_die.png', dpi=150); plt.close()

# 4. Die assignment map
fig, ax = plt.subplots(figsize=(8, 7))
for r in data:
    color = '#2E86AB' if r[5]==0 else '#D66853'
    ax.scatter(r[1]/2000, r[2]/2000, c=color, s=10, alpha=0.55, edgecolors='none')
ax.scatter([], [], color='#2E86AB', s=15, label=f'-> Die0 ({len(die0d)})')
ax.scatter([], [], color='#D66853', s=15, label=f'-> Die1 ({len(die1d)})')
ax.legend(loc='upper right', fontsize=11)
ax.set_xlim(0, 89); ax.set_ylim(0, 82); ax.set_aspect('equal')
ax.set_xlabel('X (um)', fontsize=12); ax.set_ylabel('Y (um)', fontsize=12)
ax.set_title('2D Position vs Final Die Assignment', fontsize=13, fontweight='bold')
plt.tight_layout(); plt.savefig('figures/gcd_disp_diemap.png', dpi=150); plt.close()

# 5. Displacement vectors
fig, ax = plt.subplots(figsize=(8, 7))
random.seed(42); sample = random.sample(data, min(60, len(data)))
for r in sample:
    ax.arrow(r[1]/2000, r[2]/2000, r[6]/2000, r[7]/2000,
             head_width=1.2, head_length=1.6, fc='#555555', ec='#555555',
             alpha=0.35, width=0.2, length_includes_head=True)
    color = '#2E86AB' if r[5]==0 else '#D66853'
    ax.scatter(r[1]/2000, r[2]/2000, c=color, s=18, alpha=0.7, edgecolors='none', zorder=2)
ax.set_xlim(0, 89); ax.set_ylim(0, 82); ax.set_aspect('equal')
ax.set_xlabel('X (um)', fontsize=12); ax.set_ylabel('Y (um)', fontsize=12)
ax.set_title('Displacement Vectors (60 sampled)', fontsize=13, fontweight='bold')
plt.tight_layout(); plt.savefig('figures/gcd_disp_vec.png', dpi=150); plt.close()

# 6. Heatmap
fig, ax = plt.subplots(figsize=(8, 7))
sc = ax.scatter([r[1]/2000 for r in data], [r[2]/2000 for r in data],
                c=[r[8]/2000 for r in data], cmap='YlOrRd', s=16, alpha=0.55, edgecolors='none')
cbar = plt.colorbar(sc, ax=ax, shrink=0.82)
cbar.set_label('Displacement (um)', fontsize=11)
ax.set_xlim(0, 89); ax.set_ylim(0, 82); ax.set_aspect('equal')
ax.set_xlabel('X (um)', fontsize=12); ax.set_ylabel('Y (um)', fontsize=12)
ax.set_title('Displacement Magnitude in 2D Space', fontsize=13, fontweight='bold')
plt.tight_layout(); plt.savefig('figures/gcd_disp_heat.png', dpi=150); plt.close()

print("All 6 figures saved to figures/")
