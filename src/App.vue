<script setup>
import { watchEffect } from 'vue';
import { useUserTokenStore } from './stores/auth';

const userTokenStore = useUserTokenStore();

watchEffect(() => {
  const localToken = localStorage.getItem('token');
  if (localToken) {
    userTokenStore.token = localToken;
  }
})

</script>

<template>
  <router-view></router-view>
</template>

<style>
html, body {
  margin: 0;
  padding: 0;
}

</style>
