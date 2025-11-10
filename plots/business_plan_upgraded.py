from matplotlib.patches import Patch
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Create figure directory for saving
if not os.path.exists('plots'):
    os.makedirs('plots')

# 1. FINANCIAL PROJECTIONS (24-MONTH FORECAST)
months = [3, 6, 12, 18, 24, 26]
users = [1000, 3000, 12000, 20000, 28000, 30000]
paid = [80, 300, 1440, 2800, 3920, 4500]
cvr = [8, 10, 12, 14, 14, 15]
mrr = [639, 2397, 11509, 22372, 31321, 35955]
revenue = [1917, 7191, 34527, 67116, 93963, 107865]
costs = [13500, 12000, 38000, 52000, 62000, 65000]
net = [-11583, -4809, -3473, 15116, 31963, 42865]
cumulative_cash = [-48583, -67974, -89341, -53105, 1830, 44695]

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

# Plot 1: User Growth
ax1.plot(months, users, 'o-', linewidth=3, markersize=10,
         label='Total Users', color='#2ecc71')
ax1_twin = ax1.twinx()
ax1_twin.plot(months, paid, 's-', linewidth=3, markersize=10,
              label='Paid Users', color='#e74c3c')
ax1.set_xlabel('Month', fontsize=12, fontweight='bold')
ax1.set_ylabel('Total Users', fontsize=12, fontweight='bold', color='#2ecc71')
ax1_twin.set_ylabel('Paid Users', fontsize=12,
                    fontweight='bold', color='#e74c3c')
