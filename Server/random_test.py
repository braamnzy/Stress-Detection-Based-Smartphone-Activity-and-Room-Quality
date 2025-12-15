"""
RANDOM TEST DATA GENERATOR FOR FUZZY LOGIC STRESS DETECTION
============================================================
Generate visualizations dengan data random realistis!

Usage:
    1. Edit CONFIG untuk jumlah sample yang diinginkan
    2. Run: python random_test_generator.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import random

try:
    import fuzzy_logic
    print("✅ Modul 'fuzzy_logic' berhasil diimpor.")
    SKFUZZY_AVAILABLE = True
except ImportError as e:
    print(f"❌ ERROR: Gagal impor fuzzy_logic: {e}")
    print("   Menggunakan data statis yang diekstrak dari output yang diharapkan.")
    SKFUZZY_AVAILABLE = False
except Exception as e:
    print(f"❌ ERROR saat menjalankan fuzzy_logic: {e}")
    print("   Menggunakan data statis yang diekstrak dari output yang diharapkan.")
    SKFUZZY_AVAILABLE = False

# ====================================
# ⭐ EDIT KONFIGURASI DI SINI ⭐
# ====================================

CONFIG = {
    'n_samples': 100,           # Jumlah data yang di-generate
    'random_seed': 42,          # Seed untuk reproducibility (ganti angka untuk hasil berbeda)
    'output_dir': 'random_results',
    
    # Distribusi data (dalam persen)
    'distribution': {
        'screentime': {
            'low': 0.30,        # 30% screen time rendah (0-4 jam)
            'medium': 0.40,     # 40% screen time sedang (4-8 jam)
            'high': 0.30        # 30% screen time tinggi (8-12 jam)
        },
        'temperature': {
            'comfortable': 0.60,  # 60% suhu nyaman (20-28°C)
            'extreme': 0.40       # 40% suhu ekstrim (10-40°C)
        }
    }
}

# ====================================
# RANDOM DATA GENERATION
# ====================================

def generate_random_dataset(n_samples):
    """Generate dataset dengan distribusi realistis"""
    
    np.random.seed(CONFIG['random_seed'])
    random.seed(CONFIG['random_seed'])
    
    print(f"\n📊 Generating {n_samples} random samples...")
    
    data = []
    dist = CONFIG['distribution']
    
    for i in range(n_samples):
        # Distribusi realistis untuk screen time
        rand_val = random.random()
        if rand_val < dist['screentime']['low']:
            screentime = np.random.uniform(0, 4)  # Low
        elif rand_val < dist['screentime']['low'] + dist['screentime']['medium']:
            screentime = np.random.uniform(4, 8)  # Medium
        else:
            screentime = np.random.uniform(8, 12) # High
        
        # Distribusi suhu
        if random.random() < dist['temperature']['comfortable']:
            temperature = np.random.uniform(20, 28)  # Comfortable
        else:
            temperature = np.random.uniform(10, 40)  # Extreme
        
        # Humidity random
        humidity = np.random.uniform(0, 100)
        
        # Air quality dalam range 0-5 PPM
        air_quality = round(random.uniform(0.0, 5.0), 2)
        
        # Hitung stress
        result = fuzzy_logic.calculate_stress(screentime, temperature, humidity, air_quality)
        
        # Generate description
        time_desc = "Morning" if i % 4 == 0 else "Afternoon" if i % 4 == 1 else "Evening" if i % 4 == 2 else "Night"
        activity = random.choice(["Work", "Study", "Gaming", "Browsing", "Social Media", "Video"])
        
        data.append({
            'sample_id': i + 1,
            'screentime': round(screentime, 2),
            'temperature': round(temperature, 2),
            'humidity': round(humidity, 2),
            'air_quality': round(air_quality, 2),
            'stress_value': result['stress_value'],
            'category': result['category'],
            'description': f"{time_desc} - {activity}"
        })
        
        # Progress indicator
        if (i + 1) % 50 == 0 or (i + 1) == n_samples:
            print(f"   Generated {i + 1}/{n_samples} samples...")
    
    df = pd.DataFrame(data)
    print(f"✅ Dataset generated: {len(df)} samples\n")
    return df


# ====================================
# STATISTICS & METRICS
# ====================================

def calculate_statistics(df):
    """Calculate comprehensive statistics"""
    
    stats = {
        'total_samples': len(df),
        'mean_stress': df['stress_value'].mean(),
        'std_stress': df['stress_value'].std(),
        'min_stress': df['stress_value'].min(),
        'max_stress': df['stress_value'].max(),
        'median_stress': df['stress_value'].median(),
        'q1_stress': df['stress_value'].quantile(0.25),
        'q3_stress': df['stress_value'].quantile(0.75),
    }
    
    # Category distribution
    cat_dist = df['category'].value_counts()
    stats['category_distribution'] = {
        'Rendah': cat_dist.get('Rendah', 0),
        'Sedang': cat_dist.get('Sedang', 0),
        'Tinggi': cat_dist.get('Tinggi', 0)
    }
    
    # Correlation
    numeric_cols = ['screentime', 'temperature', 'humidity', 'air_quality', 'stress_value']
    stats['correlations'] = df[numeric_cols].corr()['stress_value'].to_dict()
    
    return stats


def print_statistics(stats):
    """Print statistics summary"""
    
    print("📈 DATASET STATISTICS:")
    print("=" * 70)
    print(f"Total Samples    : {stats['total_samples']}")
    print(f"Mean Stress      : {stats['mean_stress']:.2f}")
    print(f"Median Stress    : {stats['median_stress']:.2f}")
    print(f"Std Deviation    : {stats['std_stress']:.2f}")
    print(f"Min Stress       : {stats['min_stress']:.2f}")
    print(f"Max Stress       : {stats['max_stress']:.2f}")
    print(f"Q1 (25%)         : {stats['q1_stress']:.2f}")
    print(f"Q3 (75%)         : {stats['q3_stress']:.2f}")
    
    print("\n📊 CATEGORY DISTRIBUTION:")
    print("=" * 70)
    for cat, count in stats['category_distribution'].items():
        pct = (count / stats['total_samples']) * 100
        bar = "█" * int(pct / 2)
        print(f"{cat:8s}: {count:4d} ({pct:5.1f}%) {bar}")
    
    print("\n🔗 CORRELATION WITH STRESS:")
    print("=" * 70)
    for var, corr in stats['correlations'].items():
        if var != 'stress_value':
            strength = "Strong" if abs(corr) >= 0.7 else "Moderate" if abs(corr) >= 0.4 else "Weak"
            print(f"{var:15s}: {corr:+.4f} ({strength})")
    print()


# ====================================
# VISUALIZATIONS
# ====================================

def create_visualizations(df, output_dir):
    """Create all visualization plots"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Set style
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set_palette("husl")
    
    print("🎨 Creating Visualizations...\n")
    
    # ========================================
    # 1. MAIN DASHBOARD (2x3 grid)
    # ========================================
    fig1, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig1.suptitle(f'Random Test Data Analysis - Fuzzy Logic Stress Detection ({len(df)} samples)', 
                  fontsize=16, fontweight='bold')
    
    # 1.1 Stress Value Distribution
    axes[0, 0].hist(df['stress_value'], bins=20, color='skyblue', 
                    edgecolor='black', alpha=0.7)
    axes[0, 0].axvline(df['stress_value'].mean(), color='red', 
                       linestyle='--', linewidth=2, 
                       label=f'Mean: {df["stress_value"].mean():.1f}')
    axes[0, 0].axvline(df['stress_value'].median(), color='green', 
                       linestyle='--', linewidth=2, 
                       label=f'Median: {df["stress_value"].median():.1f}')
    axes[0, 0].set_title('Distribution of Stress Values', fontweight='bold')
    axes[0, 0].set_xlabel('Stress Value')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].legend()
    axes[0, 0].grid(alpha=0.3)
    
    # 1.2 Category Distribution (Bar Chart with %)
    cat_counts = df['category'].value_counts()
    colors = {'Rendah': '#90EE90', 'Sedang': '#FFD700', 'Tinggi': '#FF6B6B'}
    bars = axes[0, 1].bar(cat_counts.index, cat_counts.values,
                          color=[colors.get(cat, 'gray') for cat in cat_counts.index],
                          edgecolor='black', linewidth=1.5)
    axes[0, 1].set_title('Category Distribution', fontweight='bold')
    axes[0, 1].set_xlabel('Stress Category')
    axes[0, 1].set_ylabel('Count')
    
    # Add percentage labels
    for bar, count in zip(bars, cat_counts.values):
        height = bar.get_height()
        pct = (count / len(df)) * 100
        axes[0, 1].text(bar.get_x() + bar.get_width()/2., height,
                        f'{count}\n({pct:.1f}%)',
                        ha='center', va='bottom', fontweight='bold')
    axes[0, 1].grid(axis='y', alpha=0.3)
    
    # 1.3 Screen Time vs Stress
    scatter1 = axes[0, 2].scatter(df['screentime'], df['stress_value'], 
                                  c=df['stress_value'], cmap='RdYlGn_r', 
                                  s=50, alpha=0.6, edgecolors='black', linewidth=0.5)
    axes[0, 2].set_title('Screen Time vs Stress', fontweight='bold')
    axes[0, 2].set_xlabel('Screen Time (hours)')
    axes[0, 2].set_ylabel('Stress Value')
    plt.colorbar(scatter1, ax=axes[0, 2], label='Stress')
    axes[0, 2].grid(alpha=0.3)
    
    # 1.4 Temperature vs Stress
    scatter2 = axes[1, 0].scatter(df['temperature'], df['stress_value'], 
                                  c=df['stress_value'], cmap='RdYlGn_r', 
                                  s=50, alpha=0.6, edgecolors='black', linewidth=0.5)
    axes[1, 0].set_title('Temperature vs Stress', fontweight='bold')
    axes[1, 0].set_xlabel('Temperature (°C)')
    axes[1, 0].set_ylabel('Stress Value')
    plt.colorbar(scatter2, ax=axes[1, 0], label='Stress')
    axes[1, 0].grid(alpha=0.3)
    
    # 1.5 Humidity vs Stress
    scatter3 = axes[1, 1].scatter(df['humidity'], df['stress_value'], 
                                  c=df['stress_value'], cmap='RdYlGn_r', 
                                  s=50, alpha=0.6, edgecolors='black', linewidth=0.5)
    axes[1, 1].set_title('Humidity vs Stress', fontweight='bold')
    axes[1, 1].set_xlabel('Humidity (%)')
    axes[1, 1].set_ylabel('Stress Value')
    plt.colorbar(scatter3, ax=axes[1, 1], label='Stress')
    axes[1, 1].grid(alpha=0.3)
    
    # 1.6 Air Quality vs Stress
    scatter4 = axes[1, 2].scatter(df['air_quality'], df['stress_value'], 
                                  c=df['stress_value'], cmap='RdYlGn_r', 
                                  s=50, alpha=0.6, edgecolors='black', linewidth=0.5)
    axes[1, 2].set_title('Air Quality vs Stress', fontweight='bold')
    axes[1, 2].set_xlabel('Air Quality (PPM)')
    axes[1, 2].set_ylabel('Stress Value')
    plt.colorbar(scatter4, ax=axes[1, 2], label='Stress')
    axes[1, 2].grid(alpha=0.3)
    
    plt.tight_layout()
    fig1.savefig(f'{output_dir}/01_main_dashboard.png', dpi=300, bbox_inches='tight')
    print("✅ [1/5] Main Dashboard (2x3 grid)")
    plt.close(fig1)
    
    # ========================================
    # 2. CORRELATION HEATMAP
    # ========================================
    fig2, ax = plt.subplots(figsize=(10, 8))
    numeric_cols = ['screentime', 'temperature', 'humidity', 'air_quality', 'stress_value']
    corr_matrix = df[numeric_cols].corr()
    
    sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='coolwarm',
                center=0, square=True, linewidths=2, cbar_kws={"shrink": 0.8},
                vmin=-1, vmax=1, ax=ax)
    ax.set_title('Correlation Matrix - Input Variables vs Stress', 
                 fontsize=14, fontweight='bold', pad=20)
    
    fig2.tight_layout()
    fig2.savefig(f'{output_dir}/02_correlation_heatmap.png', dpi=300, bbox_inches='tight')
    print("✅ [2/5] Correlation Heatmap")
    plt.close(fig2)
    
    # ========================================
    # 3. BOX PLOTS BY CATEGORY
    # ========================================
    fig3, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig3.suptitle('Input Variables Distribution by Stress Category', 
                  fontsize=14, fontweight='bold')
    
    for idx, var in enumerate(['screentime', 'temperature', 'air_quality']):
        df.boxplot(column=var, by='category', ax=axes[idx], 
                   patch_artist=True, grid=True)
        axes[idx].set_title(f'{var.capitalize()} by Category')
        axes[idx].set_xlabel('Stress Category')
        axes[idx].set_ylabel(var.capitalize())
        plt.sca(axes[idx])
        plt.xticks(rotation=0)
    
    plt.tight_layout()
    fig3.savefig(f'{output_dir}/03_boxplots_by_category.png', dpi=300, bbox_inches='tight')
    print("✅ [3/5] Box Plots by Category")
    plt.close(fig3)
    
    # ========================================
    # 4. SAMPLE DATA TABLE (first 20 rows)
    # ========================================
    fig4, ax = plt.subplots(figsize=(16, 12))
    ax.axis('tight')
    ax.axis('off')
    
    # Take first 20 samples
    df_sample = df.head(20)
    
    table_data = []
    for _, row in df_sample.iterrows():
        # Color marker
        if row['category'] == 'Rendah':
            marker = '[L]'
        elif row['category'] == 'Sedang':
            marker = '[M]'
        else:
            marker = '[H]'
        
        table_data.append([
            row['sample_id'],
            f"{row['screentime']:.1f}h",
            f"{row['temperature']:.1f}°C",
            f"{row['humidity']:.0f}%",
            f"{row['air_quality']:.2f}",
            f"{row['stress_value']:.1f}",
            f"{marker} {row['category']}",
            row['description']
        ])
    
    table = ax.table(cellText=table_data,
                     colLabels=['ID', 'Screen', 'Temp', 'Humid', 'AQ(PPM)', 
                               'Stress', 'Category', 'Description'],
                     cellLoc='center',
                     loc='center',
                     colWidths=[0.05, 0.08, 0.08, 0.08, 0.08, 0.08, 0.12, 0.43])
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.5)
    
    # Color code stress values
    for i in range(len(table_data)):
        stress_val = df_sample.iloc[i]['stress_value']
        if stress_val < 35:
            table[(i+1, 5)].set_facecolor('#90EE90')
        elif stress_val < 65:
            table[(i+1, 5)].set_facecolor('#FFD700')
        else:
            table[(i+1, 5)].set_facecolor('#FF6B6B')
    
    plt.title(f'Sample Data Table (First 20 of {len(df)} samples)', 
              fontsize=14, fontweight='bold', pad=20)
    
    plt.savefig(f'{output_dir}/04_sample_table.png', dpi=300, bbox_inches='tight')
    print("✅ [4/5] Sample Data Table")
    plt.close(fig4)
    
    # ========================================
    # 5. STRESS DISTRIBUTION ANALYSIS
    # ========================================
    fig5, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig5.suptitle('Stress Value Analysis', fontsize=14, fontweight='bold')
    
    # 5.1 Violin plot by category
    parts = axes[0, 0].violinplot([df[df['category']=='Rendah']['stress_value'],
                                    df[df['category']=='Sedang']['stress_value'],
                                    df[df['category']=='Tinggi']['stress_value']],
                                   positions=[1, 2, 3], showmeans=True, showmedians=True)
    axes[0, 0].set_xticks([1, 2, 3])
    axes[0, 0].set_xticklabels(['Rendah', 'Sedang', 'Tinggi'])
    axes[0, 0].set_ylabel('Stress Value')
    axes[0, 0].set_title('Violin Plot by Category')
    axes[0, 0].grid(alpha=0.3)
    
    # 5.2 Cumulative distribution
    sorted_stress = np.sort(df['stress_value'])
    cumulative = np.arange(1, len(sorted_stress) + 1) / len(sorted_stress) * 100
    axes[0, 1].plot(sorted_stress, cumulative, linewidth=2, color='purple')
    axes[0, 1].set_xlabel('Stress Value')
    axes[0, 1].set_ylabel('Cumulative Percentage (%)')
    axes[0, 1].set_title('Cumulative Distribution Function')
    axes[0, 1].grid(alpha=0.3)
    
    # 5.3 KDE plot
    for cat in ['Rendah', 'Sedang', 'Tinggi']:
        df_cat = df[df['category'] == cat]
        if len(df_cat) > 0:
            df_cat['stress_value'].plot(kind='density', ax=axes[1, 0], 
                                         label=cat, linewidth=2)
    axes[1, 0].set_xlabel('Stress Value')
    axes[1, 0].set_ylabel('Density')
    axes[1, 0].set_title('Kernel Density Estimation by Category')
    axes[1, 0].legend()
    axes[1, 0].grid(alpha=0.3)
    
    # 5.4 Scatter: All variables combined
    # Create combined score for x-axis
    df['combined_input'] = (df['screentime']/12 + df['temperature']/40 + 
                           df['humidity']/100 + df['air_quality']/5) / 4 * 100
    axes[1, 1].scatter(df['combined_input'], df['stress_value'], 
                      c=df['stress_value'], cmap='RdYlGn_r', 
                      s=50, alpha=0.6, edgecolors='black', linewidth=0.5)
    axes[1, 1].set_xlabel('Combined Input Score (normalized)')
    axes[1, 1].set_ylabel('Stress Value')
    axes[1, 1].set_title('Combined Input vs Stress')
    axes[1, 1].grid(alpha=0.3)
    
    plt.tight_layout()
    fig5.savefig(f'{output_dir}/05_stress_analysis.png', dpi=300, bbox_inches='tight')
    print("✅ [5/5] Stress Distribution Analysis")
    plt.close(fig5)
    
    print(f"\n✅ All visualizations saved to: {output_dir}/\n")


