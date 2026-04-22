import streamlit as st
import yt_dlp
import os

# --- UI SETTINGS ---
st.set_page_config(page_title="YT Downloader", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; background-color: #ff4b4b; color: white; height: 3em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("📽️ YT to MP4 Downloader")
st.write("Sederhana, cepat, dan bypass 403.")

url = st.text_input("Paste YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")

if url:
    if st.button("Download Now"):
        try:
            # Hapus file lama biar gak numpuk
            if os.path.exists("video.mp4"): os.remove("video.mp4")

            with st.spinner("Lagi diproses, tunggu bentar..."):
                ydl_opts = {
                    # Ambil yang terbaik, gausah pilih-pilih format di awal
                    'format': 'bestvideo+bestaudio/best',
                    'merge_output_format': 'mp4',
                    'outtmpl': 'video.%(ext)s',
                    'cookiefile': 'cookies.txt',  # Pake cookies biar gak 403
                    'quiet': True,
                    'postprocessors': [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4',
                    }],
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                if os.path.exists("video.mp4"):
                    with open("video.mp4", "rb") as f:
                        st.success("Selesai!")
                        st.download_button(
                            label="💾 SAVE TO DEVICE",
                            data=f,
                            file_name="video_result.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("File gagal dibuat. Cek apakah ffmpeg sudah diinstall di packages.txt")

        except Exception as e:
            st.error(f"Waduh Error: {str(e)}")
