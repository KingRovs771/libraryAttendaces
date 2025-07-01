<template>
  <div class="register">
    <h2>📸 Registrasi Mahasiswa</h2>

    <form @submit.prevent="submitRegistration">
      <label>🧑 Nama:</label>
      <input type="text" v-model="name" required />

      <label>🎓 NIM:</label>
      <input type="text" v-model="nim" required />

      <video ref="videoElement" autoplay></video>
      <button type="button" @click="captureImage">✅ Ambil Gambar</button>

      <div v-if="previewImage" class="image-preview">
        <h3>🔍 Preview Gambar</h3>
        <img :src="previewImage" alt="Preview Image" />
      </div>

      <button type="submit">📤 Daftar</button>
    </form>

    <p v-if="message">{{ message }}</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      name: '',
      nim: '',
      message: '',
      previewImage: null,
      imageBlob: null,
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
        this.imageBlob = blob
        this.previewImage = URL.createObjectURL(blob) // 🔍 Preview gambar sebelum dikirim
      }, 'image/png')
    },
    async submitRegistration() {
      const formData = new FormData()
      formData.append('name', this.name)
      formData.append('nim', this.nim)
      formData.append('image', this.imageBlob, 'capture.png')

      try {
        const response = await fetch('http://localhost:5000/api/register', {
          method: 'POST',
          body: formData,
        })

        const result = await response.json()
        this.message = result.message
      } catch (error) {
        console.error('❌ Error Registrasi:', error)
      }
    },
  },
}
</script>
