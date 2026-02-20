import axios from 'axios'

// 生产部署时通过 VITE_API_BASE_URL 环境变量注入后端地址
// 本地开发时默认使用 http://localhost:8000
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error.message)
    return Promise.reject(error)
  }
)

export const dishesAPI = {
  /**
   * 健康检查
   */
  async checkHealth() {
    return api.get('/health')
  },

  /**
   * 获取随机菜品
   * @param {Object} options - 可选参数
   * @param {string} options.category - 分类过滤
   * @param {number} options.difficulty - 难度过滤 (1-5)
   */
  async getRandomDish(options = {}) {
    return api.get('/api/v1/dishes/random', { params: options })
  },

  /**
   * 搜索菜品
   * @param {Object} filters - 过滤条件
   * @param {string} filters.q - 搜索关键词
   * @param {string} filters.category - 分类
   * @param {number} filters.difficulty - 难度
   * @param {number} filters.skip - 跳过数量（分页）
   * @param {number} filters.limit - 返回数量
   */
  async searchDishes(filters = {}) {
    return api.get('/api/v1/dishes/search', { params: filters })
  },

  /**
   * 获取菜品分类列表
   */
  async getCategories() {
    return api.get('/api/v1/categories')
  },

  /**
   * 获取系统元数据
   */
  async getMetadata() {
    return api.get('/api/v1/metadata')
  },

  /**
   * 获取菜品详细信息
   * @param {string} dishId - 菜品 ID
   */
  async getDishDetail(dishId) {
    return api.get(`/api/v1/dishes/${dishId}`)
  },

  /**
   * 基于食材推荐菜品
   * @param {string[]} ingredients - 食材列表
   * @param {number} limit - 返回数量
   * @param {string} category - 可选，分类过滤
   */
  async recommendDishes(ingredients, limit = 10, category = null) {
    const params = category ? { category } : {}
    return api.post('/api/v1/dishes/recommend', {
      ingredients,
      limit
    }, { params })
  }
}

export default api
