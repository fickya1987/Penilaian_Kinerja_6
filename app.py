import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import skew, norm
import numpy as np

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("Penilaian_Kinerja.csv")

df = load_data()

st.title("Distribusi dan Perbandingan Skor KPI Pegawai")

# Pilih NIPP siapa pun (bisa atasan atau bawahan)
all_nipps = df['NIPP_Pekerja'].dropna().unique()
selected_nipp = st.selectbox("Pilih NIPP Pegawai untuk Dilihat Posisi Skornya:", sorted(all_nipps))

# Ambil skor dan semua data yang valid
df_valid = df[['NIPP_Pekerja', 'Skor_KPI_Final']].dropna()
df_sorted = df_valid.sort_values(by='Skor_KPI_Final', ascending=True).reset_index(drop=True)
df_sorted['Posisi'] = range(1, len(df_sorted) + 1)

# Ambil skor NIPP terpilih
def plot_distribution(df_sorted, selected_nipp, title):
    selected_row = df_sorted[df_sorted['NIPP_Pekerja'] == selected_nipp]
    if selected_row.empty:
        st.warning("NIPP tidak ditemukan dalam data skor KPI.")
        return

    selected_score = selected_row.iloc[0]['Skor_KPI_Final']
    selected_rank = selected_row.index[0] + 1

    mean_score = df_sorted['Skor_KPI_Final'].mean()
    std_score = df_sorted['Skor_KPI_Final'].std()

    fig, ax = plt.subplots(figsize=(14, 6))

    bar_colors = ['skyblue' if nipp != selected_nipp else 'orange' for nipp in df_sorted['NIPP_Pekerja']]
    ax.bar(df_sorted['Posisi'], df_sorted['Skor_KPI_Final'], color=bar_colors, label='Skor KPI Pegawai')

    ax.axhline(mean_score, color='blue', linestyle='--', label=f'Rata-rata: {mean_score:.2f}')
    ax.axhline(selected_score, color='orange', linestyle='--', label=f'Skor NIPP {selected_nipp}: {selected_score:.2f}')
    ax.set_xticks([])
    ax.set_ylabel("Skor KPI")
    ax.set_ylim(90, 112)
    ax.set_title(title)

    x = np.linspace(0, len(df_sorted), 500)
    y = norm.pdf(x, loc=len(df_sorted)/2, scale=len(df_sorted)/8)
    y_scaled = (y / y.max()) * (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.3 + ax.get_ylim()[0]
    ax.plot(x, y_scaled, color='red', label='Kurva Normal (Visualisasi)', linewidth=2)

    ax.legend()
    st.pyplot(fig)

    st.markdown(f"**Skor Pegawai (NIPP {selected_nipp})**: {selected_score:.2f}")
    st.markdown(f"**Peringkat dari seluruh pegawai**: {selected_rank} dari {len(df_sorted)}")
    st.markdown(f"**Rata-rata seluruh skor KPI**: {mean_score:.2f}")
    st.markdown(f"**Skewness distribusi**: {skew(df_sorted['Skor_KPI_Final']):.2f}")

# Plot global distribution
plot_distribution(df_sorted, selected_nipp, "Distribusi Seluruh Pegawai")

# Plot local distribution (bawahan dari atasan yang sama)
selected_atasan = df[df['NIPP_Pekerja'] == selected_nipp]['NIPP_Atasan'].values[0] if selected_nipp in df['NIPP_Pekerja'].values else None
if selected_atasan:
    local_df = df[df['NIPP_Atasan'] == selected_atasan][['NIPP_Pekerja', 'Skor_KPI_Final']].dropna()
    if not local_df.empty:
        local_sorted = local_df.sort_values(by='Skor_KPI_Final', ascending=True).reset_index(drop=True)
        local_sorted['Posisi'] = range(1, len(local_sorted) + 1)
        plot_distribution(local_sorted, selected_nipp, f"Distribusi Pegawai di Bawah Atasan NIPP {selected_atasan}")
