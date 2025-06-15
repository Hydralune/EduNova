<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();

const handleLogout = () => {
  auth.logout();
};
</script>

<template>
  <div id="app">
    <header>
      <nav>
        <router-link to="/" class="brand">EduNova</router-link>
        <div class="nav-links">
          <template v-if="auth.isAuthenticated">
            <router-link to="/dashboard">Dashboard</router-link>
            <a @click="handleLogout" class="nav-link logout-link">Logout</a>
          </template>
          <template v-else>
            <router-link to="/login">Login</router-link>
            <router-link to="/register">Register</router-link>
          </template>
        </div>
      </nav>
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>

<style>
/* Global styles from previous step are fine, just refining nav */
body {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  color: #2c3e50;
  margin: 0;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

header {
  background: #fff;
  border-bottom: 1px solid #eaecef;
  padding: 0 2rem;
}

nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  height: 60px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

nav a:hover {
  background-color: #f0f0f0;
}

nav a.router-link-exact-active {
  color: #42b983;
}

.brand {
  font-size: 1.5rem;
}

.nav-links a {
  margin-left: 1rem;
}

.logout-link {
  cursor: pointer;
}

main {
  flex: 1;
  padding: 2rem;
}
</style>
