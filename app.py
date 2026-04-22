import streamlit as st
import yt_dlp
import os
import io

# --- STREAMLIT UI ---
st.set_page_config(page_title="YT Downloader Pro", page_icon="🎬")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stTextInput > div > div > input { background-color: #262730; color: white; border: 1px solid #444; }
    .stButton > button { width: 100%; border-radius: 5px; background-color: #FF0000; color: white; border: none; height: 3em; font-weight: bold; }
    .stButton > button:hover { background-color: #CC0000; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎬 YT to MP4 Downloader")
st.write("Menggunakan akses Cookies untuk bypass blokir YouTube.")

url = st.text_input("Enter YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")

if url:
    if st.button("Start Download & Convert"):
        try:
            # Pastikan file lama dihapus agar tidak tertukar
            if os.path.exists("downloaded_video.mp4"):
                os.remove("downloaded_video.mp4")

            with st.spinner("Downloading with Cookies... please wait."):
                # Opsi YT-DLP dengan integrasi Cookies
                ydl_opts = {
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'merge_output_format': 'mp4',
                    'outtmpl': 'downloaded_video.%(ext)s',
                    'cookiefile': 'cookies.txt',  # Menggunakan file cookie yang kamu berikan 
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'quiet': True,
                    'no_warnings': True,
                    'nocheckcertificate': True,
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                # Verifikasi file hasil download
                if os.path.exists("downloaded_video.mp4"):
                    with open("downloaded_video.mp4", "rb") as file:
                        st.success("Berhasil! Video siap di-download.")
                        st.download_button(
                            label="💾 DOWNLOAD MP4 SEKARANG",
                            data=file,
                            file_name="video_result.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("Proses selesai tapi file MP4 tidak ditemukan. Cek log.")

        except Exception as e:
            # Menampilkan error agar mudah di-debug
            st.error(f"Error: {str(e)}")

st.divider()
st.info("Tips: Jika masih error 403, pastikan file cookies.txt di GitHub isinya masih fresh.")
