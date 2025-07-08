import os
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# -------------------------------------------------------------------
# BAGIAN 1: PENGATURAN PATH DAN PEMUATAN MODEL
# -------------------------------------------------------------------

# 🔍 Path ke model yang sudah dilatih
model_path = 'face_recognition_model.h5'

# 🔍 Path ke folder training (dibutuhkan untuk mendapatkan nama kelas)
dataset_path = "../dataset/tranning/"

# 🔍 Path ke gambar yang ingin diperiksa (ganti .jpg jika formatnya lain)
image_to_check_path = '../dataset/tranning/Rizky/tranning_1.jpg'

# 🧠 Memuat model yang sudah dilatih
try:
    model = load_model(model_path)
    print(f"✅ Model '{model_path}' berhasil dimuat.")
except Exception as e:
    print(f"❌ ERROR: Gagal memuat model. Pastikan file '{model_path}' ada di direktori yang benar.")
    print(f"Detail Error: {e}")
    exit()


try:
    # Cukup gunakan ImageDataGenerator dasar untuk membaca struktur folder
    datagen = ImageDataGenerator(rescale=1./255)
    
    # Buat generator hanya untuk mendapatkan class_indices
    generator = datagen.flow_from_directory(
        dataset_path,
        target_size=(128, 128), # Ukuran harus sama dengan saat training
        batch_size=1,
        class_mode='categorical',
        shuffle=False # Penting agar urutan tidak berubah
    )
    
    # Buat dictionary untuk mapping dari indeks (angka) ke nama kelas (string)
    # Contoh: {0: 'Ainur', 1: 'Huda', 2: 'Karim'}
    class_names = {v: k for k, v in generator.class_indices.items()}
    print(f"✅ Nama kelas berhasil didapatkan: {list(class_names.values())}")

except Exception as e:
    print(f"❌ ERROR: Gagal membaca folder dataset di '{dataset_path}'.")
    print("Pastikan path sudah benar dan berisi subfolder kelas.")
    print(f"Detail Error: {e}")
    exit()

# -------------------------------------------------------------------
# BAGIAN 3: MEMPROSES GAMBAR DAN MELAKUKAN PREDIKSI
# -------------------------------------------------------------------

# 📸 Memuat dan memproses gambar yang akan diperiksa
try:
    img = cv2.imread(image_to_check_path)
    if img is None:
        raise FileNotFoundError(f"File gambar tidak ditemukan di '{image_to_check_path}'")
    
    # 1. Ubah ukuran gambar ke 128x128 piksel (sesuai input model)
    img_resized = cv2.resize(img, (128, 128))
    
    # 2. Konversi gambar ke format array dan normalisasi (bagi dengan 255)
    img_array = np.array(img_resized) / 255.0
    
    # 3. Tambahkan dimensi batch (model mengharapkan input shape: (1, 128, 128, 3))
    img_batch = np.expand_dims(img_array, axis=0)

    # 🚀 Lakukan prediksi
    predictions = model.predict(img_batch)
    
    # 📊 Dapatkan hasil prediksi
    # Cari indeks dengan probabilitas tertinggi menggunakan np.argmax
    predicted_index = np.argmax(predictions[0])
    
    # Dapatkan nama kelas dari indeks yang diprediksi
    predicted_class_name = class_names[predicted_index]
    
    # Dapatkan nilai kepercayaan (confidence score)
    confidence = np.max(predictions[0]) * 100
    
    # Tampilkan hasil
    print("\n--- HASIL PREDIKSI ---")
    print(f"🖼️  Gambar: {image_to_check_path}")
    print(f"🧑‍💻  Terdeteksi sebagai: {predicted_class_name}")
    print(f"🎯  Tingkat Kepercayaan: {confidence:.2f}%")
    
    # Tampilkan gambar dengan hasil prediksi sebagai judul
    import matplotlib.pyplot as plt
    
    # Konversi BGR (OpenCV) ke RGB (Matplotlib) untuk tampilan warna yang benar
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.title(f"Prediksi: {predicted_class_name} ({confidence:.2f}%)")
    plt.axis('off') # Sembunyikan sumbu x dan y
    plt.show()

except FileNotFoundError as e:
    print(f"❌ ERROR: {e}")
except Exception as e:
    print(f"❌ ERROR: Terjadi kesalahan saat memproses gambar atau melakukan prediksi.")
    print(f"Detail Error: {e}")