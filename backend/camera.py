import cv2
import os

def capture_image():
    """✅ Mengambil gambar dari kamera dan menyimpannya dalam folder dataset"""
    dataset_dir = "../dataset/mahasiswa"
    if not os.path.exists(dataset_dir):  # Cek apakah folder sudah ada
        os.makedirs(dataset_dir)  # Buat folder dataset jika belum ada

    # 🔍 Tangkap gambar dari kamera
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    if ret:
        image_path = os.path.join(dataset_dir, "scan_" + str(len(os.listdir(dataset_dir)) + 1) + ".jpg")
        cv2.imwrite(image_path, frame)  # Simpan gambar

        print(f"✅ Gambar berhasil disimpan: {image_path}")
        return image_path
    else:
        print("❌ Gagal mengambil gambar")
        return None
