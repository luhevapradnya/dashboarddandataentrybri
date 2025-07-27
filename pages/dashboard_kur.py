import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from streamlit_option_menu import option_menu
from datetime import datetime

st.set_page_config(page_title="Dashboard Kredit Nasabah UMKM BRI Regional Office Denpasar", layout="wide")

no_sidebar_style = """
    <style>
        div[data-testid="stSidebarNav"] {display: none;}
    </style>
"""
st.markdown(no_sidebar_style, unsafe_allow_html=True)

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/9/97/Logo_BRI.png", width=200)
    selected = option_menu(
        menu_title="Navigasi",
        options=["Beranda", "Data Entry", "Dashboard"],
        icons=["house", "pencil-square", "bar-chart"],
        menu_icon="cast",
        default_index=2
    )

if selected == "Beranda":
    st.switch_page("main_app.py")
elif selected == "Data Entry":
    st.switch_page("pages/entry_mapping.py")

# Fungsi load data
def load_data():
    if os.path.exists("umkm_data.xlsx"):
        return pd.read_excel("umkm_data.xlsx")
    else:
        st.error("Data UMKM belum tersedia. Silakan tambahkan data terlebih dahulu.")
        return pd.DataFrame()

data = load_data()



st.markdown("<h2>📊 Dashboard Kinerja Kredit UMKM BRI Regional Office Denpasar (KCP TELESERA)</h2>", unsafe_allow_html=True)



# Sidebar Filter
st.sidebar.header("🔍 Filter dan Pencarian")
# Dapatkan daftar unik dari masing-masing kolom
wilayah_list = sorted(data["Wilayah"].dropna().unique()) if "Wilayah" in data.columns else []
kategori_list = sorted(data["Kategori"].dropna().unique()) if "Kategori" in data.columns else []
status_list = sorted(data["Status"].dropna().unique()) if "Status" in data.columns else []
tahun_list = sorted(data["Tahun"].dropna().unique()) if "Tahun" in data.columns else []
bulan_list = sorted(data["Bulan"].dropna().unique()) if "Bulan" in data.columns else []

# Komponen sidebar
selected_kategori = st.sidebar.multiselect("Pilih Kategori", kategori_list)
selected_tahun = st.sidebar.multiselect("Pilih Tahun", tahun_list)
selected_bulan = st.sidebar.multiselect("Pilih Bulan", bulan_list)
cari_nama_usaha = st.sidebar.multiselect("Cari Nama Usaha", options=data["Nama Usaha"].unique())
cari_nama_nasabah = st.sidebar.text_input("Cari Nama Nasabah")

# --- Filter Data ---
filtered_data = data.copy()

# Peta nama bulan Indonesia ke Inggris
bulan_mapping = {
    "Januari": "January", "Februari": "February", "Maret": "March", "April": "April",
    "Mei": "May", "Juni": "June", "Juli": "July", "Agustus": "August",
    "September": "September", "Oktober": "October", "November": "November", "Desember": "December"
}

# Ganti nama bulan
filtered_data["Bulan_English"] = filtered_data["Bulan"].replace(bulan_mapping)
filtered_data["Tanggal Mulai"] = pd.to_datetime(
    filtered_data["Tahun"].astype(str) + "-" + filtered_data["Bulan_English"] + "-01", errors="coerce"
)


# Hitung ulang Bulan Berjalan dan Sisa Waktu Bayar
bulan_saat_ini = datetime.today().year * 12 + datetime.today().month
bulan_mulai = filtered_data["Tanggal Mulai"].dt.year * 12 + filtered_data["Tanggal Mulai"].dt.month
filtered_data["Bulan Berjalan"] = bulan_saat_ini - bulan_mulai
filtered_data["Bulan Dibayar Realistis"] = filtered_data[["Bulan Berjalan", "Jangka Waktu Peminjaman (Bulan)"]].min(axis=1)


filtered_data["Sisa Waktu Bayar (bulan)"] = (
    filtered_data["Jangka Waktu Peminjaman (Bulan)"] - filtered_data["Bulan Berjalan"]
).clip(lower=0)


# Hitung ulang Sisa Hutang
filtered_data["Sisa Hutang (Rp)"] = filtered_data["Angsuran"] * filtered_data["Sisa Waktu Bayar (bulan)"]
filtered_data["Jumlah yang Sudah Dibayar (Rp)"] = filtered_data["Angsuran"] * filtered_data["Bulan Dibayar Realistis"]
filtered_data["Status Pembayaran"] = filtered_data["Sisa Waktu Bayar (bulan)"].apply(
    lambda x: "Lunas" if x == 0 else "Belum Lunas"
)

