# Quick chart generation for hook screenshot
import pandas as pd
import matplotlib.pyplot as plt
import os

base = os.path.expanduser("~/Desktop/neca ict academy 2026 advanced ai class")
df = pd.read_csv(os.path.join(base, "sales_data_CLEANED.csv"))
df['date'] = pd.to_datetime(df['date'])

plt.style.use('seaborn-v0_8-whitegrid')
COLORS = ['#2C3E50', '#E74C3C', '#3498DB', '#2ECC71', '#F39C12']

fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle('WEEKLY SALES PERFORMANCE REPORT', fontsize=18, fontweight='bold', y=0.98)

# Pie chart
region_data = df.groupby('region')['total_sale'].sum()
axes[0,0].pie(region_data.values, labels=region_data.index, autopct='%1.1f%%', colors=COLORS, startangle=90)
axes[0,0].set_title('Revenue Distribution by Region', fontweight='bold')

# Bar chart
product_data = df.groupby('product')['total_sale'].sum().sort_values().tail(5)
axes[0,1].barh(product_data.index, product_data.values, color=COLORS[2])
axes[0,1].set_title('Top 5 Products by Revenue', fontweight='bold')

# Line chart
daily = df.groupby('date')['total_sale'].sum()
axes[0,2].plot(daily.index, daily.values, color=COLORS[0], linewidth=2, marker='o', markersize=4)
axes[0,2].set_title('Daily Revenue Trend', fontweight='bold')
axes[0,2].tick_params(axis='x', rotation=45)

# Day of week
dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
dow_data = df.groupby('day_of_week')['total_sale'].sum()
dow_data = dow_data.reindex([d for d in dow_order if d in dow_data.index])
axes[1,0].bar(dow_data.index, dow_data.values, color=COLORS[3])
axes[1,0].set_title('Revenue by Day of Week', fontweight='bold')
axes[1,0].tick_params(axis='x', rotation=45)

# Scatter
axes[1,1].scatter(df['quantity'], df['total_sale'], alpha=0.5, c=COLORS[4], edgecolors='white')
axes[1,1].set_title('Order Size vs Revenue', fontweight='bold')

# Text summary
axes[1,2].axis('off')
metrics_text = f"""
KEY METRICS

Total Revenue: ${df['total_sale'].sum():,.0f}
Total Orders: {len(df):,}
Avg Order: ${df['total_sale'].mean():,.0f}

Top Region: {region_data.idxmax()}
Top Product: {product_data.idxmax()}
"""
axes[1,2].text(0.1, 0.9, metrics_text, transform=axes[1,2].transAxes,
               fontsize=12, verticalalignment='top', fontfamily='monospace',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig(os.path.join(base, "report_charts_preview.png"), dpi=150, bbox_inches='tight', facecolor='white')
print(" Preview chart saved for hook screenshot")