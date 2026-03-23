import streamlit as st
import pandas as pd
import os
from pymatgen.io.vasp import Poscar

# =========================
# Page Settings
# =========================
st.set_page_config(page_title="2D IMCs Database", layout="wide")
st.title("2D IMCs Database")

# =========================
# Load CSV Data
# =========================
@st.cache_data
def load_data():
    # Use first column as index (file number)
    df = pd.read_csv('data.csv', index_col=0)
    return df

df = load_data()

# =========================
# Sidebar: Page Selection
# =========================
page = st.sidebar.radio("Function", ["📊 Browse Data", "🔍 View VASP", "📥 Download Data"])

# =========================
# Page 1: Browse Data
# =========================
if page == "📊 Browse Data":
    st.subheader("Data Table")
    
    # Search box
    search = st.text_input("Search by formula or other columns:")
    if search:
        # Convert all to string, ignore NaN
        df_display = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
    else:
        df_display = df
    
    st.dataframe(df_display, use_container_width=True)
    st.write(f"Total entries: {len(df_display)}")

# =========================
# Page 2: View VASP
# =========================
elif page == "🔍 View VASP":
    st.subheader("View VASP Structure")
    
    # Dropdown: show "formula (index)"
    options = [f"{df.loc[idx, 'formula']} ({idx})" for idx in df.index]
    selected_display = st.selectbox("Select structure:", options)
    
    if selected_display:
        # Extract index
        selected_idx = int(selected_display.split('(')[-1].strip(')'))
        formula = df.loc[selected_idx, 'formula']
        
        # Build VASP file path using formula
        vasp_path = f"vasp_files/{formula}.vasp"
        
        if os.path.exists(vasp_path):
            # Read structure
            structure = Poscar.from_file(vasp_path).structure
            st.write(f"### {formula} (Index {selected_idx})")
            st.write("Lattice parameters:")
            st.write(structure.lattice)
            st.write("Atomic positions:")
            st.write(structure)
        else:
            st.warning("Corresponding VASP file does not exist!")

# =========================
# Page 3: Download Data
# =========================
elif page == "📥 Download Data":
    st.subheader("Download Data / VASP Files")
    
    # Download CSV
    csv_bytes = df.to_csv().encode('utf-8')
    st.download_button("Download CSV Data", data=csv_bytes, file_name="data.csv", mime="text/csv")
    
    # Download single VASP file by formula
    options = [f"{df.loc[idx, 'formula']} ({idx})" for idx in df.index]
    selected_display = st.selectbox("Select VASP file to download:", options, key="download_select")
    selected_idx = int(selected_display.split('(')[-1].strip(')'))
    formula = df.loc[selected_idx, 'formula']
    vasp_path = f"vasp_files/{formula}.vasp"
    
    if os.path.exists(vasp_path):
        with open(vasp_path, "rb") as f:
            vasp_bytes = f.read()
        st.download_button(f"Download VASP file ({formula}.vasp)", data=vasp_bytes, file_name=f"{formula}.vasp")
    else:
        st.warning("Corresponding VASP file does not exist!")
