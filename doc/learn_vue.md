### ref

使用数据需要.value

```js
import { ref } from 'vue'

const count = ref(0)

// use 

count.value++
```


### toRefs, toRef

```js
const t2 = ref ({
    a: 1,
    b: 2
})

let { a, b } = toRefs(t2.value)
let a = toRef(t2.value, 'a')
```

### computed

``` js
let content = computed(() => {
        return ph.value + a.value
})
```


### watch

``` js
watch(refobj, (newValue, oldValue) => {
    
}) // => stopfn   stopfn()  =>  stop watch

// 监视对象

watch(refobj, (newValue, oldValue) => {  // or (value) 大多数情况不改old
    // 不改对象 newValue === oldValue    
}, {
    deep: true,
    immediate: true // => 立即执行
})

// 监视对象里的类型,若需要监视内部需要deep
watch(() => refobj.a, (newValue, oldValue) => { 
})


// 监视多个
watch([() => refobj.a, () => refobj.b], (newValue, oldValue) => {
    
})
```

### watchEffect

``` js

watchEffect(() => {
    //直接使用，自动判断watch哪个
})
```

### props

``` js
// father

<template>
    <son :name="name" :age="age"></son>
</template>


// son

let args = defineProps({
    name: String,
    age: Number
})

args.name



```


### v-for

``` html

<template>
    <ul>
        <li v-for="item in list" :key="item.id">   
            {{ item.name }} 
        </li>
    </ul>
</template>

```


### hooks

``` js

export default useSum = () => {
    const sum = ref(0)
    const add = () => {
        sum.value++
    }
    return {
        sum,
        add
    }
}

// use

const { sum, add } = useSum()

```

### 钩子

``` js
setup

onMounted

onBeforeMount

onUpdated

onBeforeUpdate

onUnmounted

onBeforeUnmount

```

### router


``` html
<!-- replace 不会留下历史记录 -->
<router-link replace to="/login" active-class="active">login</router-link>
<router-link :to="{ path: '/login' }">login</router-link>
<router-link :to="{ name : 'login' }">login</router-link>

<router-view></router-view>

```

##### 嵌套

``` js

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            component: HomeView,
            children: [
                name: 'login',
                component: Login
                path: 'login' //子级不需要/
            ]
        }
    ]
})

```

##### 传参

``` html
<!-- 第一种模板字符串 -->
<router-link :to="`/news/detail?id=${id}&name=${name}`">login</router-link>

<!-- 第二种 对象 -->
<router-link :to="{ 
    path: '/news/detail', 
    query: { 
        id, 
        name 
        } 
    }">login</router-link>

```
##### 接收

``` js

import { useRoute } from 'vue-router'

const route = useRoute()

const id = route.query.id
const name = route.query.name

// 或者解构

const { id, name } = toRefs(route.query)
```


##### params  参数

``` js
// :to = "`/news/detail/${id}/${name}`"

// :to = "{
//     name: 'detail', //不能用path
//     params: {
//         id : id,
//         name : name
//     }
// }"
routes : [
    {
        path: '/news/detail/:id/:name', //占位
        component: Detail
    }
]

// use

const route = useRoute()
const id = route.params.id
const name = route.params.name

```

##### props

``` js
// 路由收到的params参数会自动变成props，传给路由组件
routes : [
    {
        path: '/news/detail/:id/:name', //占位
        component: Detail,
        props: true
    }
]

// -----------------------------------------------

routes : [
    {
        path: '/news/detail', 
        component: Detail,
        props(route) {
            return route.query
        }
    }
]
// -----------------------------------------------



// use
defineProps(['id', 'name'])
```

##### 编程式导航

``` js

import { useRouter } from 'vue-router'

const router = useRouter()

router.push('/login')
router.replace('/login')

router.push({
    name: 'login',
    query: {
        id: 1
    }
})

```


### pinia

v-model.number: 将v-model尽可能转换成number

``` js
// store
import { defineStore } from 'pinia'

export const useCounterStore = defineStore('counter', {
    state() {
        return {
            count: 0
        }
    },
    // 放置动作
    actions: {
        increment() {
            this.count++
        }
    },
    getters: {
        doubleCount(state) {
            return state.count * 2
        },
        doubleCount() {
            return this.count * 2
        }

    }
})

// 组合式
export const useCounterStore = defineStore('counter', () => {
    const count = ref(0)
    function increment() {
        count.value++
    }
    const doubleCount = computed(() => count.value * 2)
    return { count, increment }
})

// use
import { useCounterStore } from '../stores/counter'
const store = useCounterStore()

store.count
```

##### 修改数据

``` js
import { useCounterStore } from '../stores/counter'
const store = useCounterStore()

// 1
store.count++
// 2
store.$patch({
    count: store.count + 1,
    doubleCount: store.doubleCount + 1
})
// 3
store.increment();
```

##### storeToRefs

``` js

import { storeToRefs } from 'pinia'

const store = useCounterStore()
const { count } = storeToRefs(store)

```

##### $subscribe

可以用Json.stringify使对象变成字符串

``` js

store.$subscribe((mutation, state) => {
    
})

```


### 组件通信

##### props

父子双向通信

``` html
<Child :count="count" :send-msg="getmsg"></Child>
```

``` js
// father
let count = ref(0)
function getmsg(msg) {
    console.log(msg)
    count.value++
}
// child
let props = defineProps(['count', 'sendmsg'])

function sendmsg(msg) {
    props.sendmsg(msg)
}

```

##### 自定义事件

子传父

``` html
<Child @sendmsg="getmsg"></Child>
```

``` js
// son
//声明事件

const emit = defineEmits(['send-msg'])
emit('send-msg', 'hello')

```


##### v-model

``` html
<input :value="count" @input="count = $event.target.value">
等价于
<input v-model="count">

<UI :model-value="count" @update:model-value="count = $event"></UI> // 自定义事件 组件 $event是传递的值

// 子
<input :value="modelValue" @input="$emit('update:modelValue', $event.target.value)"> //dom 节点， 原生事件，$event是dom event
```

``` js

//son
defineProps(['modelValue'])
const emit = defineEmits(['update:modelValue'])

```

##### provide/inject

祖孙通信

``` js
// father

// 向后代提供数据
provide('count', count) // 不要.value

// son

const count = inject('count')
```


### 插槽

##### 默认插槽

``` html
// father

<Child>
    <span>hello</span>
</Child>

// son
<slot></slot>
```

##### 命名插槽
``` html
// father

<Child>
    <template v-slot:title>
        <span>hello</span>
    </template>
</Child>

// son
<slot name="title"></slot>
```

##### 作用域插槽

<Child>
    <template v-slot:title="props">
        <span>hello</span>
    </template>
</Child>

// son
<slot name="title" :props="props"></slot>
```