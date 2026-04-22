import streamlit as st
import yt_dlp
import os
import io

# --- UI SETUP ---
st.set_page_config(page_title="Ultimate YT Downloader", page_icon="📽️")

st.markdown("""
    <style>
    .main { background: #0e1117; }
    .stButton>button { width: 100%; background-color: #ff4b4b; color: white; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📽️ YT to MP4 Downloader")
st.write("Sederhana, cepat, dan bypass 403.")

url = st.text_input("Paste YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")

if url:
    if st.button("Download Now"):
        try:
            # Bersihkan file sisa
            for f in os.listdir():
                if f.endswith(".mp4") or f.endswith(".webm"):
                    os.remove(f)

            with st.spinner("Processing... harap bersabar."):
                ydl_opts = {
                    'format': 'bestvideo+bestaudio/best',
                    'merge_output_format': 'mp4',
                    'outtmpl': 'video_result.%(ext)s',
                    'cookiefile': 'cookies.txt',  # Kunci utama tembus blokir
                    'postprocessors': [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4',
                    }],
                    'noplaylist': True,
                    'quiet': True,
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                # Cari file hasil merge mp4
                if os.path.exists("video_result.mp4"):
                    with open("video_result.mp4", "rb") as f:
                        st.success("Download Selesai!")
                        st.download_button(
                            label="💾 SAVE TO DEVICE",
                            data=f,
                            file_name="youtube_video.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("Gagal menggabungkan file. Pastikan packages.txt berisi ffmpeg.")

        except Exception as e:
            st.error(f"Waduh Error: {str(e)}")

st.divider()
st.caption("Pastikan cookies.txt di GitHub masih aktif.")
