import os
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# 🔍 Path Dataset
dataset_path = "../dataset/"  # Sesuaikan path berdasarkan lokasi eksekusi
print("✅ Dataset path:", os.path.abspath(dataset_path))

# 🔍 Cek apakah dataset memiliki subfolder
subfolders = [f for f in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, f))]
if not subfolders:
    print("❌ ERROR: Dataset kosong atau tidak memiliki subfolder!")
    exit()

print(f"✅ Dataset memiliki {len(subfolders)} kelas:", subfolders)

# 🔍 Verifikasi semua file gambar dalam dataset
for class_folder in subfolders:
    class_path = os.path.join(dataset_path, class_folder)
    
    for filename in os.listdir(class_path):
        filepath = os.path.join(class_path, filename)
        try:
            img = Image.open(filepath)
            img.verify()
            print(f"✅ {filename} - Format: {img.format}")
        except:
            print(f"❌ ERROR: {filename} rusak atau format tidak dikenali. Menghapus...")
            os.remove(filepath)  # 🔥 Hapus file yang rusak agar tidak mengganggu training

# 🔄 Rename semua file dengan format yang konsisten tanpa konflik nama
for class_folder in subfolders:
    class_path = os.path.join(dataset_path, class_folder)

    for i, filename in enumerate(os.listdir(class_path)):
        ext = filename.split(".")[-1]
        new_filename = f"{class_folder}_{i}.{ext}"
        new_path = os.path.join(class_path, new_filename)

        # 🔍 Cek apakah file dengan nama baru sudah ada
        counter = 1
        while os.path.exists(new_path):
            new_path = os.path.join(class_path, f"{class_folder}_{i}_{counter}.{ext}")
            counter += 1

        os.rename(os.path.join(class_path, filename), new_path)

print("✅ Semua file telah diberi nama ulang secara konsisten.")

# 🔍 Membuat Model TensorFlow
num_classes = len(subfolders)
model = Sequential([
    Conv2D(32, (3,3), activation='relu', input_shape=(128, 128, 3)),
    MaxPooling2D(2,2),
    Conv2D(64, (3,3), activation='relu'),
    MaxPooling2D(2,2),
    Flatten(),
    Dense(128, activation='relu'),
    Dense(num_classes, activation='softmax')  # Output sesuai jumlah kelas wajah
])

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

# 🔄 Cek apakah dataset memiliki cukup gambar untuk training
datagen = ImageDataGenerator(rescale=1./255)
try:
    train_data = datagen.flow_from_directory(
        dataset_path,
        target_size=(128, 128),
        batch_size=16,
        class_mode="categorical"
    )
except Exception as e:
    print(f"❌ ERROR saat mengakses dataset: {str(e)}")
    exit()

# 🔄 Latih Model
model.fit(train_data, epochs=10)
model.save("face_recognition_model.h5")
print("✅ Model telah disimpan sebagai 'face_recognition_model.h5'")

# 🔄 Fungsi Retrain Model
def retrain_model():
    """🔄 Melatih ulang model dengan data terbaru"""
    try:
        train_data = datagen.flow_from_directory(
            "../dataset/tranning/",
            target_size=(128, 128),
            batch_size=16,
            class_mode="categorical"
        )

        num_classes_updated = len(os.listdir("../dataset/tranning/"))
        model = Sequential([
            Conv2D(32, (3,3), activation='relu', input_shape=(128, 128, 3)),
            MaxPooling2D(2,2),
            Conv2D(64, (3,3), activation='relu'),
            MaxPooling2D(2,2),
            Flatten(),
            Dense(128, activation='relu'),
            Dense(num_classes_updated, activation='softmax')  # Output sesuai jumlah kelas wajah terbaru
        ])

        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        model.fit(train_data, epochs=5)  # 🔄 Latih ulang dengan data baru
        model.save("face_recognition_model.h5")
        print("✅ Model telah diperbarui dengan data terbaru!")

    except Exception as e:
        print(f"❌ ERROR saat melatih ulang model: {str(e)}")
        exit()