ax1.set_title('User Growth Trajectory (24 Months)',
              fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.legend(loc='upper left')
ax1_twin.legend(loc='upper right')
ax1.tick_params(axis='y', labelcolor='#2ecc71')
ax1_twin.tick_params(axis='y', labelcolor='#e74c3c')

# Plot 2: Conversion Rate & MRR
ax2.bar(months, cvr, alpha=0.7, color='#3498db', label='Conversion Rate (%)')
ax2_twin = ax2.twinx()
ax2_twin.plot(months, [m/1000 for m in mrr], 'ro-',
              linewidth=3, markersize=10, label='MRR (€K)')
ax2.set_xlabel('Month', fontsize=12, fontweight='bold')
ax2.set_ylabel('Conversion Rate (%)', fontsize=12,
               fontweight='bold', color='#3498db')
ax2_twin.set_ylabel('MRR (€K)', fontsize=12,
                    fontweight='bold', color='#e74c3c')
ax2.set_title('Conversion Rate & Monthly Recurring Revenue',
              fontsize=14, fontweight='bold')
ax2.legend(loc='upper left')
ax2_twin.legend(loc='upper right')
ax2.tick_params(axis='y', labelcolor='#3498db')
ax2_twin.tick_params(axis='y', labelcolor='#e74c3c')

# Plot 3: Revenue vs Costs
ax3.plot(months, [r/1000 for r in revenue], 'o-', linewidth=3,
         markersize=10, label='Revenue', color='#27ae60')
ax3.plot(months, [c/1000 for c in costs], 's-', linewidth=3,
         markersize=10, label='Costs', color='#e67e22')
ax3.fill_between(months, [r/1000 for r in revenue], [c/1000 for c in costs],
                 where=[r > c for r, c in zip(revenue, costs)], alpha=0.3, color='green', label='Profit')
ax3.fill_between(months, [r/1000 for r in revenue], [c/1000 for c in costs],
                 where=[r <= c for r, c in zip(revenue, costs)], alpha=0.3, color='red', label='Loss')
ax3.axhline(y=0, color='black', linestyle='--', linewidth=1)
ax3.set_xlabel('Month', fontsize=12, fontweight='bold')
ax3.set_ylabel('Amount (€K)', fontsize=12, fontweight='bold')
ax3.set_title('Revenue vs Costs (Break-Even Analysis)',
              fontsize=14, fontweight='bold')
ax3.legend()
ax3.grid(True, alpha=0.3)

# Plot 4: Cumulative Cash Flow
colors = ['red' if x < 0 else 'green' for x in cumulative_cash]
ax4.bar(months, [c/1000 for c in cumulative_cash], color=colors, alpha=0.7)
ax4.axhline(y=0, color='black', linestyle='--', linewidth=2)
ax4.axvline(x=26, color='gold', linestyle='--',
            linewidth=2, label='Break-Even (Month 26)')
ax4.set_xlabel('Month', fontsize=12, fontweight='bold')
ax4.set_ylabel('Cumulative Cash (€K)', fontsize=12, fontweight='bold')
ax4.set_title('Cumulative Cash Flow (Path to Profitability)',
              fontsize=14, fontweight='bold')
ax4.legend()
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('plots/1_financial_projections.png', dpi=300, bbox_inches='tight')
print("✓ Saved: plots/1_financial_projections.png")
plt.show()

# 2. UNIT ECONOMICS COMPARISON (V1 vs V2)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# V1 vs V2 Comparison
metrics = ['Monthly Price', 'Variable Cost',
           'Contribution\nMargin', 'LTV', 'CAC\n(Blended)', 'LTV:CAC']
v1_values = [5.99, 0.85, 5.14, 71.88, 14, 5.3]
v2_values = [7.99, 0.95, 7.04, 95.88, 40, 2.4]

x = np.arange(len(metrics))
width = 0.35

bars1 = ax1.bar(x - width/2, v1_values, width,
                label='V1 (Broken)', color='#e74c3c', alpha=0.7)
bars2 = ax1.bar(x + width/2, v2_values, width,
                label='V2 (Fixed)', color='#2ecc71', alpha=0.7)

ax1.set_ylabel('Value (€)', fontsize=12, fontweight='bold')
ax1.set_title('Unit Economics: V1 vs V2 Comparison',
              fontsize=14, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(metrics)
ax1.legend()
ax1.grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                 f'€{height:.2f}' if height < 100 else f'{height:.1f}',
                 ha='center', va='bottom', fontsize=9)

# LTV:CAC Waterfall
scenarios = ['LTV\n(€95.88)', 'Paid CAC\n(-€100)', 'Organic 60%\n(+€60)',
             'Blended CAC\n(€40)', 'Final\nLTV:CAC\n(2.4:1)']
values = [95.88, -100, 60, 40, 95.88/40]
cumulative = [95.88, 95.88-100, 95.88-100+60, 40, 95.88/40]

colors_wf = ['green', 'red', 'green', 'orange', 'gold']
ax2.bar(range(len(scenarios)), values, color=colors_wf, alpha=0.7)
ax2.axhline(y=0, color='black', linestyle='--', linewidth=1)
ax2.set_ylabel('Value (€ or Ratio)', fontsize=12, fontweight='bold')
ax2.set_title('Path to Viable Unit Economics', fontsize=14, fontweight='bold')
ax2.set_xticks(range(len(scenarios)))
ax2.set_xticklabels(scenarios, fontsize=10)
ax2.grid(True, alpha=0.3, axis='y')

# Add value labels
for i, (val, cum) in enumerate(zip(values, cumulative)):
    if i < 4:
        ax2.text(i, val, f'€{val:.0f}' if abs(val) > 10 else f'{val:.2f}',
                 ha='center', va='bottom' if val > 0 else 'top', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('plots/2_unit_economics.png', dpi=300, bbox_inches='tight')
print("✓ Saved: plots/2_unit_economics.png")
plt.show()

# 3. MARKET OPPORTUNITY & COMPETITIVE GAPS
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Duolingo Problem Concentration
problems = ['Monetization Issues',
            'Hearts / Energy System',
            'AI Content Quality',
            'Ads Frequency',
            'Removed Features',
            'Technical Bugs',
            'Progress Loss',
            'UI/UX Issues',
            'Non-Problem / Neutral / Satisfied']
percentages = [14.0, 13.2, 3.2, 2.2, 1.5, 0.9, 0.7, 0.6, 63.7]
colors_prob = ['#e74c3c', '#f39c12', '#e67e22', '#d35400',
               '#c0392b', '#8e44ad', '#2980b9', '#27ae60', '#95a5a6']
explode = (0.12, 0.12, 0, 0, 0, 0, 0, 0, 0)

ax1.pie(percentages, explode=explode, labels=problems, colors=colors_prob,
        autopct='%1.1f%%', shadow=True, startangle=90, textprops={'fontsize': 12, 'fontweight': 'bold'})
ax1.set_title('Distribution of User Feedback Themes\n(Full Review Breakdown)',
              fontsize=14, fontweight='bold')

# Feature Opportunity Scores
features = ['Grammar\nExplanations', 'Conversation\nPractice', 'Topic\nVocabulary',
            'Fair Pricing', 'Streak System']
demand = [85, 80, 70, 73, 75]
gap_score = [60, 65, 40, 100, 30]

x = np.arange(len(features))
width = 0.35

bars1 = ax2.bar(x - width/2, demand, width,
                label='Interview Demand (%)', color='#3498db', alpha=0.7)
bars2 = ax2.bar(x + width/2, gap_score, width,
                label='Opportunity Score', color='#f39c12', alpha=0.7)

ax2.set_ylabel('Score / Percentage', fontsize=12, fontweight='bold')
ax2.set_title('Feature Demand & Competitive Gap Analysis',
              fontsize=14, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(features)
ax2.legend()
ax2.grid(True, alpha=0.3, axis='y')
ax2.set_ylim(0, 110)

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                 f'{int(height)}',
                 ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('plots/3_market_opportunity.png', dpi=300, bbox_inches='tight')
print("✓ Saved: plots/3_market_opportunity.png")
plt.show()

# 4. CUSTOMER ACQUISITION CHANNELS
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Launch Channels (Month 1-3)
channels = ['SEO\nContent', 'Reddit/\nForums',
            'Partner-\nships', 'Google\nAds', 'Facebook/\nIG']
budget = [2000, 0, 0, 3000, 1000]
signups = [500, 300, 200, 150, 50]
cac = [4, 0, 0, 250, 250]

x = np.arange(len(channels))
width = 0.35

bars1 = ax1.bar(x - width/2, budget, width,
                label='Budget (€)', color='#e74c3c', alpha=0.7)
ax1_twin = ax1.twinx()
bars2 = ax1_twin.bar(x + width/2, signups, width,
                     label='Target Signups', color='#2ecc71', alpha=0.7)

ax1.set_ylabel('Budget (€)', fontsize=12, fontweight='bold', color='#e74c3c')
ax1_twin.set_ylabel('Signups', fontsize=12, fontweight='bold', color='#2ecc71')
ax1.set_title('Go-to-Market Channels (Month 1-3)',
              fontsize=14, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(channels)
ax1.legend(loc='upper left')
ax1_twin.legend(loc='upper right')
ax1.tick_params(axis='y', labelcolor='#e74c3c')
ax1_twin.tick_params(axis='y', labelcolor='#2ecc71')

# Organic vs Paid Mix Over Time
months_acq = [3, 6, 12, 18, 24]
organic_pct = [60, 65, 70, 75, 80]
paid_pct = [40, 35, 30, 25, 20]

ax2.fill_between(months_acq, 0, organic_pct, alpha=0.7,
                 color='#2ecc71', label='Organic %')
ax2.fill_between(months_acq, organic_pct, 100, alpha=0.7,
                 color='#e74c3c', label='Paid %')
ax2.plot(months_acq, organic_pct, 'o-', linewidth=3,
         markersize=10, color='darkgreen')

ax2.set_xlabel('Month', fontsize=12, fontweight='bold')
ax2.set_ylabel('Acquisition Mix (%)', fontsize=12, fontweight='bold')
ax2.set_title('Organic vs Paid Acquisition Strategy',
              fontsize=14, fontweight='bold')
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.set_ylim(0, 100)

# Add percentage labels
for i, (m, o) in enumerate(zip(months_acq, organic_pct)):
    ax2.text(m, o/2, f'{o}%', ha='center', va='center',
             fontsize=11, fontweight='bold', color='white')
    ax2.text(m, o + (100-o)/2, f'{100-o}%', ha='center',
             va='center', fontsize=11, fontweight='bold', color='white')

plt.tight_layout()
plt.savefig('plots/4_customer_acquisition.png', dpi=300, bbox_inches='tight')
print("✓ Saved: plots/4_customer_acquisition.png")
plt.show()

# 5. SENSITIVITY ANALYSIS
fig, ax = plt.subplots(figsize=(14, 8))

scenarios = ['Pessimistic\n(6% CVR, 10% Churn)',
             'Base Conservative\n(8-12% CVR, 8% Churn)',
             'Optimistic\n(15% CVR, 6% Churn)']
month_12_mrr = [5754, 11509, 21564]
breakeven_month = [36, 26, 18]
probability = [20, 55, 25]

x = np.arange(len(scenarios))
width = 0.25

bars1 = ax.bar(x - width, [m/1000 for m in month_12_mrr], width,
               label='Month 12 MRR (€K)', color='#3498db', alpha=0.7)
bars2 = ax.bar(x, breakeven_month, width,
               label='Break-Even Month', color='#e67e22', alpha=0.7)
bars3 = ax.bar(x + width, probability, width,
               label='Probability (%)', color='#2ecc71', alpha=0.7)

ax.set_ylabel('Value', fontsize=12, fontweight='bold')
ax.set_title('Financial Scenarios: Sensitivity Analysis',
             fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(scenarios, fontsize=11)
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

# Add value labels
for bars in [bars1, bars2, bars3]:
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}' if height > 100 else f'{int(height)}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('plots/5_sensitivity_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Saved: plots/5_sensitivity_analysis.png")
plt.show()

# 6. TIMELINE & MILESTONES (GANTT-STYLE)
fig, ax = plt.subplots(figsize=(16, 10))

phases = [
    ('Pre-Launch Validation', 0, 4, '#3498db'),
    ('MVP Phase 1: Core Loop', 4, 8, '#e67e22'),
    ('Beta Launch & Testing', 8, 10, '#9b59b6'),
    ('MVP Phase 2: AI Conversation', 10, 18, '#e74c3c'),
    ('Public Launch', 18, 19, '#2ecc71'),
    ('Scale & Optimize', 19, 24, '#f39c12'),
]

milestones = [
    (4, '€10K Pre-Sales\nValidation Gate', '#3498db'),
    (10, 'Phase 1 Decision Gate\n(NPS>30, CVR>6%)', '#9b59b6'),
    (18, 'Public Launch\n(1K signups)', '#2ecc71'),
    (26, 'Break-Even\n(€36K MRR)', '#f39c12'),
]

for i, (phase, start, end, color) in enumerate(phases):
    ax.barh(i, end - start, left=start, height=0.6, color=color,
            alpha=0.8, edgecolor='black', linewidth=2)
    ax.text(start + (end - start) / 2, i, phase, ha='center', va='center',
            fontsize=11, fontweight='bold', color='white')

# Add milestones
for week, label, color in milestones:
    ax.axvline(x=week, color=color, linestyle='--', linewidth=2, alpha=0.7)
    ax.text(week, len(phases) - 0.5, label, rotation=0, ha='center', va='bottom',
            fontsize=10, fontweight='bold', color=color,
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor=color, linewidth=2))

ax.set_xlabel('Week', fontsize=12, fontweight='bold')
ax.set_ylabel('Phase', fontsize=12, fontweight='bold')
ax.set_title('TaalBuddy 18-Week Development Timeline',
             fontsize=14, fontweight='bold')
ax.set_yticks(range(len(phases)))
ax.set_yticklabels([])
ax.set_xlim(0, 28)
ax.grid(True, alpha=0.3, axis='x')
ax.invert_yaxis()

plt.tight_layout()
plt.savefig('plots/6_timeline_gantt.png', dpi=300, bbox_inches='tight')
print("✓ Saved: plots/6_timeline_gantt.png")
plt.show()

# 7. FUNDING & BURN RATE
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Funding Stages
stages = ['Bootstrap\n(Month 0-4)', 'Angel Round\n(Month 5-6)',
          'Seed Round\n(Month 15-18)']
amounts = [50000, 75000, 300000]
valuations = [0, 350000, 2000000]
equity_dilution = [0, 21.4, 15]

x = np.arange(len(stages))
width = 0.4

bars1 = ax1.bar(x - width/2, [a/1000 for a in amounts],
                width, label='Funding (€K)', color='#2ecc71', alpha=0.7)
ax1_twin = ax1.twinx()
bars2 = ax1_twin.bar(x + width/2, equity_dilution, width,
                     label='Equity Dilution (%)', color='#e74c3c', alpha=0.7)

ax1.set_ylabel('Funding Amount (€K)', fontsize=12,
               fontweight='bold', color='#2ecc71')
ax1_twin.set_ylabel('Equity Dilution (%)', fontsize=12,
                    fontweight='bold', color='#e74c3c')
ax1.set_title('Funding Strategy & Dilution', fontsize=14, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(stages)
ax1.legend(loc='upper left')
ax1_twin.legend(loc='upper right')
ax1.tick_params(axis='y', labelcolor='#2ecc71')
ax1_twin.tick_params(axis='y', labelcolor='#e74c3c')

# Add value labels
for bar in bars1:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
             f'€{int(height)}K',
             ha='center', va='bottom', fontsize=10, fontweight='bold')

for bar in bars2:
    height = bar.get_height()
    if height > 0:
        ax1_twin.text(bar.get_x() + bar.get_width()/2., height,
                      f'{height:.1f}%',
                      ha='center', va='bottom', fontsize=10, fontweight='bold')

# Monthly Burn Rate
months_burn = [3, 6, 12, 18, 24]
burn_rate = [13.5, 12, 38, 52, 62]
team_size = [4, 4, 6, 9, 12]

ax2.bar(months_burn, burn_rate, alpha=0.7,
        color='#e67e22', label='Monthly Burn (€K)')
ax2_twin = ax2.twinx()
ax2_twin.plot(months_burn, team_size, 'go-', linewidth=3,
              markersize=10, label='Team Size')

ax2.set_xlabel('Month', fontsize=12, fontweight='bold')
ax2.set_ylabel('Monthly Burn (€K)', fontsize=12,
               fontweight='bold', color='#e67e22')
ax2_twin.set_ylabel('Team Size', fontsize=12, fontweight='bold', color='green')
ax2.set_title('Burn Rate & Team Growth', fontsize=14, fontweight='bold')
ax2.legend(loc='upper left')
ax2_twin.legend(loc='upper right')
ax2.tick_params(axis='y', labelcolor='#e67e22')
ax2_twin.tick_params(axis='y', labelcolor='green')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('plots/7_funding_burn_rate.png', dpi=300, bbox_inches='tight')
print("✓ Saved: plots/7_funding_burn_rate.png")
plt.show()

# 8. RISK MATRIX
fig, ax = plt.subplots(figsize=(14, 10))

risks = [
    ('Unit economics\nremain broken', 60, 100, 'Addressed', '#2ecc71'),
    ('Angel round fails', 40, 100, 'Mitigated', '#f39c12'),
    ('AI conversation\nquality issues', 50, 80, 'De-risked', '#3498db'),
    ('Duolingo removes\nenergy system', 30, 90, 'Monitor', '#e67e22'),
    ('Content creation\nbottleneck', 40, 60, 'Adjusted', '#9b59b6'),
]

for risk, prob, impact, status, color in risks:
    size = prob * impact / 10
    ax.scatter(prob, impact, s=size*5, alpha=0.6,
               color=color, edgecolors='black', linewidth=2)
    ax.text(prob, impact, risk, ha='center',
            va='center', fontsize=10, fontweight='bold')

# Add quadrant labels
ax.axhline(y=50, color='black', linestyle='--', linewidth=1, alpha=0.5)
ax.axvline(x=50, color='black', linestyle='--', linewidth=1, alpha=0.5)
ax.text(25, 90, 'Low Probability\nHigh Impact', ha='center', va='center', fontsize=12,
        bbox=dict(boxstyle='round', facecolor='#e74c3c', alpha=0.3))
ax.text(75, 90, 'High Probability\nHigh Impact', ha='center', va='center', fontsize=12,
        bbox=dict(boxstyle='round', facecolor='#e74c3c', alpha=0.5))
ax.text(25, 25, 'Low Probability\nLow Impact', ha='center', va='center', fontsize=12,
        bbox=dict(boxstyle='round', facecolor='#2ecc71', alpha=0.3))
ax.text(75, 25, 'High Probability\nLow Impact', ha='center', va='center', fontsize=12,
        bbox=dict(boxstyle='round', facecolor='#f39c12', alpha=0.3))

ax.set_xlabel('Probability (%)', fontsize=12, fontweight='bold')
ax.set_ylabel('Impact (Severity)', fontsize=12, fontweight='bold')
ax.set_title('Risk Assessment Matrix (Top 5 Critical Risks)',
             fontsize=14, fontweight='bold')
ax.set_xlim(0, 100)
ax.set_ylim(0, 110)
ax.grid(True, alpha=0.3)

# Legend
legend_elements = [Patch(facecolor=c, label=s) for _, _, _, s, c in risks]
ax.legend(handles=legend_elements, loc='lower right', fontsize=10)

plt.tight_layout()
plt.savefig('plots/8_risk_matrix.png', dpi=300, bbox_inches='tight')
print("✓ Saved: plots/8_risk_matrix.png")
plt.show()

# 9. COMPETITIVE POSITIONING
fig, ax = plt.subplots(figsize=(14, 10))

competitors = [
    ('TaalBuddy', 7.99, 85, 2000),
    ('Duolingo', 0, 40, 15000),
    ('Babbel', 12.99, 75, 8000),
    ('ChatGPT', 20, 70, 5000),
    ('Falou', 9.99, 55, 1000),
]

colors_comp = ['#2ecc71', '#e74c3c', '#3498db', '#9b59b6', '#f39c12']

for i, (name, price, quality, users) in enumerate(competitors):
    ax.scatter(price, quality, s=users/5, alpha=0.6, color=colors_comp[i],
               edgecolors='black', linewidth=2, label=name)
    ax.text(price, quality + 3, name, ha='center',
            va='bottom', fontsize=11, fontweight='bold')

ax.set_xlabel('Monthly Price (€)', fontsize=12, fontweight='bold')
ax.set_ylabel('Quality Score (Grammar + Conversation)',
              fontsize=12, fontweight='bold')
ax.set_title('Competitive Positioning Map\n(Bubble size = User base estimate)',
             fontsize=14, fontweight='bold')
ax.legend(loc='upper left', fontsize=11)
ax.grid(True, alpha=0.3)
ax.set_xlim(-2, 22)
ax.set_ylim(30, 95)

# Add positioning zones
ax.axhspan(70, 95, alpha=0.1, color='green', label='High Quality Zone')
ax.axhspan(30, 70, alpha=0.1, color='yellow')
ax.axvspan(0, 10, alpha=0.1, color='blue', label='Affordable Zone')

plt.tight_layout()
plt.savefig('plots/9_competitive_positioning.png',
            dpi=300, bbox_inches='tight')
print("✓ Saved: plots/9_competitive_positioning.png")
plt.show()

# 10. KEY METRICS DASHBOARD
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3)

# Metric 1: WAL (Weekly Active Learners)
ax1 = fig.add_subplot(gs[0, :2])
months_wal = [3, 6, 12]
wal = [500, 1800, 7800]
wal_pct = [50, 60, 65]

ax1.bar(months_wal, wal, alpha=0.7, color='#3498db', width=2)
ax1_twin = ax1.twinx()
ax1_twin.plot(months_wal, wal_pct, 'ro-', linewidth=3,
              markersize=12, label='% of Active Users')
ax1.set_xlabel('Month', fontsize=11, fontweight='bold')
ax1.set_ylabel('Weekly Active Learners', fontsize=11,
               fontweight='bold', color='#3498db')
ax1_twin.set_ylabel('WAL %', fontsize=11, fontweight='bold', color='red')
ax1.set_title('North Star Metric: Weekly Active Learners (10+ lessons/week)',
              fontsize=12, fontweight='bold')
ax1.tick_params(axis='y', labelcolor='#3498db')
ax1_twin.tick_params(axis='y', labelcolor='red')
ax1.grid(True, alpha=0.3)

# Metric 2: Retention Cohorts
ax2 = fig.add_subplot(gs[0, 2])
retention_days = ['D1', 'D7', 'D30', 'D90']
retention_rates = [60, 45, 35, 25]
colors_ret = ['#2ecc71', '#f39c12', '#e67e22', '#e74c3c']

ax2.barh(retention_days, retention_rates, color=colors_ret, alpha=0.7)
ax2.set_xlabel('Retention %', fontsize=11, fontweight='bold')
ax2.set_title('User Retention Targets', fontsize=12, fontweight='bold')
ax2.set_xlim(0, 100)
for i, v in enumerate(retention_rates):
    ax2.text(v + 2, i, f'{v}%', va='center', fontsize=10, fontweight='bold')

# Metric 3: Conversion Funnel
ax3 = fig.add_subplot(gs[1, :])
funnel_stages = ['Visitors', 'Signups',
                 'Active\n(7 days)', 'Trial\n(14 days)', 'Paid']
funnel_values = [10000, 1200, 800, 400, 96]
funnel_rates = [100, 12, 8, 4, 0.96]

colors_funnel = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(funnel_stages)))
bars = ax3.bar(range(len(funnel_stages)), funnel_values,
               color=colors_funnel, alpha=0.8, edgecolor='black', linewidth=2)

ax3.set_ylabel('Users', fontsize=11, fontweight='bold')
ax3.set_yscale('log')
ax3.set_title('Conversion Funnel (Month 3 Projections)',
              fontsize=12, fontweight='bold')
ax3.set_xticks(range(len(funnel_stages)))
ax3.set_xticklabels(funnel_stages, fontsize=10)
ax3.grid(True, alpha=0.3, axis='y')

# Add conversion rates
for i in range(len(funnel_stages) - 1):
    conversion = (funnel_values[i+1] / funnel_values[i]) * 100
    ax3.annotate(f'{conversion:.1f}%',
                 xy=(i + 0.5, np.sqrt(funnel_values[i] * funnel_values[i+1])),
                 ha='center', va='center', fontsize=10, fontweight='bold',
                 bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))

