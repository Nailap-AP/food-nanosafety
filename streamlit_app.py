import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from scipy import stats
import io
import base64

# Konfigurasi halaman
st.set_page_config(
    page_title="NanoCalibrate: Analytical Calibration Tool",
    page_icon="📈",
    layout="wide"
)

# CSS custom
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        color: #A23B72;
        font-weight: 600;
    }
    .stButton>button {
        background-color: #2E86AB;
        color: white;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #2E86AB;
    }
</style>
""", unsafe_allow_html=True)

# Judul aplikasi
st.markdown('<h1 class="main-header">🧪 NanoCalibrate: Analytical Calibration Tool</h1>', unsafe_allow_html=True)
st.markdown("### *For Food Nanotechnology Students & Researchers*")

# Sidebar untuk navigasi
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/test-tube.png", width=100)
    st.markdown("### 📊 Navigation")
    page = st.radio("Go to:", ["📥 Data Input", "📈 Calibration Curve", "🔍 Sample Prediction", "📊 Method Validation"])
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.info("""
    This tool helps you create calibration curves for analytical methods.
    
    **Features:**
    - Linear regression analysis
    - LOD/LOQ calculation
    - Sample concentration prediction
    - Method validation parameters
    """)
    
    st.markdown("---")
    st.markdown("**How to use:**")
    st.markdown("1. Input your calibration data")
    st.markdown("2. View regression results")
    st.markdown("3. Predict unknown samples")

# Fungsi perhitungan utama
def calculate_calibration(x, y):
    """Hitung parameter kalibrasi"""
    if len(x) < 2:
        return None
    
    # Regresi linear
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    r_squared = r_value**2
    
    # Prediksi y values
    y_pred = [intercept + slope * xi for xi in x]
    
    # Residuals
    residuals = [yi - ypi for yi, ypi in zip(y, y_pred)]
    
    # Standard deviation of residuals
    s_res = np.std(residuals, ddof=2) if len(residuals) > 2 else 0
    
    # LOD dan LOQ (3.3*sigma/slope dan 10*sigma/slope)
    if slope != 0:
        LOD = 3.3 * s_res / abs(slope)
        LOQ = 10 * s_res / abs(slope)
    else:
        LOD = LOQ = 0
    
    # Standard error of slope dan intercept
    n = len(x)
    x_mean = np.mean(x)
    Sxx = np.sum([(xi - x_mean)**2 for xi in x])
    se_slope = s_res / np.sqrt(Sxx) if Sxx > 0 else 0
    se_intercept = s_res * np.sqrt(1/n + x_mean**2/Sxx) if Sxx > 0 else 0
    
    # Confidence intervals (95%)
    t_val = stats.t.ppf(0.975, n-2) if n > 2 else 0
    ci_slope = t_val * se_slope
    ci_intercept = t_val * se_intercept
    
    return {
        'slope': slope,
        'intercept': intercept,
        'r_squared': r_squared,
        'r_value': r_value,
        's_res': s_res,
        'LOD': LOD,
        'LOQ': LOQ,
        'y_pred': y_pred,
        'residuals': residuals,
        'se_slope': se_slope,
        'se_intercept': se_intercept,
        'ci_slope': ci_slope,
        'ci_intercept': ci_intercept,
        'p_value': p_value,
        'equation': f"y = {slope:.4f}x + {intercept:.4f}"
    }

# Halaman 1: Data Input
if page == "📥 Data Input":
    st.markdown('<h2 class="sub-header">📥 Input Calibration Data</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### Method 1: Manual Input")
        st.markdown("Enter your calibration standard data:")
        
        # Input manual
        default_data = """Concentration,Response
