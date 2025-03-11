<template>
  <div class="container">
    <div class="login-container">
      <h2 class="login-title">Login</h2>
      <div class="form-group">
        <label
          for="username"
          class="form-label"
          >Username</label
        >
        <input
          type="email"
          id="username"
          placeholder="Enter your username"
          class="form-control"
          v-model="email"
          required
        />
      </div>
      <div class="form-group">
        <label
          for="password"
          class="form-label"
          >Password</label
        >
        <input
          type="password"
          id="password"
          placeholder="Enter your password"
          class="form-control"
          v-model="password"
          required
        />
      </div>
      <button
        type="button"
        id="login-button"
        @click="login"
        class="btn-primary"
      >
        Login
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { getAuth, signInWithEmailAndPassword, onAuthStateChanged } from 'firebase/auth'

const email = ref('')
const password = ref('')

const login = () => {
  signInWithEmailAndPassword(getAuth(), email.value, password.value)
    .then((userCredential) => {
      const user = userCredential.user
      console.log('User is signed in:', user.id)
      window.location.hash = '/control'
    })
    .catch((err) => {
      alert(err.message)
    })
}
</script>

<style lang="scss" scoped>
.google-blue {
  color: #4285f4;
}
.google-red {
  color: #db4437;
}
.google-yellow {
  color: #f4b400;
}
.google-green {
  color: #0f9d58;
}

.container {
  font-family: 'Roboto', sans-serif;
  background-color: #f1f3f4; /* Light gray background */
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  margin: 0;
  color: black;
}
.login-container {
  background-color: #ffffff; /* White container */
  padding: 2rem;
  border-radius: 0.5rem; /* Rounded corners */
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075); /* Slight shadow */
  width: 100%;
  max-width: 28rem; /* Maximum width */
}
.google-logo {
  display: flex;
  justify-content: center;
  margin-bottom: 1.5rem;
}
.google-logo span {
  font-size: 2.5rem;
  font-weight: bold;
}
.google-blue {
  color: #4285f4;
}
.google-red {
  color: #db4437;
}
.google-yellow {
  color: #f4b400;
}
.google-green {
  color: #0f9d58;
}
.login-title {
  font-size: 1.5rem;
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 1rem;
  text-align: center;
}
.form-group {
  margin-bottom: 1rem;
}
.form-label {
  display: block;
  font-size: 0.875rem;
  color: #495057;
  font-weight: bold;
  margin-bottom: 0.5rem;
}
.form-control {
  width: 100%;
  padding: 0.75rem;
  font-size: 1rem;
  border: 0.0625rem solid #ced4da; /* Light border */
  border-radius: 0.25rem; /* Rounded corners */
  transition:
    border-color 0.15s ease-in-out,
    shadow-box 0.15s ease-in-out;
}
.form-control:focus {
  outline: none;
  border-color: #4299e1; /* Blue focus border */
  box-shadow: 0 0 0 0.2rem rgba(66, 153, 225, 0.25); /* Blue focus shadow */
}
.btn-primary {
  background-color: #4299e1; /* Blue button */
  color: #fff;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  width: 100%;
  transition: background-color 0.15s ease-in-out;
}
.btn-primary:hover {
  background-color: #3182ce; /* Darker blue on hover */
}
</style>
