# --- STREAMLIT UI ---
st.set_page_config(page_title="Watermarker Pro", layout="wide")
st.title("📸 Professional Watermarker")

with st.sidebar:
    st.header("⚙️ Settings")
    mode = st.radio("Watermark Type:", ["Text", "Image"])
    
    if mode == "Text":
        content = st.text_input("Enter Text:", "CONFIDENTIAL")
    else:
        content = st.file_uploader("Upload Logo:", type=['png', 'jpg', 'jpeg'])
    
    st.divider()
    blend_mode = st.selectbox("Blend Mode:", ["Normal", "Multiply", "Screen", "Overlay", "Difference"])
    
    opacity = st.slider("Opacity:", 0.0, 1.0, 0.5)
    angle = st.slider("Rotation:", 0, 360, 45)
    size = st.slider("Size:", 10, 1000, 200)
    
    # TAMBAHKAN OPSI KUALITAS PREVIEW
    preview_quality = st.select_slider("Preview Speed", options=["Fast (Low Res)", "Normal", "High Quality"], value="Fast (Low Res)")

uploaded_file = st.file_uploader("Upload Main Photo:", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    raw_img = Image.open(uploaded_file)
    
    # LOGIKA FAST PREVIEW: Kecilkan gambar hanya untuk tampilan web
    w, h = raw_img.size
    if preview_quality == "Fast (Low Res)":
        preview_scale = 800 / max(w, h)
    elif preview_quality == "Normal":
        preview_scale = 1500 / max(w, h)
    else:
        preview_scale = 1.0
        
    preview_img = raw_img.resize((int(w * preview_scale), int(h * preview_scale))) if preview_scale < 1.0 else raw_img

    # Render watermark pada gambar preview (Cepat karena resolusi rendah)
    result_preview = add_watermark(preview_img, mode, content, opacity, angle, int(size * preview_scale), blend_mode)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(raw_img, caption="Original", use_container_width=True)
    with col2:
        st.image(result_preview, caption=f"Fast Preview ({blend_mode})", use_container_width=True)
        
        # SAAT DOWNLOAD: Baru render versi High Resolution (Full Quality)
        if st.button("🚀 Prepare High-Res Download"):
            with st.spinner("Processing full resolution image..."):
                full_res_result = add_watermark(raw_img, mode, content, opacity, angle, size, blend_mode)
                
                import io
                buf = io.BytesIO()
                full_res_result.save(buf, format="JPEG", quality=95)
                st.download_button("💾 Download Full Resolution", buf.getvalue(), "watermarked_full.jpg", "image/jpeg")