if selected_kategori:
    filtered_data = filtered_data[filtered_data["Kategori"].isin(selected_kategori)]


if selected_tahun:
    filtered_data = filtered_data[filtered_data["Tahun"].isin(selected_tahun)]

if selected_bulan:
    filtered_data = filtered_data[filtered_data["Bulan"].isin(selected_bulan)]

if cari_nama_usaha:
    filtered_data = filtered_data[filtered_data["Nama Usaha"].str.contains('|'.join(cari_nama_usaha), case=False, na=False)]

if cari_nama_nasabah:
    filtered_data = filtered_data[filtered_data["Nama Nasabah"].str.contains(cari_nama_nasabah, case=False, na=False)]

from dateutil.relativedelta import relativedelta

import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import streamlit as st

# 1. Mapping nama bulan ke angka
bulan_mapping = {
    "Januari": 1, "Februari": 2, "Maret": 3, "April": 4,
    "Mei": 5, "Juni": 6, "Juli": 7, "Agustus": 8,
    "September": 9, "Oktober": 10, "November": 11, "Desember": 12
}

# Pastikan `filtered_data` sudah ada sebelumnya
# Misalnya: filtered_data = data.copy() + filter user

# 2. Tambahkan kolom 'Tanggal Mulai'
filtered_data["Bulan_English"] = filtered_data["Bulan"].replace(bulan_mapping)
filtered_data["Tanggal Mulai"] = pd.to_datetime(
    filtered_data["Tahun"].astype(str) + "-" + filtered_data["Bulan_English"].astype(str) + "-01", errors="coerce"
)

# 3. Ambil tahun & bulan yang difilter
tahun_terfilter = filtered_data["Tahun"].unique()
bulan_terfilter = filtered_data["Bulan"].unique()

tahun_dipilih = tahun_terfilter[0] if len(tahun_terfilter) == 1 else None
bulan_dipilih = bulan_mapping.get(bulan_terfilter[0]) if len(bulan_terfilter) == 1 else None

# 4. Fungsi menghitung sisa hutang aktif dari tahun/bulan tertentu
def sisa_hutang_mulai_dari(row, tahun_target=None, bulan_target=None):
    try:
        mulai = row["Tanggal Mulai"]
        durasi = int(row["Jangka Waktu Peminjaman (Bulan)"])
        angsuran = row["Angsuran"]

        # Validasi
        if pd.isnull(mulai) or pd.isnull(angsuran) or angsuran == 0 or durasi == 0:
            return 0

        selesai = mulai + relativedelta(months=durasi)

        # Tentukan patokan waktu
        if tahun_target and bulan_target:
            patokan = datetime(tahun_target, bulan_target, 1)
        elif tahun_target:
            patokan = datetime(tahun_target, 1, 1)
        else:
            patokan = datetime.today()

        # Jika pinjaman sudah lunas sebelum patokan, tidak dihitung
        if selesai < patokan:
            return 0

        total = 0
        for i in range(durasi):
            t_angsur = mulai + relativedelta(months=i)
            if t_angsur >= patokan:
                total += angsuran

        return total
    except Exception as e:
        return 0

# 5. Hitung dari FILTERED DATA
# 5. Gunakan kolom Sisa Hutang (Rp) yang sudah dihitung sebelumnya di tabel
total_sisa_hutang = filtered_data["Sisa Hutang (Rp)"].sum()

# 6. Tampilkan ke Dashboard
col1, col2, col3 = st.columns(3)

with col1:
    st.info("📌 Total Usaha")
    total_usaha = len(filtered_data)
    st.metric(label="Total Usaha", value=f"{total_usaha:,}", border=True)

with col2:
    st.info("📌 Total Kredit")
    total_kredit = filtered_data["Jumlah Ajuan Kredit (Rp)"].sum() if "Jumlah Ajuan Kredit (Rp)" in filtered_data.columns else 0
    
    # Format: Rp 1.000.000 (pakai titik)
    formatted_kredit = f"Rp {total_kredit:,.0f}".replace(",", ".")
    
    st.metric(label="Total Ajuan Kredit", value=formatted_kredit, border=True)

