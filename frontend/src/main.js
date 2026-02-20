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
  currentRecommendIndex: 0,  // 新增：推荐菜品的当前批次索引
  selectedIngredients: [],
  currentTab: 'random-tab', // 当前活跃的选项卡
  isRecommending: false, // 标记当前是否在显示推荐结果
}

// ============================================================================
// DOM 元素缓存
// ============================================================================

let elements = {}

function cacheElements() {
  elements = {
    app: document.getElementById('app'),
    categoryFilter: document.getElementById('category-filter'),
    difficultyFilter: document.getElementById('difficulty-filter'),
    randomBtn: document.getElementById('random-btn'),
    recommendBtn: document.getElementById('recommend-btn'),
    dishesGrid: document.getElementById('dishes-grid'),
    loadingSpinner: document.getElementById('loading-spinner'),
    modal: document.getElementById('modal'),
    modalBackdrop: document.getElementById('modal-backdrop'),
    modalClose: document.getElementById('modal-close'),
    modalTitle: document.getElementById('modal-title'),
    modalBody: document.getElementById('modal-body'),
    pagination: document.getElementById('pagination'),
    ingredientInput: document.getElementById('ingredient-input'),
    ingredientAddBtn: document.getElementById('ingredient-add-btn'),
    ingredientsList: document.getElementById('ingredients-list'),
    tabButtons: document.querySelectorAll('.tab-button'),
    tabPanels: document.querySelectorAll('.tab-panel'),
  }
}

// ============================================================================
// 初始化应用
// ============================================================================

export async function initApp() {
  console.log('🚀 初始化 SearchMenu 应用')
  
  cacheElements()
  
  // 先绑定事件，确保无论后端是否可用，UI 都可交互
  bindEvents()
  
  // 检查后端连接
  try {
    const health = await dishesAPI.checkHealth()
    console.log('✅ 后端服务连接成功', health)
  } catch (error) {
    console.error('❌ 后端服务连接失败', error)
    showNotification('❌ 无法连接到后端服务，请确认后端已启动', 'error')
    // 不 return，继续初始化流程以保证 UI 可用
  }
  
  // 获取元数据（失败时在 loadMetadata 内部处理）
  await loadMetadata()
  
  console.log('✅ 应用初始化完成')
}

// ============================================================================
// 数据加载
// ============================================================================

async function loadMetadata() {
  showLoadingSpinner(true)
  state.isLoading = true
  
  // 分别加载元数据和分类，互不影响
  try {
    const metadata = await dishesAPI.getMetadata()
    state.totalDishes = metadata.total_dishes
  } catch (error) {
    console.error('加载元数据失败:', error)
  }
  
  try {
    const categories = await dishesAPI.getCategories()
    state.categories = categories.categories || []
    updateCategoryFilter()
  } catch (error) {
    console.error('加载分类失败:', error)
    showNotification('⚠️ 加载分类失败，请检查后端服务', 'error')
  }
  
  state.isLoading = false
  showLoadingSpinner(false)
}

async function loadDishes(resetPage = true) {
  // 如果当前正在显示推荐结果，跳过常规搜索（避免覆盖推荐）
  if (state.isRecommending) return
  
  try {
    showLoadingSpinner(true)
    state.isLoading = true
    
    if (resetPage) {
      state.currentPage = 0
    }
    
    const filters = {
      q: state.searchQuery,
      category: state.selectedCategory,
      difficulty: state.selectedDifficulty,
      skip: state.currentPage * state.pageSize,
      limit: state.pageSize
    }
    
    const response = await dishesAPI.searchDishes(filters)
    state.dishes = response.dishes
    state.totalDishes = response.total
    
    renderDishes()
    updatePagination()
  } catch (error) {
    console.error('加载菜品失败:', error)
    showNotification('加载菜品失败，请检查网络', 'error')
  } finally {
    state.isLoading = false
    showLoadingSpinner(false)
  }
}

async function loadRandomDish() {
  try {
    showLoadingSpinner(true)
    
    const filters = {
      category: state.selectedCategory || undefined,
      min_difficulty: state.selectedDifficulty ? parseInt(state.selectedDifficulty) : undefined,
      max_difficulty: state.selectedDifficulty ? parseInt(state.selectedDifficulty) : undefined,
    }
    
    // 移除未定义的属性
    Object.keys(filters).forEach(key => 
      filters[key] === undefined && delete filters[key]
    )
    
    const dish = await dishesAPI.getRandomDish(filters)
    showDishDetail(dish.id)
    showNotification('✨ 为您推荐了一道菜，请查看详情', 'success')
  } catch (error) {
    console.error('加载随机菜品失败:', error)
    showNotification('加载随机菜品失败', 'error')
  } finally {
    showLoadingSpinner(false)
  }
}