# Add value labels
for bar, val in zip(bars, funnel_values):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height,
             f'{val:,}',
             ha='center', va='bottom', fontsize=10, fontweight='bold')

# Metric 4: Customer Acquisition Cost Breakdown
ax4 = fig.add_subplot(gs[2, 0])
cac_components = ['CPC', 'Landing\nCVR',
                  'Signup\nCAC', 'Paid\nCVR', 'Final\nCAC']
cac_values = [3.5, 15, 20, 8, 250]
ax4.plot(range(len(cac_components)), cac_values, 'o-',
         linewidth=3, markersize=12, color='#e74c3c')
ax4.set_ylabel('Cost (€) / Rate (%)', fontsize=11, fontweight='bold')
ax4.set_title('CAC Calculation Path', fontsize=12, fontweight='bold')
ax4.set_xticks(range(len(cac_components)))
ax4.set_xticklabels(cac_components, fontsize=9)
ax4.grid(True, alpha=0.3)
for i, val in enumerate(cac_values):
    ax4.text(i, val + 10, f'€{val:.1f}' if i != 1 and i != 3 else f'{val}%',
             ha='center', fontsize=9, fontweight='bold')

# Metric 5: NPS Score Progression
ax5 = fig.add_subplot(gs[2, 1])
months_nps = [3, 6, 12, 24]
nps_scores = [30, 40, 50, 60]
nps_colors = ['#f39c12', '#3498db', '#2ecc71', '#27ae60']

