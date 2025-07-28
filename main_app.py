import streamlit as st

# Debug info (optional)
print("st module:", st)
print("st.__file__:", st.__file__)
print("streamlit version:", st.__version__)

# Set page config
st.set_page_config(page_title="Sistem UMKM", layout="wide")

# Hide sidebar navigation if needed
no_sidebar_style = """
    <style>
        div[data-testid="stSidebarNav"] {display: none;}
    </style>
"""
st.markdown(no_sidebar_style, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/9/97/Logo_BRI.png", width=200)
    selected = st.radio(
        "Navigasi",
        options=["Beranda", "Data Entry", "Dashboard"],
        index=0,
        format_func=lambda x: f"📌 {x}" if x == "Beranda" else ("📊 " + x if x == "Dashboard" else "📝 " + x)
    )

# Content based on selected menu
if selected == "Beranda":
    st.markdown("<h1 style='text-align: center; color: #000000; font-weight: 900;'>Aplikasi Pendataan Kredit UMKM</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #0033EE; font-weight: 700;'>Bank Rakyat Indonesia (BRI)</h3>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("""
    <div style='text-align: justify; font-size:16px; padding: 0 50px;'>
        👋 <b>Selamat datang!</b><br><br>
        Aplikasi ini membantu dalam <b>pendataan, monitoring, dan analisis data kredit UMKM</b> secara efisien.
        Anda dapat mengelola informasi UMKM yang mengajukan pinjaman, memantau perkembangan keuangan usaha,
        serta menghasilkan insight untuk mendukung pertumbuhan UMKM di Indonesia.<br><br>
        Silakan gunakan menu navigasi di sebelah kiri untuk:
        <ul>
            <li>📥 <b>Data Entry</b>: Mengisi dan memperbarui data UMKM</li>
            <li>📊 <b>Dashboard</b>: Melihat grafik visualisasi data UMKM</li>
        </ul>
        Bersama BRI, mari kita dukung UMKM Indonesia tumbuh dan berkembang! 💪
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ")
    st.image("image_gambar.png", use_container_width=True)

elif selected == "Dashboard":
    st.switch_page("pages/dashboard_kur.py")

elif selected == "Data Entry":
    st.switch_page("pages/entry_mapping.py")
