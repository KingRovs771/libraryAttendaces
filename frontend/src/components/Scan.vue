<template>
  <div class="scan">
    <h2>📸 Scan Wajah Mahasiswa</h2>
    <video ref="videoElement" autoplay></video>
    <label>📝 Keperluan:</label>
    <input v-model="purpose" type="text" placeholder="Masukkan keperluan kehadiran" required />
    <button @click="captureImage">✅ Scan & Absensi</button>
    <p v-if="message">{{ message }}</p>

    <!-- 🔥 Pop-up notifikasi setelah scan -->
    <div v-if="attendanceData" class="modal">
      <div class="modal-content">
        <h3>✅ Kehadiran Berhasil!</h3>
        <p><strong>Nama:</strong> {{ attendanceData.name }}</p>
        <p><strong>NIM:</strong> {{ attendanceData.nim }}</p>
        <p><strong>Keperluan:</strong> {{ attendanceData.purpose }}</p>
        <p><strong>Waktu Kehadiran:</strong> {{ attendanceData.arrival_time }}</p>
        <button @click="closeModal">OK</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      message: '',
      purpose: '',
      attendanceData: null, // 🔍 Data kehadiran mahasiswa
    }
  },
  mounted() {
    this.startCamera()
  },
  methods: {
    startCamera() {
      navigator.mediaDevices
        .getUserMedia({ video: true })
        .then((stream) => {
          this.$refs.videoElement.srcObject = stream
        })
        .catch((error) => {
          this.message = '❌ Kamera tidak bisa diakses, periksa izin browser.'
          console.error(error)
        })
    },
    captureImage() {
      const video = this.$refs.videoElement
      const canvas = document.createElement('canvas')
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      const ctx = canvas.getContext('2d')
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

      canvas.toBlob((blob) => {
        this.sendImage(blob)
      }, 'image/png')
    },
    async sendImage(imageBlob) {
      const formData = new FormData()
      formData.append('image', imageBlob, 'scan.png')
      formData.append('purpose', this.purpose)

      try {
        const response = await fetch('http://localhost:5000/api/scan', {
          method: 'POST',
          body: formData,
        })

        const result = await response.json()
        console.log('✅ API Response:', result)
        this.message = result.message

        // 🔥 Jika wajah dikenali, tampilkan data di pop-up
        if (result.status === 'success') {
          this.attendanceData = {
            name: result.name,
            nim: result.nim,
            purpose: result.purpose,
            arrival_time: result.arrival_time,
          }
        } else {
          this.attendanceData = null
        }
      } catch (error) {
        console.error('❌ Error mengirim scan:', error)
        this.message = '❌ Error dalam proses scan wajah.'
        this.attendanceData = null
      }
    },
    closeModal() {
      this.attendanceData = null // 🔥 Tutup pop-up setelah klik "OK"
    },
  },
}
</script>

<style>
/* 🔥 Style untuk Pop-up */
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}
.modal-content {
  background: white;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}
button {
  margin-top: 10px;
  padding: 8px 16px;
  border: none;
  background: #28a745;
  color: white;
  cursor: pointer;
}
button:hover {
  background: #218838;
}
</style>