bars_nps = ax5.bar(months_nps, nps_scores,
                   color=nps_colors, alpha=0.7, width=2)
ax5.axhline(y=50, color='green', linestyle='--',
            linewidth=2, label='Excellent (50+)')
ax5.axhline(y=30, color='orange', linestyle='--',
            linewidth=2, label='Good (30+)')
ax5.set_xlabel('Month', fontsize=11, fontweight='bold')
ax5.set_ylabel('NPS Score', fontsize=11, fontweight='bold')
ax5.set_title('Net Promoter Score Target', fontsize=12, fontweight='bold')
ax5.set_ylim(0, 80)
ax5.legend(fontsize=9)
ax5.grid(True, alpha=0.3)

for bar in bars_nps:
    height = bar.get_height()
    ax5.text(bar.get_x() + bar.get_width()/2., height,
             f'{int(height)}',
             ha='center', va='bottom', fontsize=11, fontweight='bold')

# Metric 6: Churn Rate
ax6 = fig.add_subplot(gs[2, 2])
months_churn = [3, 6, 12, 24]
churn_rates = [10, 8, 8, 6]
ax6.plot(months_churn, churn_rates, 'o-',
         linewidth=3, markersize=12, color='#e74c3c')
ax6.fill_between(months_churn, churn_rates, alpha=0.3, color='#e74c3c')
ax6.set_xlabel('Month', fontsize=11, fontweight='bold')
ax6.set_ylabel('Monthly Churn %', fontsize=11, fontweight='bold')
ax6.set_title('Monthly Churn Rate Target', fontsize=12, fontweight='bold')
ax6.set_ylim(0, 15)
ax6.grid(True, alpha=0.3)
ax6.invert_yaxis()  # Lower is better

