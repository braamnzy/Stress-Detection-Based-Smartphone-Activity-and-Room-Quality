"""
CUSTOM TEST CASE GENERATOR FOR FUZZY LOGIC STRESS DETECTION
============================================================
VERSION 2.0 - Support data yang sudah ada fuzzy_level

FEATURES:
- Auto-detect: Gunakan fuzzy_level dari CSV jika ada
- Fallback: Hitung ulang jika kolom tidak ada
- Support format waktu Indonesia
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import re

try:
    import fuzzy_logic
    print("✅ Modul 'fuzzy_logic' berhasil diimpor.")
    SKFUZZY_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Module 'fuzzy_logic' tidak tersedia")
    SKFUZZY_AVAILABLE = False
except Exception as e:
    print(f"⚠️  Error pada fuzzy_logic: {e}")
    SKFUZZY_AVAILABLE = False


# ====================================
# PATH CSV
# ====================================
YOUR_CSV_FILE = 'data/dataset_overall.csv'


# ====================================
# HELPER FUNCTIONS
# ====================================
def parse_time_indonesian(time_str):
    """Konversi format waktu Indonesia ke jam (float)"""
    if pd.isna(time_str):
        return np.nan
    
    time_str = str(time_str).strip()
    
    # Coba parse sebagai angka langsung
    try:
        return float(time_str)
    except ValueError:
        pass
    
    # Parse format Indonesia
    hours = 0
    minutes = 0
    seconds = 0
    
    jam_match = re.search(r'(\d+)\s*jam', time_str, re.IGNORECASE)
    if jam_match:
        hours = int(jam_match.group(1))
    
    menit_match = re.search(r'(\d+)\s*menit', time_str, re.IGNORECASE)
    if menit_match:
        minutes = int(menit_match.group(1))
    
    detik_match = re.search(r'(\d+)\s*detik', time_str, re.IGNORECASE)
    if detik_match:
        seconds = int(detik_match.group(1))
    
    total_hours = hours + (minutes / 60) + (seconds / 3600)
    return round(total_hours, 3)


def category_to_stress(category):
    """Konversi kategori ke stress value (estimasi)"""
    mapping = {
        'Rendah': 25.0,
        'Sedang': 50.0,
        'Tinggi': 80.0,
        'Low': 25.0,
        'Medium': 50.0,
        'High': 80.0
    }
    return mapping.get(category, 50.0)


# ====================================
# GENERATE DATASET
# ====================================
def generate_from_csv(csv_file):
    """Load test cases from CSV with smart detection"""
    try:
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"File tidak ditemukan: {csv_file}")
        
        df_input = pd.read_csv(csv_file)
        print(f"✅ Berhasil membaca CSV: {len(df_input)} baris")
        print(f"📋 Kolom yang tersedia: {list(df_input.columns)}")
        
        # Deteksi kolom waktu
        if 'total_usage_time' in df_input.columns:
            time_col = 'total_usage_time'
        elif 'screentime' in df_input.columns:
            time_col = 'screentime'
        else:
            raise ValueError("Kolom waktu tidak ditemukan")
        
        # ⭐ CEK: Apakah sudah ada fuzzy_level di CSV?
        has_fuzzy_level = 'fuzzy_level' in df_input.columns
        
        if has_fuzzy_level:
            print(f"✅ Terdeteksi kolom 'fuzzy_level' - Akan menggunakan data yang sudah ada")
        else:
            print(f"⚠️  Kolom 'fuzzy_level' tidak ada - Akan menghitung dengan fuzzy_logic")
        
        print(f"✅ Menggunakan kolom waktu: '{time_col}'")
        
        # Validasi kolom yang diperlukan
        required_cols = [time_col, 'temperature', 'humidity', 'air_quality']
        missing_cols = [col for col in required_cols if col not in df_input.columns]
        if missing_cols:
            raise ValueError(f"Kolom yang hilang: {missing_cols}")
        
        # Konversi waktu dari format Indonesia
        print(f"\n🔄 Konversi format waktu...")
        df_input['screentime_hours'] = df_input[time_col].apply(parse_time_indonesian)
        print(f"   Range waktu: {df_input['screentime_hours'].min():.1f}h - {df_input['screentime_hours'].max():.1f}h")
        
        # Bersihkan data numerik lainnya
        numeric_cols = ['temperature', 'humidity', 'air_quality']
        for col in numeric_cols:
            if df_input[col].dtype == 'object':
                df_input[col] = df_input[col].astype(str).str.replace(',', '.')
            df_input[col] = pd.to_numeric(df_input[col], errors='coerce')
        
        # Hapus baris dengan nilai NaN
        rows_before = len(df_input)
        check_cols = ['screentime_hours'] + numeric_cols
        if has_fuzzy_level:
            check_cols.append('fuzzy_level')
        
        df_input.dropna(subset=check_cols, inplace=True)
        rows_after = len(df_input)
        
        if rows_before != rows_after:
            print(f"⚠️ Dihapus {rows_before - rows_after} baris dengan data tidak valid")
        
        if len(df_input) == 0:
            raise ValueError("Tidak ada data valid setelah pembersihan")
        
        print(f"✅ Data valid: {len(df_input)} baris")
        
        # Proses setiap baris
        data = []
        print(f"\n🧮 Memproses data...")
        
        for idx, row in df_input.iterrows():
            screen = row['screentime_hours']
            temp = row['temperature']
            humid = row['humidity']
            aq = row['air_quality']
            desc = row.get('message', row.get('description', f"Case ID: {idx + 1}"))
            
            # ⭐ LOGIC: Gunakan fuzzy_level dari CSV jika ada
            if has_fuzzy_level and pd.notna(row['fuzzy_level']):
                category = row['fuzzy_level']
                stress_val = category_to_stress(category)
                source = "CSV"
            else:
                # Hitung dengan fuzzy logic
                if SKFUZZY_AVAILABLE:
                    try:
                        result = fuzzy_logic.calculate_stress(screen, temp, humid, aq)
                        stress_val = result['stress_value']
                        category = result['category']
                        source = "Calculated"
                    except Exception as e:
                        print(f"⚠️ Error menghitung stress untuk baris {idx}: {e}")
                        stress_val = 50.0
                        category = "Sedang"
                        source = "Default"
                else:
                    # Fallback calculation
                    stress_val = min(100, max(0, (screen * 3) + (temp * 0.5) + (humid * 0.3) + (aq * 0.5)))
                    if stress_val < 35:
                        category = "Rendah"
                    elif stress_val < 65:
                        category = "Sedang"
                    else:
                        category = "Tinggi"
                    source = "Fallback"
            
            data.append({
                'id': len(data) + 1,
                'screentime': screen,
                'temperature': temp,
                'humidity': humid,
                'air_quality': aq,
                'stress_value': stress_val,
                'category': category,
                'description': desc,
                'source': source
            })
        
        df_result = pd.DataFrame(data)
        
        # Print summary
        print(f"\n✅ Berhasil memproses {len(data)} test cases")
        if has_fuzzy_level:
            print(f"   📊 Distribusi kategori dari CSV:")
            print(f"      {df_result['category'].value_counts().to_dict()}")
        
        return df_result
    
    except FileNotFoundError as e:
        print(f"❌ ERROR: {e}")
        print(f"   Path yang dicoba: {os.path.abspath(csv_file)}")
        return pd.DataFrame()
    except ValueError as e:
        print(f"❌ ERROR: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ ERROR tidak terduga: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()


# ====================================
# VISUALIZATION FUNCTIONS
# ====================================
def create_visualizations(df, output_dir='custom_results'):
    """Create all 5 visualization types"""
    
    if df.empty:
        print("❌ Tidak ada data untuk visualisasi.")
        return
    
    os.makedirs(output_dir, exist_ok=True)
    
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set_palette("husl")
    
    print("\n🎨 Creating Visualizations...\n")
    
    # ========================================
    # 1. MAIN DASHBOARD (2x3 grid)
    # ========================================
    fig1, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig1.suptitle('Custom Test Cases - Fuzzy Logic Analysis Dashboard', 
                  fontsize=16, fontweight='bold')
    
    # 1.1 Stress Value Distribution
    unique_values = df['stress_value'].nunique()
    stress_range = df['stress_value'].max() - df['stress_value'].min()
    
    if unique_values == 1 or stress_range < 0.1:
        stress_val = df['stress_value'].iloc[0]
        axes[0, 0].bar([stress_val], [len(df)], color='skyblue', edgecolor='black', alpha=0.7, width=5)
        axes[0, 0].set_xlim(max(0, stress_val - 10), min(100, stress_val + 10))
        axes[0, 0].axvline(stress_val, color='red', linestyle='--', linewidth=2, 
                          label=f'Value: {stress_val:.1f}')
        axes[0, 0].text(stress_val, len(df)/2, f'{len(df)} cases\n@ {stress_val:.1f}', 
                       ha='center', va='center', fontsize=12, fontweight='bold',
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    else:
        n_bins = min(max(3, unique_values), 10)
        axes[0, 0].hist(df['stress_value'], bins=n_bins, color='skyblue', edgecolor='black', alpha=0.7)
        axes[0, 0].axvline(df['stress_value'].mean(), color='red', 
                          linestyle='--', linewidth=2, 
                          label=f'Mean: {df["stress_value"].mean():.1f}')
    
    axes[0, 0].set_title('Distribution of Stress Values', fontweight='bold')
    axes[0, 0].set_xlabel('Stress Value')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].legend()
    axes[0, 0].grid(alpha=0.3)
    
    # 1.2 Category Distribution (Pie Chart)
    cat_counts = df['category'].value_counts()
    colors = {'Rendah': '#90EE90', 'Sedang': '#FFD700', 'Tinggi': '#FF6B6B',
              'Low': '#90EE90', 'Medium': '#FFD700', 'High': '#FF6B6B'}
    axes[0, 1].pie(cat_counts.values, labels=cat_counts.index, autopct='%1.1f%%',
                   colors=[colors.get(cat, 'gray') for cat in cat_counts.index],
                   startangle=90, textprops={'fontsize': 10, 'fontweight': 'bold'})
    axes[0, 1].set_title('Category Distribution', fontweight='bold')
    
    # 1.3 Screen Time vs Stress
    if df['stress_value'].nunique() > 1:
        scatter1 = axes[0, 2].scatter(df['screentime'], df['stress_value'], 
                                      c=df['stress_value'], cmap='RdYlGn_r', 
                                      s=100, alpha=0.7, edgecolors='black')
        plt.colorbar(scatter1, ax=axes[0, 2], label='Stress')
    else:
        axes[0, 2].scatter(df['screentime'], df['stress_value'], 
                          color='red', s=100, alpha=0.7, edgecolors='black',
                          label=f'Stress: {df["stress_value"].iloc[0]:.1f}')
        axes[0, 2].legend()
    
    axes[0, 2].set_title('App Usage Time vs Stress', fontweight='bold')
    axes[0, 2].set_xlabel('Total Usage Time (hours)')
    axes[0, 2].set_ylabel('Stress Value')
    axes[0, 2].grid(alpha=0.3)
    
    # 1.4 Temperature vs Stress
    if df['stress_value'].nunique() > 1:
        scatter2 = axes[1, 0].scatter(df['temperature'], df['stress_value'], 
                                      c=df['stress_value'], cmap='RdYlGn_r', 
                                      s=100, alpha=0.7, edgecolors='black')
        plt.colorbar(scatter2, ax=axes[1, 0], label='Stress')
    else:
        axes[1, 0].scatter(df['temperature'], df['stress_value'], 
                          color='red', s=100, alpha=0.7, edgecolors='black')
    
    axes[1, 0].set_title('Temperature vs Stress', fontweight='bold')
    axes[1, 0].set_xlabel('Temperature (°C)')
    axes[1, 0].set_ylabel('Stress Value')
    axes[1, 0].grid(alpha=0.3)
    
    # 1.5 Humidity vs Stress
    if df['stress_value'].nunique() > 1:
        scatter3 = axes[1, 1].scatter(df['humidity'], df['stress_value'], 
                                      c=df['stress_value'], cmap='RdYlGn_r', 
                                      s=100, alpha=0.7, edgecolors='black')
        plt.colorbar(scatter3, ax=axes[1, 1], label='Stress')
    else:
        axes[1, 1].scatter(df['humidity'], df['stress_value'], 
                          color='red', s=100, alpha=0.7, edgecolors='black')
    
    axes[1, 1].set_title('Humidity vs Stress', fontweight='bold')
    axes[1, 1].set_xlabel('Humidity (%)')
    axes[1, 1].set_ylabel('Stress Value')
    axes[1, 1].grid(alpha=0.3)
    
    # 1.6 Air Quality vs Stress
    if df['stress_value'].nunique() > 1:
        scatter4 = axes[1, 2].scatter(df['air_quality'], df['stress_value'], 
                                      c=df['stress_value'], cmap='RdYlGn_r', 
                                      s=100, alpha=0.7, edgecolors='black')
        plt.colorbar(scatter4, ax=axes[1, 2], label='Stress')
    else:
        axes[1, 2].scatter(df['air_quality'], df['stress_value'], 
                          color='red', s=100, alpha=0.7, edgecolors='black')
    
    axes[1, 2].set_title('Air Quality vs Stress', fontweight='bold')
    axes[1, 2].set_xlabel('Air Quality (PPM)')
    axes[1, 2].set_ylabel('Stress Value')
    axes[1, 2].grid(alpha=0.3)
    
    plt.tight_layout()
    fig1.savefig(f'{output_dir}/01_main_dashboard.png', dpi=300, bbox_inches='tight')
    print("✅ [1/5] Main Dashboard")
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
    ax.set_title('Correlation Matrix - Variables vs Stress', 
                 fontsize=14, fontweight='bold', pad=20)
    
    fig2.tight_layout()
    fig2.savefig(f'{output_dir}/02_correlation_heatmap.png', dpi=300, bbox_inches='tight')
    print("✅ [2/5] Correlation Heatmap")
    plt.close(fig2)
    
    # ========================================
    # 3. BOX PLOTS BY CATEGORY
    # ========================================
    if df['category'].nunique() > 1:
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
    else:
        print("⏭️  [3/5] Box Plots skipped (only 1 category)")
    
    # ========================================
    # 4. VALIDATION TABLE
    # ========================================
    fig4, ax = plt.subplots(figsize=(16, len(df)*0.5 + 2))
    ax.axis('tight')
    ax.axis('off')
    
    table_data = []
    for _, row in df.iterrows():
        if row['category'] in ['Rendah', 'Low']:
            emoji = '🟢'
        elif row['category'] in ['Sedang', 'Medium']:
            emoji = '🟡'
        else:
            emoji = '🔴'
        
        table_data.append([
            row['id'],
            f"{row['screentime']:.1f}h",
            f"{row['temperature']:.1f}°C",
            f"{row['humidity']:.0f}%",
            f"{row['air_quality']:.2f}",
            f"{row['stress_value']:.1f}",
            f"{emoji} {row['category']}",
            row['description']
        ])
    
    table = ax.table(cellText=table_data,
                     colLabels=['ID', 'Screen', 'Temp', 'Humid', 'AQ', 
                               'Stress', 'Category', 'Description'],
                     cellLoc='center',
                     loc='center',
                     colWidths=[0.05, 0.08, 0.08, 0.08, 0.08, 0.08, 0.12, 0.43])
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2.5)
    
    # Color code
    for i in range(len(table_data)):
        stress_val = df.iloc[i]['stress_value']
        if stress_val < 35:
            table[(i+1, 5)].set_facecolor('#90EE90')
        elif stress_val < 65:
            table[(i+1, 5)].set_facecolor('#FFD700')
        else:
            table[(i+1, 5)].set_facecolor('#FF6B6B')
    
    plt.title(f'Test Cases Results Table ({len(df)} cases)', 
              fontsize=14, fontweight='bold', pad=20)
    
    plt.savefig(f'{output_dir}/04_validation_table.png', dpi=300, bbox_inches='tight')
    print("✅ [4/5] Validation Table")
    plt.close(fig4)
    
    # ========================================
    # 5. LINE PLOT PROGRESSION
    # ========================================
    fig5, ax = plt.subplots(figsize=(14, 6))
    
    df_sorted = df.sort_values('stress_value').reset_index(drop=True)
    
    ax.plot(range(len(df_sorted)), df_sorted['stress_value'], 
            marker='o', linewidth=2, markersize=8, color='purple',
            label='Stress Value')
    
    ax.axhline(y=35, color='green', linestyle=':', linewidth=2, 
               label='Low/Medium Boundary')
    ax.axhline(y=65, color='red', linestyle=':', linewidth=2, 
               label='Medium/High Boundary')
    
    ax.fill_between(range(len(df_sorted)), 0, 35, alpha=0.2, color='green')
    ax.fill_between(range(len(df_sorted)), 35, 65, alpha=0.2, color='yellow')
    ax.fill_between(range(len(df_sorted)), 65, 100, alpha=0.2, color='red')
    
    for i, row in df_sorted.iterrows():
        ax.text(i, row['stress_value'] + 3, f"{row['stress_value']:.1f}", 
                ha='center', fontsize=7, bbox=dict(facecolor='white', 
                alpha=0.7, boxstyle='round,pad=0.3'))
    
    ax.set_title('Stress Value Progression (Sorted)', 
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Test Case Index (sorted by stress)')
    ax.set_ylabel('Stress Value (0-100)')
    ax.set_ylim(-5, 105)
    ax.legend(loc='upper left')
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    fig5.savefig(f'{output_dir}/05_line_plot_progression.png', dpi=300, bbox_inches='tight')
    print("✅ [5/5] Line Plot Progression")
    plt.close(fig5)
    
    print(f"\n✅ All visualizations saved to: {output_dir}/\n")


# ====================================
# EXPORT FUNCTIONS
# ====================================
def export_results(df, output_dir='custom_results'):
    """Export results to CSV and TXT"""
    
    if df.empty:
        return
    
    df.to_csv(f'{output_dir}/test_results.csv', index=False)
    print(f"✅ Exported: test_results.csv")
    
    with open(f'{output_dir}/summary_report.txt', 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("CUSTOM TEST CASES - FUZZY LOGIC STRESS DETECTION\n")
        f.write("="*70 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Test Cases: {len(df)}\n\n")
        
        f.write("STRESS STATISTICS:\n")
        f.write("-" * 70 + "\n")
        f.write(f"Mean      : {df['stress_value'].mean():.2f}\n")
        f.write(f"Median    : {df['stress_value'].median():.2f}\n")
        f.write(f"Std Dev   : {df['stress_value'].std():.2f}\n")
        f.write(f"Min       : {df['stress_value'].min():.2f}\n")
        f.write(f"Max       : {df['stress_value'].max():.2f}\n\n")
        
        f.write("CATEGORY DISTRIBUTION:\n")
        f.write("-" * 70 + "\n")
        cat_dist = df['category'].value_counts()
        for cat, count in cat_dist.items():
            pct = (count / len(df)) * 100
            f.write(f"{cat:8s}: {count:3d} cases ({pct:5.1f}%)\n")
        
        f.write("\nCORRELATION WITH STRESS:\n")
        f.write("-" * 70 + "\n")
        corr = df[['screentime', 'temperature', 'humidity', 'air_quality', 'stress_value']].corr()
        for var in ['screentime', 'temperature', 'humidity', 'air_quality']:
            f.write(f"{var:15s}: {corr.loc[var, 'stress_value']:+.4f}\n")
    
    print(f"✅ Exported: summary_report.txt\n")


# ====================================
# MAIN
# ====================================
def main():
    print("\n" + "="*70)
    print(" CUSTOM TEST CASE GENERATOR - FUZZY LOGIC STRESS DETECTION")
    print(" VERSION 2.0 - Smart Detection")
    print("="*70)
    print(f" CSV File: {YOUR_CSV_FILE}")
    print("="*70 + "\n")
    
    df_results = generate_from_csv(YOUR_CSV_FILE)
    
    if not df_results.empty:
        print(f"\n📊 Dataset Summary:")
        print(f"   Total Cases: {len(df_results)}")
        print(f"   Stress Range: {df_results['stress_value'].min():.1f} - {df_results['stress_value'].max():.1f}")
        print(f"   Unique Stress Values: {df_results['stress_value'].nunique()}")
        print(f"   Categories: {df_results['category'].value_counts().to_dict()}")
        
        output_dir = 'custom_results'
        create_visualizations(df_results, output_dir)
        export_results(df_results, output_dir)
        
        print("\n" + "="*70)
        print("🎉 SELESAI! Cek folder 'custom_results' untuk hasil visualisasi")
        print("="*70)
    else:
        print("\n🛑 Tidak dapat memproses data.")


if __name__ == "__main__":
    main()