async function loadRecommendedDishes() {
  if (state.selectedIngredients.length === 0) {
    showNotification('请先添加食材', 'error')
    return
  }
  
  try {
    showLoadingSpinner(true)
    state.isRecommending = true
    
    // 后端最多返回100条，由前端控制每次显示1-6条
    const response = await dishesAPI.recommendDishes(
      state.selectedIngredients,
      100,
      state.selectedCategory || undefined  // 支持分类过滤
    )
    
    // 后端返回的是直接的数组
    state.recommendedDishes = Array.isArray(response) ? response : (response.recommendations || response || [])
    
    if (state.recommendedDishes.length === 0) {
      showNotification('未找到包含这些食材的菜品', 'error')
      state.dishes = []
      renderDishes()
    } else {
      showNotification(`找到 ${state.recommendedDishes.length} 道包含这些食材的菜品`, 'success')
      // 显示第一页（1-6个）
      state.currentRecommendIndex = 0
      displayRecommendationPage()
    }
  } catch (error) {
    console.error('加载推荐菜品失败:', error)
    showNotification('加载推荐菜品失败：' + error.message, 'error')
    state.isRecommending = false
  } finally {
    showLoadingSpinner(false)
  }
}

function displayRecommendationPage(pageNum = 0) {
  // 每页显示1-6个菜品，根据屏幕宽度响应式
  // 手机端（<640px）: 1个
  // 平板端（640-1024px）: 3个  
  // 桌面端（>1024px）: 6个
  const screenWidth = window.innerWidth
  let pageSize
  if (screenWidth < 640) {
    pageSize = 1
  } else if (screenWidth < 1024) {
    pageSize = 3
  } else {
    pageSize = 6
  }
  
  const startIdx = pageNum * pageSize
  const batch = state.recommendedDishes.slice(
    startIdx,
    startIdx + pageSize
  )
  
  state.dishes = batch
  state.currentRecommendIndex = pageNum
  renderDishes()
  updateRecommendationPagination(pageSize)
}

function updateRecommendationPagination(pageSize = 6) {
  const totalPages = Math.ceil(state.recommendedDishes.length / pageSize)
  
  if (state.recommendedDishes.length === 0) {
    elements.pagination.innerHTML = ''
    return
  }
  
  if (totalPages <= 1) {
    elements.pagination.innerHTML = `<span class="pagination-info">共 ${state.recommendedDishes.length} 道菜品</span>`
    return
  }
  
  let html = `
    <button type="button" class="pagination-button" id="prev-rec-btn" ${state.currentRecommendIndex === 0 ? 'disabled' : ''}>
      ← 上一页
    </button>
  `
  
  html += `<span class="pagination-info">第 ${state.currentRecommendIndex + 1} / ${totalPages} 页</span>`
  
  html += `
    <button type="button" class="pagination-button" id="next-rec-btn" ${state.currentRecommendIndex >= totalPages - 1 ? 'disabled' : ''}>
      下一页 →
    </button>
  `
  
  elements.pagination.innerHTML = html
  
  document.getElementById('prev-rec-btn')?.addEventListener('click', () => displayRecommendationPage(state.currentRecommendIndex - 1))
  document.getElementById('next-rec-btn')?.addEventListener('click', () => displayRecommendationPage(state.currentRecommendIndex + 1))
}

// ============================================================================
// 渲染函数
// ============================================================================

function renderDishes() {
  if (state.dishes.length === 0) {
    elements.dishesGrid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: #8b7355;">� 选择分类、难度或使用推荐功能来浏览菜品</div>'
    return
  }
  
  const html = state.dishes.map(dish => {
    // 兼容两种格式：searchDishes 返回 id，recommendDishes 返回 dish_id
    const dishId = dish.id || dish.dish_id
    return `
    <div class="dish-card" data-dish-id="${dishId}">
      <div class="dish-card-header">
        <div class="dish-name">${escapeHtml(dish.name)}</div>
        <div class="dish-meta">
          <span class="dish-badge">${escapeHtml(dish.category)}</span>
          <span class="dish-difficulty">${'⭐'.repeat(dish.difficulty)}</span>
        </div>
      </div>
    </div>
  `
  }).join('')
  
  elements.dishesGrid.innerHTML = html
}

