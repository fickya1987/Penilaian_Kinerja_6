import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import skew, norm
import numpy as np

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("Penilaian_Kinerja_03.csv")

df = load_data()

st.title("Distribusi dan Perbandingan Skor KPI Pegawai")

# Tombol untuk reset cache dan refresh
if st.button("🔁 Clear Cache dan Refresh"):
    st.cache_data.clear()
    st.experimental_rerun()

# Pilih NIPP siapa pun (bisa atasan atau bawahan)
all_nipps = df['NIPP_Pekerja'].dropna().unique()
selected_nipp = st.selectbox("Pilih NIPP Pegawai untuk Dilihat Posisi Skornya:", sorted(all_nipps))

# Ambil skor dan semua data yang valid
df_valid = df[['NIPP_Pekerja', 'Skor_KPI_Final']].dropna()

# Fungsi visualisasi distribusi
def plot_distribution(df_source, selected_nipp, title):
    df_sorted = df_source.sort_values(by='Skor_KPI_Final', ascending=True).reset_index(drop=True)
    df_sorted['Posisi'] = range(1, len(df_sorted) + 1)  # Ranking: tertinggi = 1 di kanan

    selected_row = df_sorted[df_sorted['NIPP_Pekerja'] == selected_nipp]
    if selected_row.empty:
        st.warning(f"NIPP {selected_nipp} tidak ditemukan dalam {title.lower()}.")
        return

    selected_score = selected_row.iloc[0]['Skor_KPI_Final']
    selected_rank = len(df_sorted) - selected_row.index[0]

    mean_score = df_sorted['Skor_KPI_Final'].mean()
    std_score = df_sorted['Skor_KPI_Final'].std()
    skew_value = skew(df_sorted['Skor_KPI_Final'])

    fig, ax = plt.subplots(figsize=(14, 6))
    bar_colors = ['skyblue' if nipp != selected_nipp else 'orange' for nipp in df_sorted['NIPP_Pekerja']]
    ax.bar(df_sorted['Posisi'], df_sorted['Skor_KPI_Final'], color=bar_colors, label='Skor KPI Pegawai')
    # ax.invert_xaxis()  # Dihapus agar kurva normal tidak terbalik  # Ranking terbaik di sisi kanan

    ax.axhline(mean_score, color='blue', linestyle='--', label=f'Rata-rata: {mean_score:.2f}')
    ax.axhline(selected_score, color='orange', linestyle='--', label=f'Skor NIPP {selected_nipp}: {selected_score:.2f}')
    ax.set_xticks([])
    ax.set_ylabel("Skor KPI")
    ax.set_ylim(90, 112)
    ax.set_title(title)

    ax.legend()
    st.pyplot(fig)

    # Info tambahan dinamis
    st.markdown(f"**Skor Pegawai (NIPP {selected_nipp})**: {selected_score:.2f}")
    st.markdown(f"**Peringkat dalam {title.lower()}**: {selected_rank} dari {len(df_sorted)}")
    st.markdown(f"**Rata-rata skor KPI**: {mean_score:.2f}")
    st.markdown(f"**Skewness distribusi ({title})**: {skew_value:.2f}")
    st.write("Jumlah pegawai dalam distribusi ini:", len(df_sorted))
    st.write("Skewness real-time:", skew_value)

# Global distribution
plot_distribution(df_valid, selected_nipp, "Distribusi Seluruh Pegawai")

# Distribusi pegawai di bawah atasan yang sama
selected_atasan = df[df['NIPP_Pekerja'] == selected_nipp]['NIPP_Atasan'].values[0] if selected_nipp in df['NIPP_Pekerja'].values else None
if selected_atasan:
    local_df = df[df['NIPP_Atasan'] == selected_atasan][['NIPP_Pekerja', 'Skor_KPI_Final']].dropna()
    if not local_df.empty:
        plot_distribution(local_df, selected_nipp, f"Distribusi Pegawai di Bawah Atasan NIPP {selected_atasan}")