0,0.01
0.5,0.15
1.0,0.32
2.0,0.61
5.0,1.52
10.0,3.01"""
        
        data_text = st.text_area("Paste CSV data (with headers):", 
                                value=default_data, 
                                height=200)
        
        if st.button("Load Manual Data", key="load_manual"):
            try:
                # Parse CSV dari text
                from io import StringIO
                df = pd.read_csv(StringIO(data_text))
                st.session_state['calibration_data'] = df
                st.success(f"Data loaded! {len(df)} points imported.")
            except:
                st.error("Error parsing CSV data. Please check format.")
    
    with col2:
        st.markdown("#### Method 2: File Upload")
        st.markdown("Upload your calibration data file:")
        
        uploaded_file = st.file_uploader("Choose CSV or Excel file", 
                                        type=['csv', 'xlsx', 'xls'])
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.session_state['calibration_data'] = df
                st.success(f"File uploaded successfully! {len(df)} rows loaded.")
            except Exception as e:
                st.error(f"Error reading file: {e}")
    
    # Tampilkan data jika sudah dimuat
    if 'calibration_data' in st.session_state:
        df = st.session_state['calibration_data']
        
        st.markdown("---")
        st.markdown("#### 📋 Data Preview")
        
        # Pilih kolom
        col1, col2 = st.columns(2)
        with col1:
            x_col = st.selectbox("Select X column (Concentration):", 
                                df.columns, 
                                index=0 if len(df.columns) > 0 else 0)
        with col2:
            y_col = st.selectbox("Select Y column (Response):", 
                                df.columns, 
                                index=1 if len(df.columns) > 1 else 0)
        
        # Simpan pilihan kolom
        st.session_state['x_col'] = x_col
        st.session_state['y_col'] = y_col
        
        # Tampilkan tabel
        st.dataframe(df, use_container_width=True)
        
        # Tampilkan statistik sederhana
        st.markdown("#### 📊 Data Statistics")
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        with stat_col1:
            st.metric("Number of Points", len(df))
        with stat_col2:
            st.metric("X Mean", f"{df[x_col].mean():.4f}")
        with stat_col3:
            st.metric("Y Mean", f"{df[y_col].mean():.4f}")
        with stat_col4:
            st.metric("Data Range", f"{df[x_col].min():.4f} - {df[x_col].max():.4f}")

# Halaman 2: Calibration Curve
elif page == "📈 Calibration Curve":
    st.markdown('<h2 class="sub-header">📈 Calibration Curve Analysis</h2>', unsafe_allow_html=True)
    
    if 'calibration_data' not in st.session_state:
        st.warning("⚠️ Please input calibration data first on the 'Data Input' page.")
        st.stop()
    
    df = st.session_state['calibration_data']
    x_col = st.session_state.get('x_col', df.columns[0])
    y_col = st.session_state.get('y_col', df.columns[1] if len(df.columns) > 1 else df.columns[0])
    
    x = df[x_col].values
    y = df[y_col].values
    
    # Hitung regresi
    results = calculate_calibration(x, y)
    
    if results is None:
        st.error("Not enough data points for calibration. Need at least 2 points.")
        st.stop()
    
    # Tampilkan hasil utama dalam metrics
    st.markdown("### 📐 Calibration Parameters")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Slope", f"{results['slope']:.4f} ± {results['se_slope']:.4f}")
        st.caption(f"95% CI: ±{results['ci_slope']:.4f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Intercept", f"{results['intercept']:.4f} ± {results['se_intercept']:.4f}")
        st.caption(f"95% CI: ±{results['ci_intercept']:.4f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("R²", f"{results['r_squared']:.6f}")
        st.caption(f"R = {results['r_value']:.4f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("p-value", f"{results['p_value']:.6f}")
        st.caption("For slope ≠ 0")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tampilkan LOD dan LOQ
    st.markdown("### 🔬 Detection Limits")
    
    lod_col1, lod_col2, lod_col3 = st.columns(3)
    with lod_col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("LOD (3.3σ/slope)", f"{results['LOD']:.6f}")
        st.caption("Limit of Detection")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with lod_col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("LOQ (10σ/slope)", f"{results['LOQ']:.6f}")
        st.caption("Limit of Quantification")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with lod_col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        s_res = results['s_res']
        st.metric("S_res", f"{s_res:.6f}")
        st.caption("Std. Dev. of Residuals")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Grafik 1: Kurva kalibrasi
    st.markdown("### 📊 Calibration Curve Plot")
    
    fig1 = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Calibration Curve", "Residual Plot"),
        column_widths=[0.7, 0.3]
    )
    
    # Plot kurva kalibrasi
    fig1.add_trace(
        go.Scatter(
            x=x, y=y,
            mode='markers',
            name='Data Points',
            marker=dict(size=10, color='#2E86AB'),
            error_y=dict(
                type='data',
                array=[s_res]*len(y),
                visible=True,
                color='gray',
                thickness=1
            )
        ),
        row=1, col=1
    )
    
    # Garis regresi
    x_line = np.linspace(min(x)*0.9, max(x)*1.1, 100)
    y_line = results['intercept'] + results['slope'] * x_line
    
    fig1.add_trace(
        go.Scatter(
            x=x_line, y=y_line,
            mode='lines',
            name=f"y = {results['slope']:.4f}x + {results['intercept']:.4f}",
            line=dict(color='#A23B72', width=3),
            hoverinfo='skip'
        ),
        row=1, col=1
    )
    
    # Plot residual
    fig1.add_trace(
        go.Scatter(
            x=x, y=results['residuals'],
            mode='markers',
            name='Residuals',
            marker=dict(size=8, color='#F18F01'),
            showlegend=False
        ),
        row=1, col=2
    )
    
    # Garis horizontal di residual plot
    fig1.add_hline(y=0, line_dash="dash", line_color="gray", row=1, col=2)
    
    # Update layout
    fig1.update_xaxes(title_text="Concentration", row=1, col=1)
    fig1.update_yaxes(title_text="Response", row=1, col=1)
    fig1.update_xaxes(title_text="Concentration", row=1, col=2)
    fig1.update_yaxes(title_text="Residuals", row=1, col=2)
    fig1.update_layout(height=500, showlegend=True)
    
    st.plotly_chart(fig1, use_container_width=True)
    
    # Tabel data lengkap
    st.markdown("### 📋 Complete Calculation Table")
    
    df_results = pd.DataFrame({
        'Concentration (x)': x,
        'Response (y)': y,
        'Predicted y': results['y_pred'],
        'Residual': results['residuals'],
        'Residual²': [r**2 for r in results['residuals']]
    })
    
    st.dataframe(df_results.style.format("{:.6f}"), use_container_width=True)
    
    # Download results
    st.markdown("### 💾 Export Results")
    
    col1, col2 = st.columns(2)
    with col1:
        # Download data sebagai CSV
        csv = df_results.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="calibration_results.csv">📥 Download Results as CSV</a>'
        st.markdown(href, unsafe_allow_html=True)
    
    with col2:
        # Generate report summary
        report = f"""CALIBRATION REPORT