for x, y in zip(months_churn, churn_rates):
    ax6.text(x, y - 0.5, f'{y}%', ha='center', fontsize=10, fontweight='bold')

plt.suptitle('TaalBuddy Key Performance Indicators Dashboard',
             fontsize=16, fontweight='bold', y=0.995)
plt.savefig('plots/10_kpi_dashboard.png', dpi=300, bbox_inches='tight')
print("✓ Saved: plots/10_kpi_dashboard.png")
plt.show()

# 11. PRICING COMPARISON
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Pricing Table
competitors_price = [
    'Duolingo\n(Free)', 'TaalBuddy\n(Premium)', 'Falou', 'Babbel', 'ChatGPT\nPlus']
prices = [0, 7.99, 9.99, 12.99, 20]
value_scores = [40, 85, 55, 75, 70]

colors_price = ['#95a5a6', '#2ecc71', '#f39c12', '#3498db', '#9b59b6']
bars_price = ax1.barh(competitors_price, prices, color=colors_price,
                      alpha=0.7, edgecolor='black', linewidth=2)

ax1.set_xlabel('Monthly Price (€)', fontsize=12, fontweight='bold')
ax1.set_title('Competitive Pricing Landscape', fontsize=14, fontweight='bold')
ax1.set_xlim(0, 25)
ax1.grid(True, alpha=0.3, axis='x')