function updateCategoryFilter() {
  const categories = state.categories || []
  const options = categories.map(cat => 
    `<option value="${escapeHtml(cat)}">${escapeHtml(cat)}</option>`
  ).join('')
  
  elements.categoryFilter.innerHTML = '<option value="">📂 所有分类</option>' + options
}

function updatePagination() {
  const totalPages = Math.ceil(state.totalDishes / state.pageSize)
  if (totalPages <= 1) {
    elements.pagination.innerHTML = ''
    return
  }
  
  let html = `
    <button type="button" class="pagination-button" id="prev-btn" ${state.currentPage === 0 ? 'disabled' : ''}>
      ← 上一页
    </button>
  `
  
  html += `<span class="pagination-info">第 ${state.currentPage + 1} / ${totalPages} 页</span>`
  
  html += `
    <button type="button" class="pagination-button" id="next-btn" ${state.currentPage >= totalPages - 1 ? 'disabled' : ''}>
      下一页 →
    </button>
  `
  
  elements.pagination.innerHTML = html
  
  document.getElementById('prev-btn')?.addEventListener('click', () => prevPage())
  document.getElementById('next-btn')?.addEventListener('click', () => nextPage())
}

function renderIngredients() {
  const html = state.selectedIngredients.map(ing => `
    <div class="ingredient-tag" data-ingredient="${escapeHtml(ing)}">
      ${escapeHtml(ing)}
      <button type="button" class="remove-ing-btn">×</button>
    </div>
  `).join('')
  
  elements.ingredientsList.innerHTML = html
}

// ============================================================================
// 模态框 / 菜品详情显示
// ============================================================================

async function showDishDetail(dishId) {
  try {
    showLoadingSpinner(true)
    const response = await dishesAPI.getDishDetail(dishId)
    const dish = response.dish || response
    showDishModal(dish)
  } catch (error) {
    console.error('获取菜品详情失败:', error)
    showNotification('获取菜品详情失败', 'error')
  } finally {
    showLoadingSpinner(false)
  }
}

function showDishModal(dish) {
  elements.modalTitle.textContent = dish.name
  
  let ingredientsHtml = dish.ingredients && dish.ingredients.length > 0
    ? dish.ingredients.map(ing => {
        // 后端返回的是 ingredient_name, quantity, is_main, is_optional
        const name = ing.ingredient_name || ing.name || ''
        let qty = ing.quantity || ''
        
        // 过滤掉"適量"等无效量词，只显示实际的量值
        const invalidQuantities = ['適量', '适量', '少量', '多少', '根据需要', '']
        if (invalidQuantities.includes(qty)) {
          qty = ''
        }
        
        const isMain = ing.is_main ? '（主食材）' : ''
        const qtyDisplay = qty ? ` ${escapeHtml(qty)}` : ''
        return `<div class="ingredient-item">${escapeHtml(name)}${qtyDisplay} ${isMain}</div>`
      }).join('')
    : '<div style="color: #8b7355;">暂无食材信息</div>'
  
  // 过滤掉占位符步骤（只有默认文本的步骤）
  let validSteps = []
  if (dish.steps && dish.steps.length > 0) {
    validSteps = dish.steps.filter(step => {
      const desc = typeof step === 'object' ? step.description : step
      const placeholders = ['按照食材特性进行烹制', '按照菜谱制作']
      return desc && !placeholders.includes(desc)
    })
  }
  
  let stepsHtml = validSteps.length > 0
    ? validSteps.map((step, idx) => `
        <div class="step-item">
          <span class="step-number">第 ${idx + 1} 步：</span>
          ${escapeHtml(typeof step === 'object' ? step.description : step)}
        </div>
      `).join('')
    : '<div style="color: #8b7355;">暂无详细步骤信息（来自HowToCook的菜谱可能需要查看原文档）</div>'
  
  const modalContent = `
    <div class="modal-section">
      <div style="display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem;">
        <span class="dish-badge">${escapeHtml(dish.category)}</span>
        <span style="color: #c99a63; font-weight: 600;">${'⭐'.repeat(dish.difficulty)}</span>
      </div>
      <p style="color: #8b7355; font-size: 0.95rem;">${escapeHtml(dish.description || '来自HowToCook的菜谱')}</p>
    </div>
    
    <div class="modal-section">
      <h3>📋 食材清单</h3>
      <div class="ingredients-display">
        ${ingredientsHtml}
      </div>
    </div>
    
    <div class="modal-section">
      <h3>👨‍🍳 烹饪步骤</h3>
      <div class="steps-display">
        ${stepsHtml}
      </div>
    </div>
  `
  
  elements.modalBody.innerHTML = modalContent
  showModal()
}

