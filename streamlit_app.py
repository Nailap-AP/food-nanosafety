import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(
    page_title="Food NanoSafety",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS kustom
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2c7873;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2c7873;
        margin-bottom: 1rem;
    }
    .risk-high { color: #e74c3c; font-weight: bold; }
    .risk-medium { color: #f39c12; font-weight: bold; }
    .risk-low { color: #27ae60; font-weight: bold; }
    .agency-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-right: 8px;
    }
    .bpom { background-color: #3498db; color: white; }
    .fda { background-color: #2ecc71; color: white; }
    .efsa { background-color: #9b59b6; color: white; }
    .fsanz { background-color: #e74c3c; color: white; }
</style>
""", unsafe_allow_html=True)

# Data dummy untuk aplikasi
REGULATIONS_DATA = [
    {
        "id": 1,
        "judul": "Regulasi Nanomaterial dalam Pangan Olahan",
        "lembaga": "BPOM",
        "deskripsi": "Peraturan BPOM tentang penggunaan nanomaterial dalam pangan olahan dengan batasan maksimal dan persyaratan pelabelan.",
        "status": "Disetujui",
        "tanggal": "2022-05-15",
        "link": "https://www.pom.go.id"
    },
    {
        "id": 2,
        "judul": "Guidance for Industry: Safety of Nanomaterials in Food",
        "lembaga": "FDA",
        "deskripsi": "Panduan FDA mengenai penilaian keamanan bahan nanomaterial yang digunakan dalam produk pangan.",
        "status": "Disetujui",
        "tanggal": "2021-11-10",
        "link": "https://www.fda.gov"
    },
    {
        "id": 3,
        "judul": "Nano-sized additives in food: risk assessment requirements",
        "lembaga": "EFSA",
        "deskripsi": "Persyaratan penilaian risiko untuk bahan tambahan pangan berukuran nano menurut otoritas keamanan pangan Eropa.",
        "status": "Dibatasi",
        "tanggal": "2023-02-28",
        "link": "https://www.efsa.europa.eu"
    },
    {
        "id": 4,
        "judul": "Nanotechnology in Food Products",
        "lembaga": "FSANZ",
        "deskripsi": "Kebijakan Food Standards Australia New Zealand mengenai penggunaan nanoteknologi dalam produk pangan.",
        "status": "Dalam Review",
        "tanggal": "2022-12-05",
        "link": "https://www.foodstandards.gov.au"
    }
]

TOXICITY_DATA = [
    {
        "nanopartikel": "Nano-SiO₂",
        "aplikasi_pangan": "Anti-caking agent",
        "metode_uji": "In vitro (sel Caco-2)",
        "hasil": "IC50 > 1000 μg/mL",
        "status_keamanan": "Aman",
        "referensi": "J. Food Sci. 2020, 85(3), 456-462"
    },
    {
        "nanopartikel": "TiO₂ (E171)",
        "aplikasi_pangan": "Food whitener",
        "metode_uji": "In vivo (tikus)",
        "hasil": "LD50 > 5000 mg/kg",
        "status_keamanan": "Hati-hati",
        "referensi": "Food Chem. Toxicol. 2019, 124, 123-130"
    },
    {
        "nanopartikel": "Nano-Ag",
        "aplikasi_pangan": "Antimicrobial packaging",
        "metode_uji": "In vitro (sel hati)",
        "hasil": "IC50 = 25 μg/mL",
        "status_keamanan": "Berisiko",
        "referensi": "Nanotoxicology, 2021, 15(2), 156-167"
    },
    {
        "nanopartikel": "Chitosan nanoparticles",
        "aplikasi_pangan": "Nutrient delivery",
        "metode_uji": "In vivo (tikus)",
        "hasil": "LD50 > 2000 mg/kg",
        "status_keamanan": "Aman",
        "referensi": "Int. J. Biol. Macromol. 2022, 194, 102-110"
    },
    {
        "nanopartikel": "ZnO nanoparticles",
        "aplikasi_pangan": "Fortification",
        "metode_uji": "In vitro (sel usus)",
        "hasil": "IC50 = 50 μg/mL",
        "status_keamanan": "Hati-hati",
        "referensi": "J. Agric. Food Chem. 2021, 69(12), 3456-3463"
    },
    {
        "nanopartikel": "Lipid nanoparticles",
        "aplikasi_pangan": "Omega-3 delivery",
        "metode_uji": "In vivo (tikus)",
        "hasil": "LD50 > 3000 mg/kg",
        "status_keamanan": "Aman",
        "referensi": "Food Funct. 2020, 11(4), 2893-2902"
    }
]

NEWS_DATA = [
    {
        "judul": "BPOM Evaluasi Regulasi Nanoteknologi Pangan 2023",
        "ringkasan": "Badan POM mengumumkan evaluasi regulasi penggunaan nanoteknologi dalam produk pangan untuk meningkatkan perlindungan konsumen.",
        "tanggal": "2023-06-10",
        "kategori": "Regulasi"
    },
    {
        "judul": "Studi Baru: Dampak Nanopartikel TiO₂ pada Mikrobioma Usus",
        "ringkasan": "Penelitian terbaru mengungkapkan efek nanopartikel titanium dioksida terhadap keseimbangan mikrobioma usus pada model hewan.",
        "tanggal": "2023-05-28",
        "kategori": "Riset"
    },
    {
        "judul": "EFSA Perbarui Panduan Keamanan Nanomaterial",
        "ringkasan": "Otoritas Keamanan Pangan Eropa memperbarui panduan penilaian risiko untuk nanomaterial dalam makanan dan kemasan pangan.",
        "tanggal": "2023-04-15",
        "kategori": "Regulasi"
    }
]

# Fungsi untuk menghitung risiko
def calculate_risk_score(answers):
    """Menghitung skor risiko berdasarkan jawaban"""
    score = 0
    for answer in answers:
        if answer == "Ya, lengkap":
            score += 3
        elif answer == "Terbatas":
            score += 2
        elif answer == "Tidak ada":
            score += 1
        elif answer == "Diatur ketat":
            score += 3
        elif answer == "Diatur umum":
            score += 2
        elif answer == "Tidak diatur":
            score += 1
        elif answer == "Tinggi":
            score += 1
        elif answer == "Sedang":
            score += 2
        elif answer == "Rendah":
            score += 3
        elif answer == "< 20 nm":
            score += 1
        elif answer == "20-100 nm":
            score += 2
        elif answer == "> 100 nm":
            score += 3
        elif answer == "Tinggi (> 1 mg/g)":
            score += 1
        elif answer == "Sedang (0.1-1 mg/g)":
            score += 2
        elif answer == "Rendah (< 0.1 mg/g)":
            score += 3
    
    return score

def main():
    # Header
    st.markdown('<h1 class="main-header">🍎 Food NanoSafety</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Database Regulasi & Keamanan Nanoteknologi Pangan</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://images.unsplash.com/photo-1592417817098-8fd3d9eb14a5?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80", 
                 caption="Nanoteknologi Pangan", use_column_width=True)
        
        st.markdown("### Navigasi")
        menu = st.radio(
            "Pilih Menu:",
            ["🏠 Dashboard", "📋 Database Regulasi", "🧪 Data Toksisitas", "⚠️ Risk Assessment", "📰 Berita Terkini"]
        )
        
        st.markdown("---")
        st.markdown("### Filter Data")
        agency_filter = st.multiselect(
            "Filter Lembaga:",
            ["BPOM", "FDA", "EFSA", "FSANZ"],
            default=["BPOM", "FDA", "EFSA", "FSANZ"]
        )
        
        st.markdown("---")
        st.markdown("### Informasi")
        st.info(
            "Aplikasi ini dikembangkan untuk mendukung pendidikan dan penelitian "
            "di bidang Nanoteknologi Pangan. Data hanya untuk tujuan edukasi."
        )
    
    # Konten utama berdasarkan menu
    if menu == "🏠 Dashboard":
        show_dashboard()
    elif menu == "📋 Database Regulasi":
        show_regulations(agency_filter)
    elif menu == "🧪 Data Toksisitas":
        show_toxicity()
    elif menu == "⚠️ Risk Assessment":
        show_risk_assessment()
    elif menu == "📰 Berita Terkini":
        show_news()

def show_dashboard():
    """Menampilkan dashboard utama"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Jumlah Regulasi", len(REGULATIONS_DATA))
    
    with col2:
        safe_count = len([d for d in TOXICITY_DATA if d["status_keamanan"] == "Aman"])
        st.metric("Nanopartikel Aman", f"{safe_count}/{len(TOXICITY_DATA)}")
    
    with col3:
        st.metric("Update Terbaru", "Jun 2023")
    
    st.markdown("---")
    
    # Grafik distribusi status keamanan
    st.subheader("Distribusi Status Keamanan Nanopartikel")
    df_toxicity = pd.DataFrame(TOXICITY_DATA)
    safety_counts = df_toxicity["status_keamanan"].value_counts()
    
    fig = px.pie(
        values=safety_counts.values,
        names=safety_counts.index,
        color=safety_counts.index,
        color_discrete_map={
            "Aman": "#27ae60",
            "Hati-hati": "#f39c12",
            "Berisiko": "#e74c3c"
        }
    )
    fig.update_layout(showlegend=True, height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Ringkasan aplikasi
    st.markdown("---")
    st.subheader("Tentang Food NanoSafety")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="card">
        <h4>🎯 Tujuan Aplikasi</h4>
        <p>Menyediakan database terpadu untuk regulasi, keamanan, dan aspek toksikologi 
        nanopartikel dalam pangan bagi mahasiswa dan peneliti nanoteknologi pangan.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
        <h4>📊 Cakupan Data</h4>
        <p>• Regulasi dari BPOM, FDA, EFSA, FSANZ</p>
        <p>• Data toksisitas 6 jenis nanopartikel</p>
        <p>• Alat penilaian risiko nanopartikel</p>
        <p>• Update berita terkini</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
        <h4>👥 Target Pengguna</h4>
        <p>• Mahasiswa S1-S3 Nanoteknologi Pangan</p>
        <p>• Peneliti dan akademisi</p>
        <p>• Industri pangan yang menggunakan nanoteknologi</p>
        <p>• Regulator dan policymaker</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
        <h4>⚠️ Disclaimer</h4>
        <p>Informasi dalam aplikasi ini hanya untuk tujuan pendidikan. 
        Selalu periksa sumber resmi untuk keputusan regulasi dan keamanan.</p>
        </div>
        """, unsafe_allow_html=True)

def show_regulations(agency_filter):
    """Menampilkan database regulasi"""
    st.subheader("📋 Database Regulasi Nanoteknologi Pangan")
    
    # Filter data berdasarkan pilihan di sidebar
    filtered_data = [r for r in REGULATIONS_DATA if r["lembaga"] in agency_filter]
    
    if not filtered_data:
        st.warning("Tidak ada data regulasi untuk lembaga yang dipilih.")
        return
    
    # Tampilkan data dalam dataframe
    df = pd.DataFrame(filtered_data)
    
    # Tambahkan kolom badge untuk lembaga
    def format_agency(agency):
        color_map = {
            "BPOM": "bpom",
            "FDA": "fda",
            "EFSA": "efsa",
            "FSANZ": "fsanz"
        }
        return f'<span class="agency-badge {color_map.get(agency, "")}">{agency}</span>'
    
    df["Lembaga"] = df["lembaga"].apply(format_agency)
    
    # Tampilkan tabel
    st.markdown(df[["Lembaga", "judul", "status", "tanggal"]].to_html(escape=False, index=False), unsafe_allow_html=True)
    
    # Detail untuk setiap regulasi
    st.markdown("---")
    st.subheader("Detail Regulasi")
    
    for reg in filtered_data:
        with st.expander(f"{reg['judul']} - {reg['lembaga']}"):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.metric("Status", reg["status"])
                st.metric("Tanggal", reg["tanggal"])
                st.metric("Lembaga", reg["lembaga"])
            
            with col2:
                st.write("**Deskripsi:**")
                st.info(reg["deskripsi"])
                
                if st.button(f"Buka Sumber {reg['lembaga']}", key=f"btn_{reg['id']}"):
                    st.markdown(f"[Kunjungi Situs Resmi {reg['lembaga']}]({reg['link']})")

def show_toxicity():
    """Menampilkan database toksisitas"""
    st.subheader("🧪 Database Toksisitas Nanopartikel")
    
    # Konversi ke dataframe
    df = pd.DataFrame(TOXICITY_DATA)
    
    # Filter
    col1, col2 = st.columns(2)
    with col1:
        nanoparticle_filter = st.multiselect(
            "Filter Nanopartikel:",
            options=df["nanopartikel"].unique(),
            default=df["nanopartikel"].unique()
        )
    
    with col2:
        safety_filter = st.multiselect(
            "Filter Status Keamanan:",
            options=df["status_keamanan"].unique(),
            default=df["status_keamanan"].unique()
        )
    
    # Filter data
    filtered_df = df[
        (df["nanopartikel"].isin(nanoparticle_filter)) & 
        (df["status_keamanan"].isin(safety_filter))
    ]
    
    # Tampilkan tabel
    st.dataframe(
        filtered_df,
        column_config={
            "nanopartikel": "Nanopartikel",
            "aplikasi_pangan": "Aplikasi dalam Pangan",
            "metode_uji": "Metode Uji",
            "hasil": "Hasil (LD50/IC50)",
            "status_keamanan": "Status Keamanan",
            "referensi": "Referensi"
        },
        use_container_width=True
    )
    
    # Visualisasi
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribusi Aplikasi Nanopartikel")
        app_counts = filtered_df["aplikasi_pangan"].value_counts()
        fig1 = px.bar(
            x=app_counts.values,
            y=app_counts.index,
            orientation='h',
            color=app_counts.values,
            color_continuous_scale="Viridis"
        )
        fig1.update_layout(xaxis_title="Jumlah", yaxis_title="Aplikasi")
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("Status Keamanan")
        safety_counts = filtered_df["status_keamanan"].value_counts()
        
        # Buat grafik batang dengan warna berbeda
        colors = []
        for status in safety_counts.index:
            if status == "Aman":
                colors.append("#27ae60")
            elif status == "Hati-hati":
                colors.append("#f39c12")
            else:
                colors.append("#e74c3c")
        
        fig2 = go.Figure(data=[
            go.Bar(
                x=safety_counts.index,
                y=safety_counts.values,
                marker_color=colors
            )
        ])
        fig2.update_layout(xaxis_title="Status", yaxis_title="Jumlah")
        st.plotly_chart(fig2, use_container_width=True)

def show_risk_assessment():
    """Menampilkan alat penilaian risiko"""
    st.subheader("⚠️ Alat Penilaian Risiko Nanopartikel")
    st.markdown("""
    Isi checklist berikut untuk menilai potensi risiko nanopartikel dalam penelitian Anda.
    Skor akan menentukan tingkat risiko (Rendah, Sedang, Tinggi).
    """)
    
    # Form penilaian risiko
    with st.form("risk_assessment_form"):
        st.markdown("### Checklist Penilaian Risiko")
        
        answers = []
        
        # Pertanyaan 1
        q1 = st.radio(
            "1. Apakah nanopartikel memiliki data toksikologi yang memadai?",
            ["Ya, lengkap", "Terbatas", "Tidak ada"],
            index=1
        )
        answers.append(q1)
        
        # Pertanyaan 2
        q2 = st.radio(
            "2. Apakah ada regulasi spesifik untuk nanopartikel ini?",
            ["Diatur ketat", "Diatur umum", "Tidak diatur"],
            index=1
        )
        answers.append(q2)
        
        # Pertanyaan 3
        q3 = st.radio(
            "3. Potensi bioakumulasi dalam tubuh?",
            ["Tinggi", "Sedang", "Rendah"],
            index=1
        )
        answers.append(q3)
        
        # Pertanyaan 4
        q4 = st.radio(
            "4. Ukuran partikel (nm)?",
            ["< 20 nm", "20-100 nm", "> 100 nm"],
            index=1
        )
        answers.append(q4)
        
        # Pertanyaan 5
        q5 = st.radio(
            "5. Dosis yang digunakan?",
            ["Tinggi (> 1 mg/g)", "Sedang (0.1-1 mg/g)", "Rendah (< 0.1 mg/g)"],
            index=1
        )
        answers.append(q5)
        
        # Tombol submit
        submitted = st.form_submit_button("Hitung Skor Risiko")
        
        if submitted:
            # Hitung skor
            score = calculate_risk_score(answers)
            max_score = 15
            
            # Tentukan level risiko
            if score >= 11:
                risk_level = "RENDAH"
                risk_color = "#27ae60"
                recommendations = """
                **Rekomendasi:** Nanopartikel relatif aman untuk digunakan dalam penelitian pangan 
                dengan data pendukung yang memadai. Tetap lakukan pengujian sesuai protokol keamanan.
                """
            elif score >= 6:
                risk_level = "SEDANG"
                risk_color = "#f39c12"
                recommendations = """
                **Rekomendasi:** Perlu penelitian lebih lanjut mengenai aspek toksikologi dan 
                pengawasan ketat selama penggunaan. Evaluasi parameter seperti dosis dan ukuran partikel.
                """
            else:
                risk_level = "TINGGI"
                risk_color = "#e74c3c"
                recommendations = """
                **Rekomendasi:** Nanopartikel ini memiliki potensi risiko yang signifikan. 
                Disarankan untuk mencari alternatif yang lebih aman atau melakukan kajian mendalam 
                sebelum digunakan dalam pangan.
                """
            
            # Tampilkan hasil
            st.markdown("---")
            st.subheader("Hasil Penilaian Risiko")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div style='text-align: center; padding: 20px; border-radius: 10px; background-color: {risk_color}20;'>
                    <h2 style='color: {risk_color};'>{score}/{max_score}</h2>
                    <h3 style='color: {risk_color};'>RISIKO {risk_level}</h3>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("**Detail Jawaban:**")
                for i, answer in enumerate(answers, 1):
                    st.write(f"{i}. {answer}")
            
            # Rekomendasi
            st.markdown("---")
            st.markdown("### Rekomendasi")
            st.info(recommendations)
            
            # Matriks risiko
            st.markdown("### Matriks Risiko Nanopartikel")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div style='background-color: #27ae6020; padding: 15px; border-radius: 10px; border-left: 5px solid #27ae60;'>
                <h4>🟢 Risiko Rendah</h4>
                <p><strong>Skor: 11-15</strong></p>
                <p>Data toksikologi memadai, regulasi jelas, dan potensi bioakumulasi rendah.</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div style='background-color: #f39c1220; padding: 15px; border-radius: 10px; border-left: 5px solid #f39c12;'>
                <h4>🟡 Risiko Sedang</h4>
                <p><strong>Skor: 6-10</strong></p>
                <p>Data toksikologi terbatas, perlu penelitian lebih lanjut sebelum penggunaan luas.</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div style='background-color: #e74c3c20; padding: 15px; border-radius: 10px; border-left: 5px solid #e74c3c;'>
                <h4>🔴 Risiko Tinggi</h4>
                <p><strong>Skor: 0-5</strong></p>
                <p>Data toksikologi minimal, potensi bahaya tinggi, butuh evaluasi mendalam.</p>
                </div>
                """, unsafe_allow_html=True)

def show_news():
    """Menampilkan berita terkini"""
    st.subheader("📰 Berita Terkini Nanoteknologi Pangan")
    
    for i, news in enumerate(NEWS_DATA):
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"### {news['judul']}")
                st.markdown(f"**Kategori:** {news['kategori']} | **Tanggal:** {news['tanggal']}")
                st.markdown(f"> {news['ringkasan']}")
            
            with col2:
                # Badge kategori
                if news['kategori'] == "Regulasi":
                    st.markdown('<span style="background-color: #3498db; color: white; padding: 5px 10px; border-radius: 5px;">REGULASI</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span style="background-color: #2ecc71; color: white; padding: 5px 10px; border-radius: 5px;">RISET</span>', unsafe_allow_html=True)
            
            st.markdown("---")
    
    # Form untuk menambahkan berita (simulasi)
    st.markdown("### 📤 Tambahkan Update Baru")
    
    with st.expander("Tambahkan informasi baru (simulasi)"):
        new_title = st.text_input("Judul Berita:")
        new_summary = st.text_area("Ringkasan:")
        new_category = st.selectbox("Kategori:", ["Regulasi", "Riset", "Event", "Lainnya"])
        
        if st.button("Simpan Update"):
            st.success(f"Update '{new_title}' telah disimpan (simulasi).")
            st.balloons()

if __name__ == "__main__":
    main()