for i, (bar, price, score) in enumerate(zip(bars_price, prices, value_scores)):
    width = bar.get_width()
    if price > 0:
        ax1.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                 f'€{price:.2f} (Value: {score})',
                 va='center', fontsize=10, fontweight='bold')
    else:
        ax1.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                 f'Free (Value: {score})',
                 va='center', fontsize=10, fontweight='bold')

# Value for Money Analysis
ax2.scatter(prices, value_scores, s=[p*100 if p > 0 else 500 for p in prices],
            c=colors_price, alpha=0.6, edgecolors='black', linewidth=2)

for name, price, score in zip(competitors_price, prices, value_scores):
    ax2.text(price, score + 2, name.replace('\n', ' '),
             ha='center', fontsize=10, fontweight='bold')

# Add value line
ax2.plot([0, 20], [40, 90], 'k--', alpha=0.3,
         linewidth=2, label='Expected Value Line')

# Highlight TaalBuddy's position
ax2.annotate('TaalBuddy:\nBest Value\nfor Money',
             xy=(7.99, 85), xytext=(12, 60),
             arrowprops=dict(arrowstyle='->', color='green', lw=3),
             fontsize=12, fontweight='bold', color='green',
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))

ax2.set_xlabel('Monthly Price (€)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Value Score (Quality + Features)',
               fontsize=12, fontweight='bold')
