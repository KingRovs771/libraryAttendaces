<template>
  <div class="attendance">
    <h2>📌 Absensi Mahasiswa</h2>

    <form @submit.prevent="submitAttendance">
      <label>📸 Foto Wajah:</label>
      <input type="file" @change="handleFileUpload" accept="image/*" required />
      <label>📝 Keperluan:</label>
      <input v-model="purpose" type="text" required />
      <button type="submit">✅ Absen</button>
    </form>

    <p v-if="message">{{ message }}</p>

    <div v-if="studentData" class="student-info">
      <h3>🎓 Data Mahasiswa:</h3>
      <p><strong>Nama:</strong> {{ studentData.name }}</p>
      <p><strong>NIM:</strong> {{ studentData.nim }}</p>
      <p><strong>Waktu Kehadiran:</strong> {{ studentData.arrival_time }}</p>
      <p><strong>Keperluan:</strong> {{ studentData.purpose }}</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      file: null,
      purpose: '',
      message: '',
      studentData: null, // 🔍 Tambahkan variabel untuk menyimpan data mahasiswa
    }
  },
  methods: {
    handleFileUpload(event) {
      this.file = event.target.files[0]
    },
    async submitAttendance() {
      const formData = new FormData()
      formData.append('image', this.file)
      formData.append('purpose', this.purpose)

      try {
        const response = await axios.post('http://localhost:5000/api/absen', formData)
        const result = response.data

        this.message = result.message

        // 🔍 Jika wajah dikenali, simpan data mahasiswa dan tampilkan
        if (result.status === 'success') {
          this.studentData = {
            name: result.name,
            nim: result.nim,
            arrival_time: result.arrival_time,
            purpose: result.purpose,
          }
        } else {
          this.studentData = null // 🔥 Reset jika tidak dikenali
        }
      } catch (error) {
        console.error('❌ Error Absensi:', error)
        this.message = '❌ Error: Absensi gagal.'
        this.studentData = null
      }
    },
  },
}
</script>