# ====================================
# EXPORT FUNCTIONS
# ====================================

def export_results(df, stats, output_dir):
    """Export results to CSV and TXT"""
    
    # CSV export
    df.to_csv(f'{output_dir}/random_test_data.csv', index=False)
    print(f"✅ Exported: random_test_data.csv ({len(df)} rows)")
    
    # Detailed report
    with open(f'{output_dir}/analysis_report.txt', 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("RANDOM TEST DATA ANALYSIS - FUZZY LOGIC STRESS DETECTION\n")
        f.write("="*70 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Random Seed: {CONFIG['random_seed']}\n")
        f.write(f"Total Samples: {stats['total_samples']}\n\n")
        
        f.write("STRESS STATISTICS:\n")
        f.write("-" * 70 + "\n")
        f.write(f"Mean         : {stats['mean_stress']:.2f}\n")
        f.write(f"Median       : {stats['median_stress']:.2f}\n")
        f.write(f"Std Dev      : {stats['std_stress']:.2f}\n")
        f.write(f"Min          : {stats['min_stress']:.2f}\n")
        f.write(f"Max          : {stats['max_stress']:.2f}\n")
        f.write(f"Q1 (25%)     : {stats['q1_stress']:.2f}\n")
        f.write(f"Q3 (75%)     : {stats['q3_stress']:.2f}\n")
        f.write(f"IQR          : {stats['q3_stress'] - stats['q1_stress']:.2f}\n\n")
        
        f.write("CATEGORY DISTRIBUTION:\n")
        f.write("-" * 70 + "\n")
        for cat, count in stats['category_distribution'].items():
            pct = (count / stats['total_samples']) * 100
            f.write(f"{cat:8s}: {count:4d} samples ({pct:5.1f}%)\n")
        
        f.write("\nCORRELATION WITH STRESS:\n")
        f.write("-" * 70 + "\n")
        for var, corr in stats['correlations'].items():
            if var != 'stress_value':
                strength = "Strong" if abs(corr) >= 0.7 else "Moderate" if abs(corr) >= 0.4 else "Weak"
                f.write(f"{var:15s}: {corr:+.4f} ({strength})\n")
        
        f.write("\nINPUT VARIABLE STATISTICS:\n")
        f.write("-" * 70 + "\n")
        for col in ['screentime', 'temperature', 'humidity', 'air_quality']:
            f.write(f"\n{col.upper()}:\n")
            f.write(f"  Mean   : {df[col].mean():.2f}\n")
            f.write(f"  Median : {df[col].median():.2f}\n")
            f.write(f"  Std    : {df[col].std():.2f}\n")
            f.write(f"  Range  : {df[col].min():.2f} - {df[col].max():.2f}\n")
    
    print(f"✅ Exported: analysis_report.txt\n")


# ====================================
# MAIN
# ====================================

def main():
    print("\n" + "="*70)
    print(" RANDOM TEST DATA GENERATOR - FUZZY LOGIC STRESS DETECTION")
    print("="*70)
    print(f" Configuration:")
    print(f"   - Samples: {CONFIG['n_samples']}")
    print(f"   - Random Seed: {CONFIG['random_seed']}")
    print(f"   - Output Dir: {CONFIG['output_dir']}/")
    print("="*70)
    
    # Generate random dataset
    df = generate_random_dataset(CONFIG['n_samples'])
    
    # Calculate statistics
    stats = calculate_statistics(df)
    
    # Print statistics
    print_statistics(stats)
    
    # Create visualizations
    create_visualizations(df, CONFIG['output_dir'])
    
    # Export results
    export_results(df, stats, CONFIG['output_dir'])
    
    print("="*70)
    print("✅ ALL DONE!")
    print("="*70)
    print(f"\n📂 Check folder: {CONFIG['output_dir']}/")
    print("   - 01_main_dashboard.png (2x3 comprehensive view)")
    print("   - 02_correlation_heatmap.png (variable correlations)")
    print("   - 03_boxplots_by_category.png (distribution by category)")
    print("   - 04_sample_table.png (first 20 samples)")
    print("   - 05_stress_analysis.png (advanced analysis)")
    print("   - random_test_data.csv (full dataset)")
    print("   - analysis_report.txt (detailed statistics)")
    print("\n💡 Tips:")
    print("   - Change 'random_seed' in CONFIG for different results")
    print("   - Increase 'n_samples' for larger dataset")
    print("   - Adjust 'distribution' percentages for different scenarios")


if __name__ == '__main__':
    main()