label_hutang = "Total Piutang"
if tahun_dipilih and bulan_dipilih:
    label_hutang += f" {bulan_terfilter[0]} {tahun_dipilih}"
elif tahun_dipilih:
    label_hutang += f" {tahun_dipilih}"
elif bulan_dipilih:
    label_hutang += f" Bulan {bulan_terfilter[0]}"

with col3:
    st.info("📌 Total Piutang")
    formatted_piutang = f"Rp {total_sisa_hutang:,.0f}".replace(",", ".")
    st.metric(label=label_hutang, value=formatted_piutang, border=True)






# Hitung tanggal mulai pinjaman
# Pemetaan bulan Indonesia ke Inggris
bulan_mapping = {
    "Januari": "January", "Februari": "February", "Maret": "March", "April": "April",
    "Mei": "May", "Juni": "June", "Juli": "July", "Agustus": "August",
    "September": "September", "Oktober": "October", "November": "November", "Desember": "December"
}

data["Bulan"] = data["Bulan"].replace(bulan_mapping)
data["Tanggal Mulai"] = pd.to_datetime(data["Tahun"].astype(str) + "-" + data["Bulan"] + "-01", errors="coerce")

# Hitung jumlah bulan yang sudah berjalan
bulan_saat_ini = datetime.today().year * 12 + datetime.today().month
bulan_mulai = data["Tanggal Mulai"].dt.year * 12 + data["Tanggal Mulai"].dt.month
data["Bulan Berjalan"] = bulan_saat_ini - bulan_mulai
# Batasi bulan berjalan agar tidak melebihi jangka waktu pinjaman
data["Bulan Dibayar Realistis"] = data[["Bulan Berjalan", "Jangka Waktu Peminjaman (Bulan)"]].min(axis=1)


# Hitung sisa waktu bayar (jangan sampai negatif)
data["Sisa Waktu Bayar (bulan)"] = (data["Jangka Waktu Peminjaman (Bulan)"] - data["Bulan Berjalan"]).clip(lower=0)
data["Status Pembayaran"] = data["Sisa Waktu Bayar (bulan)"].apply(
    lambda x: "✅ Lunas" if x == 0 else "❌ Belum Lunas"
)
# Hitung sisa hutang berdasarkan angsuran bulanan
data["Sisa Hutang (Rp)"] = data["Angsuran"] * data["Sisa Waktu Bayar (bulan)"]
data["Jumlah yang Sudah Dibayar (Rp)"] = data["Angsuran"] * data["Bulan Dibayar Realistis"]


# Buat tabel ringkas dari filtered_data
tabel_nasabah = filtered_data[[
    "Nama Nasabah", "Nama Usaha", 
    "Jumlah yang Sudah Dibayar (Rp)", 
    "Sisa Hutang (Rp)", 
    "Sisa Waktu Bayar (bulan)",
    "Status Pembayaran"
]].copy()


# Pastikan tipe data numerik untuk formatting
tabel_nasabah["Sisa Hutang (Rp)"] = tabel_nasabah["Sisa Hutang (Rp)"].astype(int)
tabel_nasabah["Jumlah yang Sudah Dibayar (Rp)"] = tabel_nasabah["Jumlah yang Sudah Dibayar (Rp)"].astype(int)
tabel_nasabah["Sisa Waktu Bayar (bulan)"] = tabel_nasabah["Sisa Waktu Bayar (bulan)"].astype(int)


# Urutkan berdasarkan sisa hutang dan waktu bayar
tabel_nasabah = tabel_nasabah.sort_values(
    by=["Sisa Hutang (Rp)", "Sisa Waktu Bayar (bulan)"], ascending=[True, True]
)

# Format angka jadi lebih rapi dengan tanda ribuan
# Ganti koma jadi titik
tabel_nasabah["Sisa Hutang (Rp)"] = tabel_nasabah["Sisa Hutang (Rp)"].map("{:,}".format).str.replace(",", ".", regex=False)
tabel_nasabah["Jumlah yang Sudah Dibayar (Rp)"] = tabel_nasabah["Jumlah yang Sudah Dibayar (Rp)"].map("{:,}".format).str.replace(",", ".", regex=False)

# Tampilkan tabel di Streamlit
with st.container(border=True, height=490):
    st.markdown("#### 💳 Rekapitulasi Pembayaran Pinjaman Nasabah")
    
    st.dataframe(
    tabel_nasabah[[
        "Nama Usaha", "Nama Nasabah", 
        "Jumlah yang Sudah Dibayar (Rp)", "Sisa Hutang (Rp)", 
        "Sisa Waktu Bayar (bulan)", "Status Pembayaran"
    ]],
    use_container_width=True,
    hide_index=True,
    height=420
    )



