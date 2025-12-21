// api/index.js
import request from '@/utils/request'

export const login = (data) => request.post('/login', data)
export const register = (data) => request.post('/register', data)
export const getSelfInfo = () => request.get('/user')
export const getUserInfo = (id) => request.get(`/user/${id}`)
export const updateUserInfo = (data) => request.post('/update_user', data)
export const uploadFile = (data) => request.post('/upload', data, {
  headers: { 'Content-Type': 'multipart/form-data' }
})

export const getProducts = () => request.get('/get_products')
export const getProductDetail = (id) => request.get(`/product/${id}`)
export const createProduct = (data) => request.post('/create_product', data)
export const modifyProduct = (data) => request.post('/modify_product', data)
export const deleteProduct = (id) => request.delete(`/delete_product/${id}`)
export const buyProduct = (id) => request.post(`/buy_product/${id}`)
export const getCategories = () => request.get('/get_categories')

export const getOrders = () => request.get('/get_orders')
export const getFavoriteFolders = () =>
  request.get('/favorite_folders')

export const createFavoriteFolder = (data) =>
  request.post('/create_favorite_folder', data)

export const modifyFavoriteFolder = (data) =>
  request.post('/modify_favorite_folder', data)

export const deleteFavoriteFolder = (id) =>
  request.delete(`/delete_favorite_folder/${id}`)

export const favoriteProduct = (data) =>
  request.post('/favorite_product', data)
/*
data = {
  product_id,
  folder_id
}
*/

export const getFavorites = (folderId) =>
  request.get(`/get_favorites/${folderId}`)

export const deleteFavorite = (folderId, productId) =>
  request.delete(`/delete_favorite/${folderId}/product/${productId}`)

export const publishComment = (data) => request.post('/publish_comment', data)
export const getComments = (id) => request.get(`/get_comments/${id}`)
export const deleteComment = (id) => request.delete(`/delete_comment/${id}`)
export const sendMsg = (data) => request.post('/send_msg', data)
export const getMsgs = () => request.get('/get_msgs')