import glob
import cv2
import os
import mysql.connector
import face_recognition
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from tensorflow.keras.models import load_model
from PIL import Image
from sklearn.metrics import accuracy_score
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

# 🔗 Koneksi Database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="library_attendance",
    autocommit=True
)
cursor = db.cursor(buffered=True)

# 🔍 Load Model CNN Terbaru
model = load_model("face_recognition_model.h5")

# 🔍 Folder Dataset
DATASET_DIR = "../dataset/absensi"
if not os.path.exists(DATASET_DIR):
    os.makedirs(DATASET_DIR)  # ✅ Buat folder dataset jika belum ada

# 🔍 Folder Dataset
DATASET_DIR_TRAIN = "../dataset/tranning"
if not os.path.exists(DATASET_DIR_TRAIN):
    os.makedirs(DATASET_DIR_TRAIN)  # ✅ Buat folder dataset jika belum ada


def evaluate_model_accuracy(model_path, dataset_path):
    """✅ Evaluasi akurasi model CNN berdasarkan dataset validasi."""
    
    try:
        model = load_model(model_path)
        print(f"✅ Model {model_path} berhasil dimuat!")

        # 🔍 Preprocessing dataset validasi
        datagen = ImageDataGenerator(rescale=1./255)
        validation_data = datagen.flow_from_directory(
            dataset_path,
            target_size=(128, 128),
            batch_size=16,
            class_mode="categorical"
        )

        if validation_data.samples == 0:
            print("❌ ERROR: Dataset validasi kosong, tambahkan lebih banyak gambar!")
            return None

        # 🔍 Evaluasi model dan mendapatkan akurasi
        accuracy = model.evaluate(validation_data)[1] * 100
        print(f"✅ Akurasi Model CNN: {accuracy:.2f}%")

        return accuracy
    
    except Exception as e:
        print(f"❌ ERROR: Gagal menghitung akurasi - {str(e)}")
        return None

@app.route("/api/checkAPI", methods=["GET"])
def checkAPI():
    return jsonify({
        "status": "success",
        "message": "✅ API berjalan dengan baik!"
    })

def capture_image(nim):
    """✅ Tangkap gambar dari kamera dan simpan sebagai nim_x.jpg hanya jika wajah dikenali"""
    dataset_dir = "../dataset/absensi/"  # 🔥 Pastikan hanya folder ini digunakan

    if not os.path.exists(dataset_dir):
        os.makedirs(dataset_dir)

    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("❌ ERROR: Kamera tidak bisa diakses!")
        return None

    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("❌ ERROR: Gagal menangkap gambar!")
        return None

    # 🔍 Lakukan pengenalan wajah sebelum menyimpan gambar
    image_temp = "temp_scan.jpg"
    cv2.imwrite(image_temp, frame)

    image = face_recognition.load_image_file(image_temp)
    face_encodings = face_recognition.face_encodings(image)

    if not face_encodings:
        os.remove(image_temp)  # 🔥 Hapus gambar jika wajah tidak terdeteksi
        print("❌ Wajah tidak dikenali, gambar tidak disimpan!")
        return None

    # 🔍 Cek apakah ada file dengan nama NIM yang sudah ada
    existing_files = glob.glob(os.path.join(dataset_dir, f"{nim}_*.jpg"))

    # 🔍 Tentukan angka terakhir yang sudah ada
    if existing_files:
        numbers = [int(os.path.splitext(f.split("_")[-1])[0]) for f in existing_files]
        next_number = max(numbers) + 1
    else:
        next_number = 1

    # 🔍 Buat nama file baru dengan angka di belakang
    image_path = os.path.join(dataset_dir, f"{nim}_{next_number}.jpg")

    # 🔥 Simpan gambar jika wajah dikenali
    cv2.imwrite(image_path, frame)
    os.remove(image_temp)  # 🔥 Hapus gambar sementara setelah verifikasi

    print(f"✅ Gambar berhasil disimpan sebagai: {image_path}")
    return image_path

@app.route("/api/scan", methods=["POST"])
def scan():
    keperluan = request.form.get("purpose")

    cap = cv2.VideoCapture(1)  # 🔥 Pastikan kamera dapat diakses
    if not cap.isOpened():
        return jsonify({"status": "error", "message": "❌ Kamera tidak bisa diakses!"}), 400

    ret, frame = cap.read()
    cap.release()
    if ret:
        print("✅ Gambar berhasil ditangkap dan disimpan sebagai `test_image.jpg`")
    else:
        print("❌ ERROR: Gagal menangkap gambar!")

    if not ret:
        return jsonify({"status": "error", "message": "❌ Gagal menangkap gambar!"}), 400

    try:
        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)

        if not face_encodings:
            return jsonify({"status": "unknown", "message": "❌ Wajah tidak dikenali, silakan daftar ulang."})

        # 🔍 Cek database untuk mencocokkan encoding wajah dengan mahasiswa
        cursor.execute("SELECT id, name, nim, face_encoding FROM students")
        students = cursor.fetchall()

        for student in students:
            stored_encoding = np.array(eval(student[3]))  
            match = face_recognition.compare_faces([stored_encoding], face_encodings[0], tolerance=0.6)

            if match[0]:  # ✅ Wajah cocok dengan database
                student_id, name, nim = student[0], student[1], student[2]
                arrival_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # 🔍 Simpan gambar dengan format berurutan sesuai NIM
                image_path = capture_image(nim)  

                # 🔗 Simpan kehadiran langsung ke database
                cursor.execute(
                    "INSERT INTO attendance (student_id, arrival_time, purpose) VALUES (%s, %s, %s)",
                    (student_id, arrival_time, keperluan)
                )
                db.commit()

                return jsonify({
                    "status": "success",
                    "message": f"✅ {name} ({nim}) telah hadir",
                    "name": name,
                    "nim": nim,
                    "arrival_time": arrival_time,
                    "purpose": keperluan,
                })

    except Exception as e:
        return jsonify({"status": "error", "message": f"❌ Error saat memproses gambar: {str(e)}"}), 500

    return jsonify({"status": "unknown", "message": "❌ Mahasiswa tidak ditemukan dalam database."})