row_1_col_1, row_1_col_2 = st.columns(2)
with row_1_col_1:
    with st.container(border=True, height=490):
        # Pastikan mapping bulan dalam Bahasa Indonesia ke angka
        bulan_mapping = {
            "Januari": "01", "Februari": "02", "Maret": "03", "April": "04",
            "Mei": "05", "Juni": "06", "Juli": "07", "Agustus": "08",
            "September": "09", "Oktober": "10", "November": "11", "Desember": "12"
        }

        # Gabungkan tahun dan bulan menjadi satu kolom tanggal mulai
        filtered_data["Tanggal Mulai"] = pd.to_datetime(
            filtered_data["Tahun"].astype(str) + "-" + 
            filtered_data["Bulan"].map(bulan_mapping),
            format="%Y-%m", errors='coerce'
        )

        # Hitung sisa waktu bayar
        today = pd.to_datetime("today")
        filtered_data["Sisa Waktu Bayar (bulan)"] = (
            filtered_data["Jangka Waktu Peminjaman (Bulan)"] -
            ((today.year - filtered_data["Tanggal Mulai"].dt.year) * 12 +
            (today.month - filtered_data["Tanggal Mulai"].dt.month))
        ).clip(lower=0)


        # Buat kolom status pelunasan
        filtered_data["Status Pelunasan"] = filtered_data["Sisa Waktu Bayar (bulan)"].apply(
            lambda x: "Lunas" if x == 0 else "Belum Lunas"
        )

        # Hitung jumlah tiap status
        pelunasan_counts = filtered_data["Status Pelunasan"].value_counts().reset_index()
        pelunasan_counts.columns = ["Status", "Jumlah"]

        # Pie chart
        fig_pie = px.pie(
            pelunasan_counts,
            names="Status",
            values="Jumlah",
            color="Status",
            color_discrete_map={"Lunas": "green", "Belum Lunas": "orange"},
            title="Distribusi Status Pelunasan Kredit",
            hole=0.4
        )
        fig_pie.update_traces(textinfo="percent+label")
        st.plotly_chart(fig_pie, use_container_width=True)

import plotly.graph_objects as go

with row_1_col_2:
    with st.container(border=True, height=490):
        # Hitung total plafon per kategori
        pengajuan_kredit = filtered_data.groupby("Kategori")["Jumlah Ajuan Kredit (Rp)"].sum().reset_index()

        # Format label lengkap dengan titik
        pengajuan_kredit["Label Kredit"] = pengajuan_kredit["Jumlah Ajuan Kredit (Rp)"].apply(lambda x: f"{x:,.0f}".replace(",", "."))

        # Urutkan
        pengajuan_kredit = pengajuan_kredit.sort_values(by="Jumlah Ajuan Kredit (Rp)", ascending=False)

        # Tentukan nilai maksimum untuk membuat sumbu Y yang sesuai
        y_max = pengajuan_kredit["Jumlah Ajuan Kredit (Rp)"].max()
        interval = 5_000_000_000  # Tiap 5 M
        tickvals = list(range(0, int(y_max) + interval, interval))
        ticktext = [f"{int(val/1_000_000_000)} M" for val in tickvals]

        # Buat bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=pengajuan_kredit["Kategori"],
                y=pengajuan_kredit["Jumlah Ajuan Kredit (Rp)"],
                text=pengajuan_kredit["Label Kredit"],
                textposition="outside",
                marker_color='royalblue'
            )
        ])

        # Layout dengan sumbu Y pakai satuan M
        fig.update_layout(
            title="Total Pengajuan Kredit per Kategori Usaha",
            yaxis=dict(
                title="Jumlah Ajuan Kredit (Rp)",
                tickvals=tickvals,
                ticktext=ticktext
            ),
            xaxis=dict(
                title="Kategori Usaha",
                tickangle=-15
            ),
            margin=dict(t=40, b=80),
            height=440
        )
        fig.update_traces(
        textfont=dict(
        family="Trebuchet MS",
        size=11,
        color="black"
        )
    )

        st.plotly_chart(fig, use_container_width=True)

row_2_col_1, row_2_col_2 = st.columns(2)

