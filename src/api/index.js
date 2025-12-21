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
export const getCategories = () => request.get('/get_categories')

// 订单与收藏
export const getOrders = () => request.get('/get_orders')
export const getFavoriteFolders = () =>
  request.get('/api/favorite_folders')

// 创建收藏夹
export const createFavoriteFolder = (data) =>
  request.post('/api/create_favorite_folder', data)

// 修改收藏夹名称
export const modifyFavoriteFolder = (data) =>
  request.post('/api/modify_favorite_folder', data)

// 删除收藏夹
export const deleteFavoriteFolder = (id) =>
  request.delete(`/api/delete_favorite_folder/${id}`)

// 收藏商品到收藏夹
export const favoriteProduct = (data) =>
  request.post('/api/favorite_product', data)
/*
data = {
  product_id,
  folder_id
}
*/

// 获取某个收藏夹下的收藏
export const getFavorites = (folderId) =>
  request.get(`/api/get_favorites/${folderId}`)

export const deleteFavorite = (folderId, productId) =>
  request.delete(`/api/delete_favorite/${folderId}/product/${productId}`)

// 评论与消息
export const publishComment = (data) => request.post('/publish_comment', data)
export const getComments = (id) => request.get(`/get_comments/${id}`)
export const deleteComment = (id) => request.delete(`/delete_comment/${id}`)
export const sendMsg = (data) => request.post('/send_msg', data)
export const getMsgs = () => request.get('/get_msgs')