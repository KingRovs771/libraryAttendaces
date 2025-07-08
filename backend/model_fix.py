import os
import cv2
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from PIL import Image

# -----------------------------------------------------------------------------------
# BAGIAN 1: ANALISIS DAN TAMPILAN DATASET (SESUAI GAMBAR)
# -----------------------------------------------------------------------------------

# 🔍 Path Dataset diubah sesuai permintaan
dataset_path = "../dataset/tranning"
print(f"✅ Dataset path: {os.path.abspath(dataset_path)}\n")

# Dapatkan daftar kelas (subfolder)
if not os.path.exists(dataset_path) or not os.listdir(dataset_path):
    print(f"❌ ERROR: Folder dataset di '{os.path.abspath(dataset_path)}' tidak ditemukan atau kosong!")
    exit()

subfolders = [f for f in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, f))]
if not subfolders:
    print("❌ ERROR: Dataset tidak memiliki subfolder kelas!")
    exit()

print("--- Menampilkan Jumlah Sampel Asli per Kelas ---")
initial_samples = {}
for class_folder in sorted(subfolders):
    class_path = os.path.join(dataset_path, class_folder)
    num_files = len(os.listdir(class_path))
    initial_samples[class_folder] = num_files
    # Output mirip dengan 'Gambar 4.3 Data wajah'
    print(f"[{'*' * 20}] ({num_files:3d} samples)   label : {class_folder}")

print("\n--- Menampilkan Jumlah Data Setelah Augmentasi (Simulasi) ---")
# Berdasarkan deskripsi: 1 gambar asli + 20 hasil augmentasi = 21
# Total per kelas = (jumlah sampel asli * 20) + jumlah sampel asli
augmented_counts = []
for class_name, initial_count in initial_samples.items():
    augmented_total = initial_count + (initial_count * 20) # Totalnya 1050 jika sampel asli 50
    augmented_counts.append((class_name, augmented_total))

# Output mirip dengan 'Gambar 4.4 Data wajah setelah di augmentasi'
for item in augmented_counts:
    print(item)

print("\n--- Menampilkan Matriks Gambar Sampel ---")
# Ambil satu gambar sebagai contoh dari kelas pertama
try:
    first_class_folder = sorted(subfolders)[0]
    first_class_path = os.path.join(dataset_path, first_class_folder)
    sample_image_name = os.listdir(first_class_path)[0]
    sample_image_path = os.path.join(first_class_path, sample_image_name)

    print(f"🖼️  Memuat gambar sampel dari: {sample_image_path}\n")
    
    # Baca gambar menggunakan OpenCV
    img = cv2.imread(sample_image_path)
    
    # Ubah ukuran gambar (misal ke 250x250 seperti di contoh)
    img_resized = cv2.resize(img, (250, 250))
    
    # Tampilkan informasi bentuk dan beberapa nilai piksel (matriks)
    # Output mirip dengan 'Gambar 4.7 Matriks gambar'
    print(f"Shape gambar setelah di-resize: {img_resized.shape} -> (Tinggi, Lebar, Channel Warna)")
    print("Nilai matriks piksel (beberapa baris/kolom pertama):")
    print(img_resized[:5, :5, 0]) # Tampilkan matriks 5x5 untuk channel Biru (Blue)
    
    # Tampilkan gambar menggunakan Matplotlib
    # Konversi BGR (OpenCV) ke RGB (Matplotlib) agar warna sesuai
    plt.imshow(cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB))
    plt.title(f"Contoh Gambar: {sample_image_name}")
    plt.show()

except Exception as e:
    print(f"❌ ERROR saat memproses gambar sampel: {e}")

print("\n--- Memulai Proses Training Model ---\n")

# 🔍 Verifikasi dan bersihkan file gambar yang rusak
print("✅ Memverifikasi semua file gambar dalam dataset...")
for class_folder in subfolders:
    class_path = os.path.join(dataset_path, class_folder)
    for filename in os.listdir(class_path):
        filepath = os.path.join(class_path, filename)
        try:
            with Image.open(filepath) as img:
                img.verify()
        except Exception:
            print(f"❌ ERROR: File '{filename}' rusak atau format tidak dikenali. Menghapus...")
            os.remove(filepath)

# 🧠 Membuat Model TensorFlow
num_classes = len(subfolders)
model = Sequential([
    Conv2D(32, (3,3), activation='relu', input_shape=(128, 128, 3)),
    MaxPooling2D(2,2),
    Conv2D(64, (3,3), activation='relu'),
    MaxPooling2D(2,2),
    Flatten(),
    Dense(128, activation='relu'),
    Dense(num_classes, activation='softmax')
])

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model.summary() # Tampilkan arsitektur model

# 🏞️ Augmentasi Data on-the-fly dengan ImageDataGenerator
datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20, # Menambahkan augmentasi seperti di deskripsi
    zoom_range=0.2,
    horizontal_flip=True,
    validation_split=0.15 # Memisahkan 15% untuk testing/validasi
)

try:
    # Generator untuk data training (85%)
    train_data = datagen.flow_from_directory(
        dataset_path,
        target_size=(128, 128),
        batch_size=16,
        class_mode="categorical",
        subset='training' # Tentukan ini sebagai data training
    )

    # Generator untuk data testing (15%)
    test_data = datagen.flow_from_directory(
        dataset_path,
        target_size=(128, 128),
        batch_size=16,
        class_mode="categorical",
        subset='validation' # Tentukan ini sebagai data validasi/testing
    )

    # 🚀 Latih Model
    model.fit(train_data, epochs=10, validation_data=test_data)
    
    # 💾 Simpan Model
    model.save("face_recognition_model.h5")
    print("\n✅ Model telah disimpan sebagai 'face_recognition_model.h5'")

except Exception as e:
    print(f"\n❌ ERROR saat mempersiapkan data atau melatih model: {str(e)}")
    exit()