function showModal() {
  elements.modal.classList.remove('hidden')
  elements.modalBackdrop.classList.remove('hidden')
}

function hideModal() {
  elements.modal.classList.add('hidden')
  elements.modalBackdrop.classList.add('hidden')
}

// ============================================================================
// 事件绑定
// ============================================================================

function bindEvents() {
  // 分类过滤
  elements.categoryFilter.addEventListener('change', (e) => {
    state.selectedCategory = e.target.value
    loadDishes()
  })
  
  // 难度过滤
  elements.difficultyFilter.addEventListener('change', (e) => {
    state.selectedDifficulty = e.target.value
    loadDishes()
  })
  
  // 随机推荐
  elements.randomBtn.addEventListener('click', () => {
    loadRandomDish()
  })
  
  // 食材推荐
  elements.ingredientAddBtn.addEventListener('click', () => {
    const value = elements.ingredientInput.value.trim()
    if (value) {
      addIngredient(value)
      elements.ingredientInput.value = ''
    }
  })
  
  elements.ingredientInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      const value = e.target.value.trim()
      if (value) {
        addIngredient(value)
        elements.ingredientInput.value = ''
      }
    }
  })
  
  // 食材标签删除按钮事件委托
  elements.ingredientsList.addEventListener('click', (e) => {
    if (e.target.classList.contains('remove-ing-btn')) {
      const tag = e.target.closest('.ingredient-tag')
      const ingredient = tag.dataset.ingredient
      removeIngredient(ingredient)
    }
  })
  
  elements.recommendBtn.addEventListener('click', () => {
    loadRecommendedDishes()
  })
  
  // 菜品卡片点击事件委托
  elements.dishesGrid.addEventListener('click', (e) => {
    const card = e.target.closest('.dish-card')
    if (card) {
      const dishId = card.dataset.dishId
      showDishDetail(dishId)
    }
  })
  
  // 选项卡切换
  elements.tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const tabName = btn.dataset.tab
      switchTab(tabName)
    })
  })
  
  // 模态框关闭
  elements.modalClose.addEventListener('click', hideModal)
  elements.modalBackdrop.addEventListener('click', hideModal)
}

function addIngredient(ingredient) {
  if (!state.selectedIngredients.includes(ingredient)) {
    state.selectedIngredients.push(ingredient)
    renderIngredients()
  }
}

export function removeIngredient(ingredient) {
  state.selectedIngredients = state.selectedIngredients.filter(i => i !== ingredient)
  renderIngredients()
}

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

function switchTab(tabName) {
  // 更新按钮状态
  elements.tabButtons.forEach(btn => {
    if (btn.dataset.tab === tabName) {
      btn.classList.add('active')
    } else {
      btn.classList.remove('active')
    }
  })
  
  // 更新面板显示 - 查找所有带有tab-panel类的div
  const allPanels = document.querySelectorAll('.tab-panel')
  allPanels.forEach(panel => {
    if (panel.id === tabName) {
      panel.classList.add('active')
    } else {
      panel.classList.remove('active')
    }
  })
  
  state.currentTab = tabName
}

// ============================================================================
// 工具函数
// ============================================================================

function showLoadingSpinner(show) {
  if (show) {
    elements.loadingSpinner.classList.remove('hidden')
  } else {
    elements.loadingSpinner.classList.add('hidden')
  }
}

function showNotification(message, type = 'success') {
  const notification = document.createElement('div')
  notification.className = `notification ${type}`
  notification.textContent = message
  document.body.appendChild(notification)
  
  setTimeout(() => {
    notification.remove()
  }, 3000)
}

function escapeHtml(text) {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}

// ============================================================================
// 导出API供HTML调用
// ============================================================================

export const app = {
  initApp,
  showDishDetail,
  removeIngredient,
  displayRecommendationPage,
}

// ============================================================================
// 应用入口
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
  initApp()
})

// 全局访问
window.app = app
