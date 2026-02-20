import './styles.css'
import { dishesAPI } from './api.js'

// ============================================================================
// 全局状态管理
// ============================================================================

const state = {
  dishes: [],
  categories: [],
  currentDish: null,
  currentPage: 0,
  pageSize: 10,
  totalDishes: 0,
  isLoading: false,
  searchQuery: '',
  selectedCategory: '',
  selectedDifficulty: '',
  recommendedDishes: [],
  selectedIngredients: [],
  showModal: false,
  modalContent: null,
}

// ============================================================================
// DOM 元素缓存
// ============================================================================

let elements = {}

function cacheElements() {
  elements = {
    app: document.getElementById('app'),
    searchInput: document.getElementById('search-input'),
    categoryFilter: document.getElementById('category-filter'),
    difficultyFilter: document.getElementById('difficulty-filter'),
    searchBtn: document.getElementById('search-btn'),
    randomBtn: document.getElementById('random-btn'),
    recommendBtn: document.getElementById('recommend-btn'),
    dishesGrid: document.getElementById('dishes-grid'),
    loadingSpinner: document.getElementById('loading-spinner'),
    modal: document.getElementById('modal'),
    modalBackdrop: document.getElementById('modal-backdrop'),
    modalClose: document.getElementById('modal-close'),
    pagination: document.getElementById('pagination'),
    ingredientInput: document.getElementById('ingredient-input'),
    ingredientAddBtn: document.getElementById('ingredient-add-btn'),
    ingredientsList: document.getElementById('ingredients-list'),
  }
}

// ============================================================================
// 初始化应用
// ============================================================================

export async function initApp() {
  console.log('🚀 初始化 SearchMenu 应用')
  
  cacheElements()
  
  // 检查后端连接
  try {
    const health = await dishesAPI.checkHealth()
    console.log('✅ 后端服务连接成功', health)
  } catch (error) {
    console.error('❌ 后端服务连接失败', error)
    showNotification('❌ 无法连接到后端服务，请确保 API 服务已启动', 'error')
    return
  }
  
  // 获取元数据
  await loadMetadata()
  
  // 绑定事件
  bindEvents()
  
  // 加载初始菜品列表
  await loadDishes()
  
  console.log('✅ 应用初始化完成')
}

// ============================================================================
// 数据加载
// ============================================================================

async function loadMetadata() {
  try {
    state.isLoading = true
    const metadata = await dishesAPI.getMetadata()
    state.totalDishes = metadata.total_dishes
    
    const categories = await dishesAPI.getCategories()
    state.categories = categories.categories
    
    updateCategoryFilter()
  } catch (error) {
    console.error('加载元数据失败:', error)
  } finally {
    state.isLoading = false
  }
}

async function loadDishes(resetPage = true) {
  try {
    state.isLoading = true
    showLoadingSpinner(true)
    
    if (resetPage) state.currentPage = 0
    
    const filters = {
      skip: state.currentPage * state.pageSize,
      limit: state.pageSize,
    }
    
    if (state.searchQuery) filters.q = state.searchQuery
    if (state.selectedCategory) filters.category = state.selectedCategory
    if (state.selectedDifficulty) filters.difficulty = parseInt(state.selectedDifficulty)
    
    const dishes = await dishesAPI.searchDishes(filters)
    state.dishes = dishes
    
    renderDishes()
    updatePagination()
  } catch (error) {
    console.error('加载菜品失败:', error)
    showNotification('加载菜品失败，请重试', 'error')
  } finally {
    state.isLoading = false
    showLoadingSpinner(false)
  }
}

async function loadRandomDish() {
  try {
    state.isLoading = true
    showLoadingSpinner(true)
    
    const options = {}
    if (state.selectedCategory) options.category = state.selectedCategory
    if (state.selectedDifficulty) options.difficulty = parseInt(state.selectedDifficulty)
    
    const dish = await dishesAPI.getRandomDish(options)
    showDishModal(dish)
  } catch (error) {
    console.error('获取随机菜品失败:', error)
    showNotification('获取随机菜品失败，请重试', 'error')
  } finally {
    state.isLoading = false
    showLoadingSpinner(false)
  }
}

async function loadRecommendedDishes() {
  if (state.selectedIngredients.length === 0) {
    showNotification('请至少输入一个食材', 'warning')
    return
  }
  
  try {
    state.isLoading = true
    showLoadingSpinner(true)
    
    const dishes = await dishesAPI.recommendDishes(state.selectedIngredients, 20)
    state.recommendedDishes = dishes
    
    showRecommendationModal()
  } catch (error) {
    console.error('推荐菜品失败:', error)
    showNotification('推荐菜品失败，请重试', 'error')
  } finally {
    state.isLoading = false
    showLoadingSpinner(false)
  }
}

// ============================================================================
// 渲染函数
// ============================================================================

