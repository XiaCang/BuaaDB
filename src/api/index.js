// api/index.js
import request from '@/utils/request'

// 用户相关
export const login = (data) => request.post('/login', data)
export const register = (data) => request.post('/register', data)
export const getSelfInfo = () => request.get('/user')
export const getUserInfo = (id) => request.get(`/user/${id}`)
export const updateUserInfo = (data) => request.post('/update_user', data)
export const uploadFile = (data) => request.post('/upload', data, {
  headers: { 'Content-Type': 'multipart/form-data' }
})

// 商品相关
export const getProducts = () => request.get('/get_products')
export const getProductDetail = (id) => request.get(`/product/${id}`)
export const createProduct = (data) => request.post('/create_product', data)
export const modifyProduct = (data) => request.post('/modify_product', data) // 建议后端该接口带上ID
export const deleteProduct = (id) => request.delete(`/delete_product/${id}`)
export const buyProduct = (id) => request.post(`/buy_product/${id}`)

// 订单与收藏
export const getOrders = () => request.get('/get_orders')
export const favoriteProduct = (id) => request.post(`/favorite_product/${id}`)
export const getFavorites = () => request.get('/get_favorites')
export const deleteFavorite = (id) => request.delete(`/delete_favorite/${id}`)

// 评论与消息
export const publishComment = (data) => request.post('/publish_comment', data)
export const getComments = (id) => request.get(`/get_comments/${id}`)
export const deleteComment = (id) => request.delete(`/delete_comment/${id}`)
export const sendMsg = (data) => request.post('/send_msg', data)
export const getMsgs = () => request.get('/get_msgs')