with row_2_col_2:
    with st.container(border=True, height=490):
        ########Distribusi UMKM berdasarkan Kategori Usaha######
        # Hitung jumlah UMKM per kategori usaha
        kategori_counts = filtered_data["Kategori"].value_counts().reset_index()
        kategori_counts.columns = ["Kategori", "Jumlah UMKM"]

        # Buat pie chart
        fig = px.pie(kategori_counts,
                    names="Kategori",
                    values="Jumlah UMKM",
                    title="Distribusi UMKM per Kategori Usaha",
                    hole=0.4)  # Untuk donat chart, hapus jika mau pie biasa

        fig.update_traces(textinfo='percent+label')

        # Tampilkan chart
        st.plotly_chart(fig, use_container_width=True)

with row_2_col_1:
    with st.container(border=True, height=490):
        ############ Distribusi UMKM Berdasarkan Status Tempat Usaha ############

        # Hitung jumlah UMKM berdasarkan Status Tempat Usaha
        status_df = filtered_data["Status Tempat Usaha"].value_counts().reset_index()
        status_df.columns = ["Status Tempat Usaha", "Jumlah"]

        # Buat bar chart
        fig = px.bar(
            status_df,
            x="Status Tempat Usaha",
            y="Jumlah",
            color="Status Tempat Usaha",
            text="Jumlah",
            title="Distribusi Status Tempat Usaha"
        )

        fig.update_traces(
            texttemplate='%{text:,.0f}',
            textposition='outside',
            textfont=dict(family="Trebuchet MS", size=11, color="black")
        )

        fig.update_layout(
            bargap=0.2,
            xaxis_title="Status Tempat Usaha",
            yaxis_title="Jumlah UMKM",
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)


row_3_col_1, row_3_col_2 = st.columns(2)

with row_3_col_1:
    with st.container(border=True, height=490):
        ############ Sebaran Wilayah UMKM per Kecamatan (filtered) ############
        sebaran_kecamatan = filtered_data["Kecamatan"].value_counts().reset_index()
        sebaran_kecamatan.columns = ["Kecamatan", "Jumlah UMKM"]

        fig = px.bar(
            sebaran_kecamatan, x="Kecamatan", y="Jumlah UMKM",
            title="Sebaran UMKM per Kecamatan",
            labels={"Jumlah UMKM": "Jumlah UMKM", "Kecamatan": "Kecamatan"},
            text="Jumlah UMKM"
        )
        fig.update_traces(
            texttemplate='%{text:,.0f}',
            textposition='outside',
            textfont=dict(family="Trebuchet MS", size=11, color="black")
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

with row_3_col_2:
    with st.container(border=True, height=490):
        ############ Rata-rata Omzet vs Laba Bersih per Kategori Usaha ############

        # Salin data
        omzet_laba = filtered_data.copy()

        # Ambil kolom-kolom omzet dan laba bersih
        omzet_cols = [col for col in omzet_laba.columns if "Omzet" in col]
        laba_cols = [col for col in omzet_laba.columns if "Laba Bersih" in col]

        # Hitung total omzet dan laba bersih per baris (usaha)
        omzet_laba["Total Omzet"] = omzet_laba[omzet_cols].sum(axis=1)
        omzet_laba["Total Laba Bersih"] = omzet_laba[laba_cols].sum(axis=1)

        # Hitung rata-rata omzet dan laba per kategori
        rata2 = omzet_laba.groupby("Kategori")[["Total Omzet", "Total Laba Bersih"]].mean().reset_index()

        # Ubah ke format long (melt) agar bisa bar grouped
        df_melted = rata2.melt(id_vars="Kategori",
                               value_vars=["Total Omzet", "Total Laba Bersih"],
                               var_name="Tipe", value_name="Jumlah")

        # Buat bar chart
        fig = px.bar(
            df_melted,
            x="Kategori",
            y="Jumlah",
            color="Tipe",
            barmode="group",
            text_auto=".2s",
            title="Perbandingan Rata-rata Omzet dan Laba Bersih per Kategori Usaha"
        )

        fig.update_layout(
            xaxis_title=None,
            yaxis_title="Jumlah Rata-rata (Rp)",
            legend_title_text="",
            xaxis_tickangle=-45,
            uniformtext_minsize=8
        )

        st.plotly_chart(fig, use_container_width=True)


# --- Tampilkan Data yang Sudah Difilter (opsional) ---
st.subheader(f"📄 Data Terfilter: {len(filtered_data)} baris")
