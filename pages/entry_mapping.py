import streamlit as st
import pandas as pd
import os
from streamlit_option_menu import option_menu
# Load or initialize UMKM data

# Fungsi untuk load data dari file CSV

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
        default_index=1
    )

if selected == "Beranda":
    st.switch_page("main_app.py")
elif selected == "Dashboard":
    st.switch_page("pages/dashboard_kur.py")

def load_data():
    if os.path.exists("umkm_data.xlsx"):
        return pd.read_excel("umkm_data.xlsx")
    else:
        return pd.DataFrame(columns=[
            "Tahun","Bulan","ID", "Nama Usaha", "Nama Nasabah", "Kategori", "Alamat", "Kelurahan", "Kecamatan",
            "Alamat Pemilik (KTP)", "Wilayah", "No Telepon",
            *[f"Omzet {bulan} (Rp)" for bulan in bulan_list],
            *[f"Laba Bersih {bulan} (Rp)" for bulan in bulan_list],
            "Lama Usaha (Tahun)", "Jumlah Ajuan Kredit (Rp)","Angsuran per Bulan", "Jangka Waktu Peminjaman (Bulan)", "Riwayat Pinjaman",
            "Status Tempat Usaha", "Status"
        ])

def save_data(df):
    df.to_excel("umkm_data.xlsx", index=False)

# Fungsi untuk simpan data ke file CSV
def load_data():
    if os.path.exists("umkm_data.xlsx"):
        return pd.read_excel("umkm_data.xlsx")
    
# Inisialisasi data di session_state
if "umkm_data" not in st.session_state:
    st.session_state.umkm_data = load_data()
    st.session_state.umkm_data.rename(columns={
        "Jangka Waktu Peminjaman": "Jangka Waktu Peminjaman (Bulan)"
    }, inplace=True)

data = st.session_state.umkm_data.copy()
def format_rupiah(x):
    try:
        return "{:,}".format(int(x)).replace(",", ".")
    except:
        return x  # kalau string, abaikan

for col in data.columns:
    if "Rp" in col or "Angsuran" in col or "Kredit" in col:
        data[col] = data[col].apply(format_rupiah)

# Bulan-bulan untuk Omzet dan Laba
bulan_list = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
              "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

# Inisialisasi data di session_state
if "umkm_data" not in st.session_state:
    st.session_state.umkm_data = load_data()
if "history" not in st.session_state:
    st.session_state.history = []

# ========================
# SIDEBAR INPUT DATA UMKM
# ========================
with st.sidebar:
    st.header("📥 Tambah Data UMKM")
    tahun = st.text_input("Tahun")
    bulan = st.text_input("Bulan")
    nama_usaha = st.text_input("Nama Usaha")
    nama_nasabah = st.text_input("Nama Nasabah")
    kategori_umkm = st.selectbox("Kategori", [
        "Kuliner", "Fashion", "Jasa", "Perdagangan"
    ])
    alamat = st.text_input("Alamat Usaha")
    kelurahan = st.text_input("Kelurahan")
    kecamatan = st.text_input("Kecamatan")
    alamat_ktp = st.text_input("Alamat Pemilik (KTP)")
    wilayah = st.text_input("Wilayah (Kabupaten)")
    no_telepon = st.text_input("No Telepon", max_chars=15).strip()

    st.markdown("#### 📈 Omzet & Laba Bersih per Bulan")
    omzet_values = {}
    laba_values = {}
    for bulan in bulan_list:
        col1, col2 = st.columns(2)
        with col1:
            omzet_values[f"Omzet {bulan} (Rp)"] = st.number_input(f"Omzet {bulan}", min_value=0, step=1000, key=f"omzet_{bulan}")
        with col2:
            laba_values[f"Laba Bersih {bulan} (Rp)"] = st.number_input(f"Laba {bulan}", min_value=0, step=1000, key=f"laba_{bulan}")

    lama_usaha = st.number_input("Lama Usaha (Tahun)", min_value=0.0, format="%.1f")
    jumlah_kredit = st.number_input("Jumlah Ajuan Kredit (Rp)", min_value=0, step=100000)
    angsuran = st.number_input("Angsuran per Bulan", min_value=0, step=100000)
    jangka_waktu = st.number_input("Jangka Waktu Peminjaman (Bulan)", min_value=1)
    riwayat_pinjaman = st.selectbox("Riwayat Pinjaman", ["Tidak Pernah Gagal Bayar", "Pernah Gagal Bayar"])
    status_tempat_usaha = st.selectbox("Status Tempat Usaha", ["Milik Pribadi", "Kontrak Jangka Panjang", "Kontrak Jangka Pendek", "Lainnya"])

    if st.button("➕ Tambahkan UMKM", use_container_width=True):
        if nama_usaha:
            validasi_omzet = omzet_values.get("Omzet Januari (Rp)", 0)
            validasi_laba = laba_values.get("Laba Bersih Januari (Rp)", 0)

            status = "Approve" if (
                lama_usaha >= 0.5 and
                validasi_omzet >= 2_000_000 and
                validasi_laba >= 1_000_000 and
                riwayat_pinjaman == "Tidak Pernah Gagal Bayar" and
                status_tempat_usaha in ["Milik Pribadi", "Kontrak Jangka Panjang"]
            ) else "Reject"
            new_entry = pd.DataFrame([{
                "Tahun": tahun,
                "Bulan": bulan,
                "ID": len(st.session_state.umkm_data) + 1,
                "Nama Usaha": nama_usaha,
                "Nama Nasabah": nama_nasabah,
                "Kategori": kategori_umkm,
                "Alamat": alamat,
                "Kelurahan": kelurahan,
                "Kecamatan": kecamatan,
                "Alamat Pemilik (KTP)": alamat_ktp,
                "Wilayah": wilayah,
                "No Telepon": f"{no_telepon[:3]}-{no_telepon[3:6]}-{no_telepon[6:9]}-{no_telepon[9:]}",
                **{k: format_rupiah(v) for k, v in omzet_values.items()},
                **{k: format_rupiah(v) for k, v in laba_values.items()},
                "Lama Usaha (Tahun)": int(round(lama_usaha)),
                "Jumlah Ajuan Kredit (Rp)": format_rupiah(round(jumlah_kredit, -3)),
                "Jangka Waktu Peminjaman (Bulan)": int(jangka_waktu),
                "Angsuran per Bulan": format_rupiah(round(angsuran, -3)),
                "Riwayat Pinjaman": riwayat_pinjaman,
                "Status Tempat Usaha": status_tempat_usaha,
                "Status": status
            }])

            st.session_state.history.append(st.session_state.umkm_data.copy())
            st.session_state.umkm_data = pd.concat([st.session_state.umkm_data, new_entry], ignore_index=True)
            save_data(st.session_state.umkm_data)
            st.success("✅ UMKM berhasil ditambahkan!")
        else:
            st.error("⚠️ Harap isi Nama Usaha.")

    if st.button("↩️ Undo Perubahan Terakhir", use_container_width=True):
        if st.session_state.history:
            st.session_state.umkm_data = st.session_state.history.pop()
            save_data(st.session_state.umkm_data)
            st.success("🔄 Undo berhasil!")
        else:
            st.warning("⚠️ Tidak ada perubahan untuk di-undo.")

