import streamlit as st
import yt_dlp
import os

# --- UI MINIMALIS ---
st.set_page_config(page_title="YT Downloader Pro", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; background-color: #ff4b4b; color: white; height: 3.5em; font-weight: bold; border: none; }
    .stInput>div>div>input { background-color: #1a1c23; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("📽️ YT to MP4 Downloader")
st.write("Versi Bandel: Ambil kualitas terbaik & paksa jadi MP4.")

url = st.text_input("Paste YouTube URL:", placeholder="https://www.youtube.com/watch?v=...")

if url:
    if st.button("DOWNLOAD NOW"):
        try:
            # Hapus file sampah sebelumnya
            output_file = "video_final.mp4"
            if os.path.exists(output_file):
                os.remove(output_file)

            with st.spinner("Sikat! Lagi diproses..."):
                ydl_opts = {
                    # 'best' saja tanpa embel-embel agar tidak pilih-pilih format di awal
                    'format': 'bestvideo+bestaudio/best',
                    'outtmpl': 'video_temp.%(ext)s',
                    'cookiefile': 'cookies.txt', # Pake cookies biar gak 403
                    'noplaylist': True,
                    'quiet': True,
                    # KUNCI UTAMA: Paksa FFmpeg ubah apa pun hasilnya jadi MP4
                    'postprocessors': [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4',
                    }],
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Download dan biarkan post-processor merubah namanya jadi .mp4
                    ydl.download([url])
                
                # Cari file hasil konversi (biasanya namanya jadi video_temp.mp4)
                final_path = "video_temp.mp4"
                
                if os.path.exists(final_path):
                    with open(final_path, "rb") as f:
                        st.success("BERHASIL! Sikat bosku.")
                        st.download_button(
                            label="💾 KLIK UNTUK SIMPAN VIDEO",
                            data=f,
                            file_name="youtube_download.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("File MP4 tidak terbentuk. Pastikan 'ffmpeg' ada di packages.txt")

        except Exception as e:
            st.error(f"Waduh Error: {str(e)}")

st.divider()
st.caption("Kalau masih error, cek apakah linknya private atau cookies.txt sudah expired.")
