import {ref} from 'vue'

export const useSum = () => {
    const sum = ref(0)
    const add = (num) => {
        sum.value += num
    }
    return {
        sum,
        add
    }
}