# ========================
# TAMPILAN FILTER DATA
# ========================
st.subheader("🔍 Filter Data UMKM")
data = st.session_state.umkm_data.copy()

col1, col2, col3, col4 = st.columns(4)

with col1:
    filter_kategori = st.selectbox("Filter Kategori", ["Semua"] + sorted(data["Kategori"].dropna().unique()))
with col2:
    filter_tempat = st.selectbox("Filter Status Tempat Usaha", ["Semua"] + sorted(data["Status Tempat Usaha"].dropna().unique()))
with col3:
    filter_tahun = st.selectbox("Filter Tahun",["Semua"] + sorted(map(str, data["Tahun"].dropna().unique())))
with col4:
    filter_bulan = st.selectbox("Filter Bulan", ["Semua"] + sorted(data["Bulan"].dropna().unique()))

# Terapkan filter
if filter_kategori != "Semua":
    data = data[data["Kategori"] == filter_kategori]
if filter_tempat != "Semua":
    data = data[data["Status Tempat Usaha"] == filter_tempat]
if filter_tahun != "Semua":
    data = data[data["Tahun"] == filter_tahun]
if filter_bulan != "Semua":
    data = data[data["Bulan"] == filter_bulan]


# Ganti status dengan ikon
def add_icon(status):
    return "✅ Approve" if status == "Approve" else "❌ Reject"
data["Status"] = data["Status"].apply(add_icon)

st.subheader("📊 Data UMKM")
st.markdown(f"Total data ditampilkan: **{len(data)}**")

def color_accepted(val):
    return 'color: green' if val == "✅ Approve" else 'color: red'

data_display = data.copy()
for col in data_display.columns:
    if "Rp" in col or "Angsuran" in col or "Kredit" in col or "Omzet" in col or "Laba" in col:
        data_display[col] = data_display[col].apply(format_rupiah)
st.dataframe(data_display, use_container_width=True, hide_index=True)

# ========================
# HAPUS DATA UMKM
# ========================
st.subheader("🗑️ Hapus Data UMKM")
if not data.empty:
    selected_ids = st.multiselect("Pilih ID UMKM yang Ingin Dihapus:", options=data["ID"].tolist())
    if st.button("❌ Hapus Baris Terpilih", use_container_width=True):
        if selected_ids:
            st.session_state.history.append(st.session_state.umkm_data.copy())
            st.session_state.umkm_data = st.session_state.umkm_data[~st.session_state.umkm_data["ID"].isin(selected_ids)].reset_index(drop=True)
            save_data(st.session_state.umkm_data)
            st.success(f"✅ Data dengan ID {', '.join(map(str, selected_ids))} berhasil dihapus!")
        else:
            st.warning("⚠️ Harap pilih minimal satu ID.")
else:
    st.info("ℹ️ Tidak ada data untuk dihapus.")

