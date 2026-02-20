import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiService } from '../services/api.js'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const isLoading = ref(false)
  const telegramWebApp = ref(null)

  // Computed
  const isAuthenticated = computed(() => !!user.value)
  const isBusinessOwner = computed(() => user.value?.role === 'business_owner')
  const isVerified = computed(() => user.value?.is_verified === true)

  // Actions
  const initTelegramAuth = async () => {
    console.log('🔐 Initializing Telegram Auth...')
    
    // Сначала пробуем загрузить из localStorage
    try {
      const cached = localStorage.getItem('mapchap_user')
      if (cached) {
        const cachedUser = JSON.parse(cached)
        if (cachedUser?.telegram_id) {
          user.value = cachedUser
          console.log('📦 Loaded user from cache:', cachedUser.first_name)
          // Пытаемся обновить данные с сервера в фоне
          fetchUser()
          return
        }
      }
    } catch (e) {}
    
    if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
      telegramWebApp.value = window.Telegram.WebApp
      const tg = window.Telegram.WebApp
      
      tg.ready()
      tg.expand()
      
      const initData = tg.initDataUnsafe?.user
      
      if (initData) {
        console.log('👤 Telegram user found:', initData.first_name)
        
        try {
          isLoading.value = true
          const result = await apiService.telegramAuth({
            id: initData.id,
            first_name: initData.first_name,
            last_name: initData.last_name || '',
            username: initData.username || '',
            photo_url: initData.photo_url || '',
            language_code: initData.language_code || 'ru'
          })
          
          if (result.success && result.user) {
            user.value = result.user
            // Сохраняем в localStorage
            try {
              localStorage.setItem('mapchap_user', JSON.stringify(result.user))
            } catch (e) {}
            console.log('✅ Auth successful')
          }
        } catch (error) {
          console.error('❌ Auth error:', error)
          // Заглушка для разработки
          user.value = {
            id: String(Date.now()),
            telegram_id: initData.id,
            first_name: initData.first_name,
            last_name: initData.last_name || '',
            username: initData.username || '',
            photo_url: initData.photo_url || '',
            role: 'user',
            is_verified: false,
            favorite_categories: [],
            favorites: [],
            notifications_enabled: true
          }
        } finally {
          isLoading.value = false
        }
      } else {
        console.log('⚠️ No Telegram user data, using demo mode')
        // Демо-режим для тестирования
        user.value = {
          id: 'demo-user',
          telegram_id: 123456789,
          first_name: 'Демо',
          last_name: 'Пользователь',
          username: 'demo_user',
          photo_url: '',
          role: 'user',
          is_verified: false,
          favorite_categories: [],
          favorites: [],
          notifications_enabled: true
        }
      }
    } else {
      console.log('⚠️ Not in Telegram, using demo mode')
      // Демо-режим для разработки вне Telegram
      user.value = {
        id: 'demo-user',
        telegram_id: 123456789,
        first_name: 'Демо',
        last_name: 'Пользователь',
        username: 'demo_user',
        photo_url: '',
        role: 'user',
        is_verified: false,
        favorite_categories: [],
        favorites: [],
        notifications_enabled: true
      }
    }
  }

  const registerAsBusiness = async (businessData) => {
    if (!user.value) return
    
    user.value = {
      ...user.value,
      role: 'business_owner',
      is_verified: true,
      company_name: businessData.companyName,
      inn: businessData.inn || null,
      verification_type: businessData.verificationType
    }
    
    // Сохраняем в localStorage для persistence
    try {
      localStorage.setItem('mapchap_user', JSON.stringify(user.value))
    } catch (e) {
      console.log('⚠️ Could not save to localStorage')
    }
    
    console.log('✅ User registered as business:', user.value.company_name)
  }

  const fetchUser = async () => {
    if (!user.value?.telegram_id) return
    
    try {
      const userData = await apiService.getUser(user.value.telegram_id)
      if (userData) {
        user.value = userData
        // Сохраняем в localStorage
        try {
          localStorage.setItem('mapchap_user', JSON.stringify(userData))
        } catch (e) {}
        console.log('✅ User data refreshed')
      }
    } catch (error) {
      console.log('⚠️ Could not fetch user, keeping local data')
      // Пробуем загрузить из localStorage
      try {
        const cached = localStorage.getItem('mapchap_user')
        if (cached) {
          user.value = JSON.parse(cached)
          console.log('📦 Loaded user from cache')
        }
      } catch (e) {}
    }
  }

  const updateUser = async (updates) => {
    if (!user.value) return
    
    try {
      await apiService.updateUser(user.value.telegram_id, updates)
      user.value = { ...user.value, ...updates }
    } catch (error) {
      console.error('Update user error:', error)
      // Обновляем локально в любом случае
      user.value = { ...user.value, ...updates }
    }
  }

  const logout = () => {
    user.value = null
    console.log('🚪 User logged out')
  }

  return {
    user,
    isLoading,
    telegramWebApp,
    isAuthenticated,
    isBusinessOwner,
    isVerified,
    initTelegramAuth,
    registerAsBusiness,
    fetchUser,
    updateUser,
    logout
  }
})