ax2.set_title('Price vs Value Analysis', fontsize=14, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.legend()
ax2.set_xlim(-2, 22)
ax2.set_ylim(30, 95)

plt.tight_layout()
plt.savefig('plots/11_pricing_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Saved: plots/11_pricing_comparison.png")
plt.show()

# 12. FEATURE PRIORITY MATRIX
fig, ax = plt.subplots(figsize=(14, 10))

features_priority = [
    ('Grammar\nTooltips', 85, 90, 'Phase 1', '#2ecc71'),
    ('Structured\nLessons', 95, 95, 'Phase 1', '#2ecc71'),
    ('Fair Practice\n(No Energy)', 80, 100, 'Phase 1', '#2ecc71'),
    ('AI Text\nConversation', 80, 70, 'Phase 2', '#3498db'),
    ('Progress\nDashboard', 75, 80, 'Phase 1', '#2ecc71'),
    ('Dark Mode', 40, 30, 'Phase 2', '#95a5a6'),
    ('Voice Chat', 60, 50, 'Future', '#f39c12'),
    ('Taal Buddy\nMatching', 50, 60, 'Future', '#f39c12'),
]

for feature, demand, ease, phase, color in features_priority:
    size = (demand * ease) / 20
    ax.scatter(ease, demand, s=size*5, alpha=0.6,
               color=color, edgecolors='black', linewidth=2)
    ax.text(ease, demand, feature, ha='center',
            va='center', fontsize=9, fontweight='bold')

# Add quadrant lines
ax.axhline(y=70, color='black', linestyle='--', linewidth=1, alpha=0.5)
ax.axvline(x=70, color='black', linestyle='--', linewidth=1, alpha=0.5)

# Add quadrant labels
ax.text(85, 92, 'Quick Wins\n(High Demand, Easy)', ha='center', fontsize=11,
        bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
ax.text(85, 50, 'Fill-Ins\n(Low Demand, Easy)', ha='center', fontsize=11,
        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.5))
ax.text(45, 92, 'Major Projects\n(High Demand, Hard)', ha='center', fontsize=11,
        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
ax.text(45, 50, 'Time Sinks\n(Low Demand, Hard)', ha='center', fontsize=11,
        bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.5))

ax.set_xlabel('Ease of Implementation', fontsize=12, fontweight='bold')
ax.set_ylabel('User Demand / Impact', fontsize=12, fontweight='bold')
ax.set_title('Feature Priority Matrix (Effort vs Impact)',
             fontsize=14, fontweight='bold')
ax.set_xlim(20, 100)
ax.set_ylim(20, 100)
ax.grid(True, alpha=0.3)

# Legend
legend_elements = [
    Patch(facecolor='#2ecc71', label='Phase 1 (Week 1-8)'),
    Patch(facecolor='#3498db', label='Phase 2 (Week 11-18)'),
    Patch(facecolor='#f39c12', label='Future (Month 12+)'),
    Patch(facecolor='#95a5a6', label='Low Priority')
]
ax.legend(handles=legend_elements, loc='lower left', fontsize=11)

plt.tight_layout()
plt.savefig('plots/12_feature_priority.png', dpi=300, bbox_inches='tight')
print("✓ Saved: plots/12_feature_priority.png")
plt.show()

print("\n" + "="*60)
print("✓ ALL PLOTS SAVED SUCCESSFULLY!")
print("="*60)
print("\nPlots saved in 'plots/' directory:")
print("  1. plots/1_financial_projections.png")
print("  2. plots/2_unit_economics.png")
print("  3. plots/3_market_opportunity.png")
print("  4. plots/4_customer_acquisition.png")
print("  5. plots/5_sensitivity_analysis.png")
print("  6. plots/6_timeline_gantt.png")
print("  7. plots/7_funding_burn_rate.png")
print("  8. plots/8_risk_matrix.png")
print("  9. plots/9_competitive_positioning.png")
print(" 10. plots/10_kpi_dashboard.png")
print(" 11. plots/11_pricing_comparison.png")
print(" 12. plots/12_feature_priority.png")
print("\nTo download in Colab, run:")
print("  from google.colab import files")
print("  import shutil")
print("  shutil.make_archive('taalbuddy_plots', 'zip', 'plots')")
print("  files.download('taalbuddy_plots.zip')")
print("="*60)