function renderDishes() {
  const html = state.dishes.map(dish => `
    <div class="card" onclick="window.app.showDishDetail('${dish.id}')">
      <div class="mb-3">
        <h3 class="text-lg font-bold text-gray-800">${dish.name}</h3>
        <div class="flex gap-2 mt-2">
          <span class="tag tag-primary">${dish.category}</span>
          <span class="tag">${'⭐'.repeat(dish.difficulty)}${' ☆'.repeat(5 - dish.difficulty)}</span>
        </div>
      </div>
      <p class="text-sm text-gray-600 mb-3 line-clamp-2">${dish.description}</p>
      <p class="text-xs text-gray-500">⏱️ ${dish.estimated_time}</p>
    </div>
  `).join('')
  
  elements.dishesGrid.innerHTML = html || '<p class="col-span-full text-center text-gray-400">未找到菜品</p>'
}

function updateCategoryFilter() {
  const options = [
    '<option value="">所有分类</option>',
    ...state.categories.map(cat => `<option value="${cat}">${cat}</option>`)
  ].join('')
  elements.categoryFilter.innerHTML = options
}

function updatePagination() {
  const totalPages = Math.ceil(state.totalDishes / state.pageSize)
  const pageButtons = []
  
  // 上一页
  pageButtons.push(`
    <button class="btn ${state.currentPage === 0 ? 'opacity-50 cursor-not-allowed' : 'btn-outline'}" 
            ${state.currentPage === 0 ? 'disabled' : 'onclick="window.app.prevPage()"'}>
      ← 上一页
    </button>
  `)
  
  // 页码
  for (let i = 0; i < Math.min(totalPages, 5); i++) {
    const pageNum = i
    pageButtons.push(`
      <button class="btn ${state.currentPage === pageNum ? 'btn-primary' : 'btn-outline'}" 
              onclick="window.app.goToPage(${pageNum})">
        ${pageNum + 1}
      </button>
    `)
  }
  
  // 下一页
  pageButtons.push(`
    <button class="btn ${state.currentPage >= totalPages - 1 ? 'opacity-50 cursor-not-allowed' : 'btn-outline'}" 
            ${state.currentPage >= totalPages - 1 ? 'disabled' : 'onclick="window.app.nextPage()"'}>
      下一页 →
    </button>
  `)
  
  elements.pagination.innerHTML = pageButtons.join('')
}

// ============================================================================
// 模态框和详情
// ============================================================================

async function showDishDetail(dishId) {
  try {
    state.isLoading = true
    showLoadingSpinner(true)
    
    const dish = await dishesAPI.getDishDetail(dishId)
    showDishModal(dish)
  } catch (error) {
    console.error('加载菜品详情失败:', error)
    showNotification('加载菜品详情失败', 'error')
  } finally {
    state.isLoading = false
    showLoadingSpinner(false)
  }
}

function showDishModal(dish) {
  const ingredientsHtml = (dish.ingredients || [])
    .map(ing => `
      <div class="flex justify-between items-center p-2 bg-gray-50 rounded">
        <span>${ing.ingredient_name} <span class="text-xs text-gray-500">${ing.is_main ? '(主料)' : ''}</span></span>
        <span class="font-medium">${ing.quantity}</span>
      </div>
    `)
    .join('')
  
  const stepsHtml = (dish.steps || [])
    .map((step, idx) => `
      <div class="flex gap-4 p-3 bg-gray-50 rounded">
        <div class="flex-shrink-0">
          <span class="inline-flex items-center justify-center h-8 w-8 rounded-full bg-primary text-white font-bold">
            ${idx + 1}
          </span>
        </div>
        <div class="flex-1">
          <p class="text-sm">${step.description}</p>
          <p class="text-xs text-gray-500 mt-1">⏱️ ${step.duration}</p>
        </div>
      </div>
    `)
    .join('')
  
  const html = `
    <div class="w-full max-w-2xl p-6">
      <div class="flex justify-between items-start mb-4">
        <div>
          <h2 class="text-3xl font-bold text-gray-800">${dish.name}</h2>
          <div class="flex gap-2 mt-2">
            <span class="tag tag-primary">${dish.category}</span>
            <span class="tag">难度: ${'⭐'.repeat(dish.difficulty)}</span>
          </div>
        </div>
      </div>
      
      <p class="text-gray-600 mb-4">${dish.description}</p>
      <p class="text-sm text-gray-500 mb-6">⏱️ 估计时间: ${dish.estimated_time}</p>
      
      <div class="mb-6">
        <h3 class="text-xl font-bold text-gray-800 mb-3">📋 食材</h3>
        <div class="space-y-2">
          ${ingredientsHtml}
        </div>
      </div>
      
      <div class="mb-6">
        <h3 class="text-xl font-bold text-gray-800 mb-3">👨‍🍳 烹饪步骤</h3>
        <div class="space-y-3">
          ${stepsHtml}
        </div>
      </div>
    </div>
  `
  
  showModal(html)
}

