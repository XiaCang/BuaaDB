import { ref, computed } from 'vue'
import { defineStore } from 'pinia'


export const useUserTokenStore = defineStore('userToken', () => {
    const token = ref('')
    const isLogin = computed(() => token.value !== '')
    return { token, isLogin }
})