========================
Equation: {results['equation']}
R²: {results['r_squared']:.6f}
R: {results['r_value']:.6f}
p-value: {results['p_value']:.6f}

SLOPE: {results['slope']:.6f} ± {results['se_slope']:.6f}
95% CI: ±{results['ci_slope']:.6f}

INTERCEPT: {results['intercept']:.6f} ± {results['se_intercept']:.6f}
95% CI: ±{results['ci_intercept']:.6f}

LOD: {results['LOD']:.6f}
LOQ: {results['LOQ']:.6f}
S_res: {results['s_res']:.6f}

Number of points: {len(x)}
X range: {min(x):.6f} - {max(x):.6f}
"""
        
        b64 = base64.b64encode(report.encode()).decode()
        href = f'<a href="data:text/plain;base64,{b64}" download="calibration_report.txt">📄 Download Report Summary</a>'
        st.markdown(href, unsafe_allow_html=True)

# Halaman 3: Sample Prediction
elif page == "🔍 Sample Prediction":
    st.markdown('<h2 class="sub-header">🔍 Predict Unknown Samples</h2>', unsafe_allow_html=True)
    
    if 'calibration_data' not in st.session_state:
        st.warning("⚠️ Please input calibration data and create calibration curve first.")
        st.stop()
    
    df = st.session_state['calibration_data']
    x_col = st.session_state.get('x_col', df.columns[0])
    y_col = st.session_state.get('y_col', df.columns[1] if len(df.columns) > 1 else df.columns[0])
    
    x = df[x_col].values
    y = df[y_col].values
    
    results = calculate_calibration(x, y)
    
    if results is None:
        st.error("Calibration not available. Please check data.")
        st.stop()
    
    st.markdown(f"**Using calibration equation:** `{results['equation']}` (R² = {results['r_squared']:.6f})")
    
    # Input sampel
    st.markdown("### 🔢 Input Sample Responses")
    
    input_method = st.radio("Input method:", ["Single Value", "Multiple Values", "Upload File"])
    
    sample_responses = []
    
    if input_method == "Single Value":
        col1, col2 = st.columns(2)
        with col1:
            response = st.number_input("Sample response:", 
                                      value=0.5, 
                                      min_value=0.0, 
                                      step=0.01,
                                      format="%.4f")
        with col2:
            replicate = st.number_input("Number of replicates:", 
                                       min_value=1, 
                                       max_value=10, 
                                       value=3)
        
        if st.button("Add to List"):
            sample_responses.extend([response] * replicate)
    
    elif input_method == "Multiple Values":
        responses_text = st.text_area("Enter responses (one per line):", 
                                     value="0.45\n0.48\n0.47\n1.25\n1.23\n1.26")
        
        if st.button("Parse Responses"):
            lines = responses_text.strip().split('\n')
            for line in lines:
                try:
                    sample_responses.append(float(line.strip()))
                except:
                    pass
    
    else:  # Upload File
        sample_file = st.file_uploader("Upload sample responses file", type=['csv', 'txt'])
        if sample_file is not None:
            try:
                if sample_file.name.endswith('.csv'):
                    sample_df = pd.read_csv(sample_file)
                else:
                    # Assume plain text with one value per line
                    content = sample_file.getvalue().decode()
                    values = [float(line.strip()) for line in content.split('\n') if line.strip()]
                    sample_responses.extend(values)
            except Exception as e:
                st.error(f"Error reading file: {e}")
    
    # Tampilkan responses yang sudah dimasukkan
    if sample_responses:
        st.markdown(f"**{len(sample_responses)} sample response(s) loaded**")
        
        # Hitung konsentrasi untuk setiap response
        concentrations = []
        for resp in sample_responses:
            if results['slope'] != 0:
                conc = (resp - results['intercept']) / results['slope']
                concentrations.append(max(0, conc))  # Tidak boleh negatif
            else:
                concentrations.append(0)
        
        # Hitung statistik jika ada replikat
        df_samples = pd.DataFrame({
            'Response': sample_responses,
            'Calculated Concentration': concentrations
        })
        
        # Group by similar responses (for replicates)
        df_samples['Group'] = pd.cut(df_samples['Response'], 
                                    bins=len(set(np.round(sample_responses, 4))),
                                    labels=False)
        
        st.dataframe(df_samples, use_container_width=True)
        
        # Statistik
        st.markdown("### 📊 Prediction Statistics")
        
        if len(concentrations) > 1:
            mean_conc = np.mean(concentrations)
            std_conc = np.std(concentrations, ddof=1)
            cv = (std_conc / mean_conc * 100) if mean_conc != 0 else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Mean Concentration", f"{mean_conc:.6f}")
            with col2:
                st.metric("Standard Deviation", f"{std_conc:.6f}")
            with col3:
                st.metric("CV%", f"{cv:.2f}%")
            
            # Prediksi dengan interval kepercayaan
            st.markdown("### 📐 Confidence Intervals")
            
            # Standard error of prediction
            n = len(x)
            x_mean = np.mean(x)
            Sxx = np.sum([(xi - x_mean)**2 for xi in x])
            
            if Sxx > 0 and n > 2:
                # Untuk setiap prediksi
                conf_level = st.slider("Confidence Level (%)", 90, 99, 95)
                alpha = 1 - conf_level/100
                t_val = stats.t.ppf(1 - alpha/2, n-2)
                
                pred_errors = []
                for i, resp in enumerate(sample_responses):
                    # Standard error untuk prediksi individu
                    se_pred = results['s_res'] * np.sqrt(1 + 1/n + ((resp - np.mean(y))**2)/((results['slope']**2)*Sxx))
                    pred_errors.append(se_pred)
                
                df_samples['SE Prediction'] = pred_errors
                df_samples[f'{conf_level}% CI Lower'] = df_samples['Calculated Concentration'] - t_val * df_samples['SE Prediction']
                df_samples[f'{conf_level}% CI Upper'] = df_samples['Calculated Concentration'] + t_val * df_samples['SE Prediction']
                
                st.dataframe(df_samples, use_container_width=True)

# Halaman 4: Method Validation
elif page == "📊 Method Validation":
    st.markdown('<h2 class="sub-header">📊 Method Validation Parameters</h2>', unsafe_allow_html=True)
    
    if 'calibration_data' not in st.session_state:
        st.warning("⚠️ Please input calibration data first.")
        st.stop()
    
    df = st.session_state['calibration_data']
    x_col = st.session_state.get('x_col', df.columns[0])
    y_col = st.session_state.get('y_col', df.columns[1] if len(df.columns) > 1 else df.columns[0])
    
    x = df[x_col].values
    y = df[y_col].values
    
    results = calculate_calibration(x, y)
    
    if results is None:
        st.error("Calibration not available.")
        st.stop()
    
    st.markdown("### 🧪 Validation Parameters Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Linearity")
        st.info(f"**R²:** {results['r_squared']:.6f}")
        
        # F-test for linearity
        if len(x) > 2:
            ss_residual = np.sum([r**2 for r in results['residuals']])
            ss_total = np.sum([(yi - np.mean(y))**2 for yi in y])
            df_residual = len(x) - 2
            df_total = len(x) - 1
            
            if ss_residual > 0 and df_residual > 0:
                ms_residual = ss_residual / df_residual
                ms_regression = (ss_total - ss_residual) / 1
                F_calc = ms_regression / ms_residual
                
                st.metric("F-value", f"{F_calc:.4f}")
    
    with col2:
        st.markdown("#### Sensitivity")
        st.info(f"**Sensitivity (slope):** {results['slope']:.6f}")
        st.metric("LOD", f"{results['LOD']:.6f}")
        st.metric("LOQ", f"{results['LOQ']:.6f}")
    
    # Additional validation parameters
    st.markdown("### 📈 Additional Calculations")
    
    # Range
    st.markdown(f"**Working Range:** {min(x):.6f} - {max(x):.6f}")
    st.markdown(f"**Linear Range:** Based on R² > 0.99")
    
    # Anda bisa menambahkan lebih banyak parameter validasi di sini
    # seperti precision, accuracy, recovery, dll.

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    <p>NanoCalibrate v1.0 | Designed for Food Nanotechnology Students</p>
    <p>For educational and research purposes</p>
    </div>
    """,
    unsafe_allow_html=True
)
