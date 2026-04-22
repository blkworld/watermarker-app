import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageChops
import numpy as np

def apply_blend(base, watermark_layer, mode):
    # Separate RGB and Alpha from the watermark layer
    w_rgb = watermark_layer.convert("RGB")
    w_alpha = watermark_layer.split()[3]
    
    if mode == "Normal":
        return Image.alpha_composite(base, watermark_layer)
    elif mode == "Multiply":
        blended_rgb = ImageChops.multiply(base.convert("RGB"), w_rgb)
    elif mode == "Screen":
        blended_rgb = ImageChops.screen(base.convert("RGB"), w_rgb)
    elif mode == "Overlay":
        # Overlay logic for Pillow
        blended_rgb = Image.blend(base.convert("RGB"), ImageChops.soft_light(base.convert("RGB"), w_rgb), 0.5)
    elif mode == "Difference":
        blended_rgb = ImageChops.difference(base.convert("RGB"), w_rgb)
    else:
        return Image.alpha_composite(base, watermark_layer)

    # Re-apply alpha channel to the blended result
    blended_rgba = blended_rgb.convert("RGBA")
    blended_rgba.putalpha(w_alpha)
    return Image.alpha_composite(base, blended_rgba)

def add_watermark(base_image, watermark_type, watermark_content, opacity, angle, size, blend_mode):
    base = base_image.convert("RGBA")
    width, height = base.size
    txt_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    
    # Calculate tiling spacing
    step = int(max(width, height) / 4) 

    if watermark_type == "Text":
        try:
            # You can upload a .ttf file to your repo to use a specific font
            font = ImageFont.truetype("arial.ttf", size)
        except:
            font = ImageFont.load_default()
        
        fill_color = (255, 255, 255, int(255 * opacity))
        
        for x in range(0, width + step, step):
            for y in range(0, height + step, step):
                item_txt = Image.new("RGBA", (size * len(watermark_content), size * 2), (0, 0, 0, 0))
                item_draw = ImageDraw.Draw(item_txt)
                item_draw.text((0, 0), watermark_content, font=font, fill=fill_color)
                item_rotated = item_txt.rotate(angle, expand=1)
                txt_layer.paste(item_rotated, (x, y), item_rotated)

    else: # Image Watermark
        if watermark_content is not None:
            mark = Image.open(watermark_content).convert("RGBA")
            aspect_ratio = mark.width / mark.height
            mark = mark.resize((size, int(size / aspect_ratio)))
            
            alpha = mark.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
            mark.putalpha(alpha)
            
            for x in range(0, width + step, step):
                for y in range(0, height + step, step):
                    item_rotated = mark.rotate(angle, expand=1)
                    txt_layer.paste(item_rotated, (x, y), item_rotated)

    return apply_blend(base, txt_layer, blend_mode).convert("RGB")

# --- STREAMLIT UI ---
st.set_page_config(page_title="Watermarker Pro", layout="wide")
st.title("📸 Professional Watermarker")

with st.sidebar:
    st.header("⚙️ Settings")
    mode = st.radio("Watermark Type:", ["Text", "Image"])
    
    if mode == "Text":
        content = st.text_input("Enter Text:", "CONFIDENTIAL")
    else:
        content = st.file_uploader("Upload Logo (PNG recommended):", type=['png', 'jpg', 'jpeg'])
    
    st.divider()
    blend_mode = st.selectbox("Blend Mode:", 
                              ["Normal", "Multiply", "Screen", "Overlay", "Difference"])
    
    opacity = st.slider("Opacity:", 0.0, 1.0, 0.3)
    angle = st.slider("Rotation (Degrees):", 0, 360, 45)
    size = st.slider("Size:", 10, 800, 100)

uploaded_file = st.file_uploader("Upload Main Photo:", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    img = Image.open(uploaded_file)
    result = add_watermark(img, mode, content, opacity, angle, size, blend_mode)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(img, caption="Original Photo", use_container_width=True)
    with col2:
        st.image(result, caption=f"Result ({blend_mode} Mode)", use_container_width=True)
        
        import io
        buf = io.BytesIO()
        result.save(buf, format="JPEG", quality=95)
        st.download_button("💾 Download Result", buf.getvalue(), "watermarked.jpg", "image/jpeg")