@app.route("/api/register", methods=["POST"])
def register():
    """✅ Registrasi mahasiswa dengan kamera"""
    if "name" not in request.form or "nim" not in request.form or "image" not in request.files:
        return jsonify({"status": "error", "message": "❌ Data tidak lengkap!"}), 400

    name = request.form["name"]
    nim = request.form["nim"]
    image_file = request.files["image"]

    # 🔍 Simpan gambar dan hindari konflik nama
    image_path = os.path.join(DATASET_DIR_TRAIN, f"{nim}.jpg")

    if os.path.exists(image_path):
        return jsonify({"status": "error", "message": "❌ Gambar mahasiswa sudah ada, registrasi ulang tidak diperlukan!"})

    image_file.save(image_path)

    # 🔍 Deteksi wajah
    try:
        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)
        if not face_encodings:
            return jsonify({"status": "error", "message": "❌ Wajah tidak ditemukan"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": f"❌ Error saat memproses gambar: {str(e)}"}), 500

    face_encoding_str = str(face_encodings[0].tolist())

    # 🔗 Simpan ke Database
    cursor.execute("INSERT INTO students (name, nim, face_encoding, image_path) VALUES (%s, %s, %s, %s)", 
                   (name, nim, face_encoding_str, image_path))
    db.commit()

    return jsonify({"status": "success", "message": "✅ Registrasi berhasil!", "image_preview": image_path})

@app.route("/api/accuracy", methods=["GET"])
def get_model_accuracy():
    """✅ Menghitung dan Menampilkan Akurasi Model Neural Network dengan Nama & NIM Mahasiswa"""
    
    # 🔍 Ambil dataset validasi dari database
    image_paths = []
    labels = []
    mahasiswa_list = []

    cursor.execute("SELECT id, name, nim FROM students")
    students = cursor.fetchall()

    dataset_dir = DATASET_DIR

    for student in students:
        nim = student[2]  # Gunakan NIM sebagai identitas
        mahasiswa_list.append({"name": student[1], "nim": nim})  

        # 🔍 Cari semua file gambar yang sesuai dengan NIM (contoh: 21530010_1.jpg, 21530010_2.jpg)
        file_search = glob.glob(os.path.join(dataset_dir, f"{nim}*.jpg"))
        
        if file_search:
            image_paths.extend(file_search)  # Tambahkan semua varian gambar ke dataset validasi
            labels.extend([nim] * len(file_search))  # Gunakan NIM sebagai label untuk semua gambar
        
    print(f"✅ Dataset validasi diambil: {len(image_paths)} sampel")

    predictions = []
    true_labels = []

    for image_path, true_label in zip(image_paths, labels):
        try:
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)
            
            if not face_encodings:
                continue  

            img = cv2.imread(image_path)
            img = cv2.resize(img, (128, 128))
            img = np.expand_dims(img, axis=0) / 255.0  

            prediction = model.predict(img)
            predicted_label = np.argmax(prediction)
            
            predictions.append(predicted_label)
            true_labels.append(true_label)

        except Exception as e:
            print(f"❌ Error memproses gambar {image_path}: {str(e)}")

    # 🔍 Hitung akurasi model
    if predictions and true_labels:
        accuracy = accuracy_score(true_labels, predictions) * 100
    else:
        accuracy = 0  

    return jsonify({
        "status": "success",
        "accuracy": f"{accuracy:.2f}%",
        "total_samples": len(true_labels),
        "students": mahasiswa_list 
    })

@app.route("/api/accuracy_model", methods=["GET"])
def get_model_accuracy_model():
    """✅ API untuk mengambil akurasi model CNN."""
    model_path = "face_recognition_model.h5"
    dataset_path = "../dataset/mahasiswa"
    
    accuracy = evaluate_model_accuracy(model_path, dataset_path)
    
    if accuracy is not None:
        return jsonify({"status": "success", "accuracy": f"{accuracy:.2f}%"})
    else:
        return jsonify({"status": "error", "message": "❌ Gagal menghitung akurasi!"})


if __name__ == "__main__":
    app.run(debug=True)