function showRecommendationModal() {
  const dishesHtml = state.recommendedDishes
    .map(dish => `
      <div class="flex items-center justify-between p-3 bg-gray-50 rounded">
        <div class="flex-1">
          <h4 class="font-bold text-gray-800">${dish.name}</h4>
          <p class="text-sm text-gray-500">${dish.category} · 难度: ${dish.difficulty}⭐</p>
          <p class="text-xs text-gray-400 mt-1">匹配食材: ${dish.matched_ingredients.join(', ')}</p>
        </div>
        <span class="text-lg font-bold text-primary">${Math.round(dish.match_score)}%</span>
      </div>
    `)
    .join('')
  
  const html = `
    <div class="w-full max-w-2xl p-6">
      <h2 class="text-2xl font-bold text-gray-800 mb-2">🎯 食材推荐结果</h2>
      <p class="text-gray-600 mb-4">根据您输入的食材: ${state.selectedIngredients.join(', ')}</p>
      
      <div class="space-y-3 max-h-[60vh] overflow-y-auto">
        ${dishesHtml || '<p class="text-gray-400">未找到匹配的菜品</p>'}
      </div>
    </div>
  `
  
  showModal(html)
}

function showModal(content) {
  elements.modal.innerHTML = `
    <div class="flex justify-end mb-4 border-b pb-4">
      <button id="modal-close" class="text-gray-500 hover:text-gray-700 text-2xl">✕</button>
    </div>
    ${content}
  `
  
  elements.modal.classList.remove('hidden')
  elements.modalBackdrop.classList.remove('hidden')
  
  document.getElementById('modal-close').addEventListener('click', hideModal)
}

function hideModal() {
  elements.modal.classList.add('hidden')
  elements.modalBackdrop.classList.add('hidden')
}

// ============================================================================
// 事件处理
// ============================================================================

function bindEvents() {
  elements.searchBtn.addEventListener('click', () => loadDishes())
  elements.randomBtn.addEventListener('click', loadRandomDish)
  elements.recommendBtn.addEventListener('click', loadRecommendedDishes)
  
  elements.searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') loadDishes()
  })
  
  elements.categoryFilter.addEventListener('change', () => {
    state.selectedCategory = elements.categoryFilter.value
    loadDishes()
  })
  
  elements.difficultyFilter.addEventListener('change', () => {
    state.selectedDifficulty = elements.difficultyFilter.value
    loadDishes()
  })
  
  // 食材推荐
  elements.ingredientAddBtn.addEventListener('click', addIngredient)
  elements.ingredientInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') addIngredient()
  })
  
  // 模态框背景点击关闭
  elements.modalBackdrop.addEventListener('click', hideModal)
}

function addIngredient() {
  const ingredient = elements.ingredientInput.value.trim()
  if (ingredient && !state.selectedIngredients.includes(ingredient)) {
    state.selectedIngredients.push(ingredient)
    state.searchQuery = ingredient
    elements.searchInput.value = ingredient
    elements.ingredientInput.value = ''
    renderIngredients()
  }
}

function removeIngredient(ingredient) {
  state.selectedIngredients = state.selectedIngredients.filter(i => i !== ingredient)
  renderIngredients()
}

function renderIngredients() {
  elements.ingredientsList.innerHTML = state.selectedIngredients
    .map(ing => `
      <span class="tag tag-primary">
        ${ing}
        <button onclick="window.app.removeIngredient('${ing}')" class="ml-2 font-bold">✕</button>
      </span>
    `)
    .join('')
}

// ============================================================================
// 辅助函数
// ============================================================================

function showLoadingSpinner(show) {
  if (elements.loadingSpinner) {
    elements.loadingSpinner.classList.toggle('hidden', !show)
  }
}

function showNotification(message, type = 'info') {
  const colors = {
    info: 'bg-blue-100 text-blue-800',
    success: 'bg-green-100 text-green-800',
    error: 'bg-red-100 text-red-800',
    warning: 'bg-yellow-100 text-yellow-800',
  }
  
  const notification = document.createElement('div')
  notification.className = `fixed top-4 right-4 p-4 rounded-lg ${colors[type]} z-50 animate-pulse`
  notification.textContent = message
  
  document.body.appendChild(notification)
  
  setTimeout(() => {
    notification.remove()
  }, 3000)
}

// ============================================================================
// 分页
// ============================================================================

function prevPage() {
  if (state.currentPage > 0) {
    state.currentPage--
    loadDishes(false)
  }
}

function nextPage() {
  const totalPages = Math.ceil(state.totalDishes / state.pageSize)
  if (state.currentPage < totalPages - 1) {
    state.currentPage++
    loadDishes(false)
  }
}

function goToPage(page) {
  state.currentPage = page
  loadDishes(false)
}

// ============================================================================
// 导出应用 API
// ============================================================================

export const app = {
  showDishDetail,
  removeIngredient,
  prevPage,
  nextPage,
  goToPage,
}

// 使应用 API 全局可访问
if (typeof window !== 'undefined') {
  window.app = app
}

// 初始化应用
initApp()
