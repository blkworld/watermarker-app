import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageChops
import numpy as np

def apply_blend(base, watermark_layer, mode, global_opacity):
    # base is RGBA, watermark_layer is RGBA
    base_rgb = base.convert("RGB")
    
    # Create a version of the watermark that is purely RGB (ignoring its alpha for the math)
    # We use a white background for Multiply to keep it neutral
    w_rgb = Image.new("RGB", base.size, (255, 255, 255))
    w_rgb.paste(watermark_layer.convert("RGB"), mask=watermark_layer.split()[3])
    
    if mode == "Normal":
        # Normal mode just uses standard alpha compositing
        blended_rgb = watermark_layer.convert("RGB")
    elif mode == "Multiply":
        blended_rgb = ImageChops.multiply(base_rgb, w_rgb)
    elif mode == "Screen":
        # For screen, neutral is black
        w_rgb_screen = Image.new("RGB", base.size, (0, 0, 0))
        w_rgb_screen.paste(watermark_layer.convert("RGB"), mask=watermark_layer.split()[3])
        blended_rgb = ImageChops.screen(base_rgb, w_rgb_screen)
    elif mode == "Overlay":
        # Simple Overlay approximation
        blended_rgb = Image.blend(base_rgb, ImageChops.soft_light(base_rgb, w_rgb), 0.7)
    elif mode == "Difference":
        blended_rgb = ImageChops.difference(base_rgb, w_rgb)
    else:
        blended_rgb = watermark_layer.convert("RGB")

    # The magic fix: 
    # Use the watermark's Alpha channel multiplied by the user's opacity as a MASK
    mask = watermark_layer.split()[3]
    if global_opacity < 1.0:
        mask = ImageEnhance.Brightness(mask).enhance(global_opacity)
    
    # Composite: Base + Blended Result + Mask
    return Image.composite(blended_rgb.convert("RGBA"), base, mask)

def add_watermark(base_image, watermark_type, watermark_content, opacity, angle, size, blend_mode):
    base = base_image.convert("RGBA")
    width, height = base.size
    
    # Initialize watermark layer with transparency (0 alpha)
    watermark_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    
    # Tiling calculation
    step = int(max(width, height) / 4) 

    if watermark_type == "Text":
        try:
            font = ImageFont.truetype("arial.ttf", size)
        except:
            font = ImageFont.load_default()
        
        # We draw with full white, opacity is handled later by the blend function
        fill_color = (255, 255, 255, 255)
        
        for x in range(0, width + step, step):
            for y in range(0, height + step, step):
                item_txt = Image.new("RGBA", (size * len(watermark_content), size * 2), (0, 0, 0, 0))
                item_draw = ImageDraw.Draw(item_txt)
                item_draw.text((0, 0), watermark_content, font=font, fill=fill_color)
                item_rotated = item_txt.rotate(angle, expand=1)
                watermark_layer.paste(item_rotated, (x, y), item_rotated)

    else: # Image Watermark
        if watermark_content is not None:
            mark = Image.open(watermark_content).convert("RGBA")
            aspect_ratio = mark.width / mark.height
            mark = mark.resize((size, int(size / aspect_ratio)))
            
            for x in range(0, width + step, step):
                for y in range(0, height + step, step):
                    item_rotated = mark.rotate(angle, expand=1)
                    watermark_layer.paste(item_rotated, (x, y), item_rotated)

    return apply_blend(base, watermark_layer, blend_mode, opacity).convert("RGB")

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
    blend_mode = st.selectbox("Blend Mode:", ["Normal", "Multiply", "Screen", "Overlay", "Difference"])
    
    opacity = st.slider("Opacity:", 0.0, 1.0, 0.5)
    angle = st.slider("Rotation (Degrees):", 0, 360, 45)
    size = st.slider("Size:", 10, 1000, 200)

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
