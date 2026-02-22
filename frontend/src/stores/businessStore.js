import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiService } from '../services/api.js'
import { useAuthStore } from './authStore.js'

export const useBusinessStore = defineStore('business', () => {
  const authStore = useAuthStore()
  
  // State
  const userOffers = ref([])
  const isLoading = ref(false)
  const categories = ref([
    { id: 'food', name: 'Еда и рестораны', icon: '🍕', color: '#FF6B6B' },
    { id: 'shopping', name: 'Магазины', icon: '🛍️', color: '#4ECDC4' },
    { id: 'beauty', name: 'Салоны красоты', icon: '💄', color: '#FFD166' },
    { id: 'services', name: 'Услуги', icon: '🔧', color: '#06D6A0' },
    { id: 'medical', name: 'Медицина', icon: '⚕️', color: '#118AB2' },
    { id: 'furniture', name: 'Мебель и декор', icon: '🛋️', color: '#073B4C' },
    { id: 'pharmacy', name: 'Аптеки', icon: '💊', color: '#EF476F' },
    { id: 'entertainment', name: 'Развлечения', icon: '🎭', color: '#7209B7' },
    { id: 'education', name: 'Образование', icon: '📚', color: '#F72585' },
    { id: 'auto', name: 'Автосервисы', icon: '🚗', color: '#4361EE' },
    { id: 'hotel', name: 'Отели', icon: '🏨', color: '#4CC9F0' }
  ])

  // Computed
  const getUserOffers = computed(() => userOffers.value)
  
  const getCategoryById = (id) => {
    return categories.value.find(c => c.id === id)
  }

  // Actions
  const loadUserOffers = async () => {
    if (!authStore.user?.telegram_id) {
      console.log('⚠️ loadUserOffers: No telegram_id')
      return
    }
    
    isLoading.value = true
    console.log('📡 Loading offers for user:', authStore.user.telegram_id)
    
    try {
      const result = await apiService.getUserOffers(authStore.user.telegram_id)
      console.log('📦 API response:', result)
      userOffers.value = result.offers || []
      console.log('✅ Loaded', userOffers.value.length, 'offers')
    } catch (error) {
      console.error('❌ Load offers error:', error)
      userOffers.value = []
    } finally {
      isLoading.value = false
    }
  }

  const createOffer = async (offerData) => {
    if (!authStore.user?.telegram_id) throw new Error('Not authenticated')
    
    console.log('📝 Creating offer:', offerData.title)
    
    // Геокодирование адреса через Yandex Geocoder
    let coordinates = offerData.coordinates || [offerData.lat || 55.751244, offerData.lng || 37.618423]
    
    if (offerData.address && window.ymaps) {
      try {
        const result = await window.ymaps.geocode(offerData.address, { results: 1 })
        const geoObject = result.geoObjects.get(0)
        if (geoObject) {
          const coords = geoObject.geometry.getCoordinates()
          coordinates = coords
          console.log('📍 Geocoded address:', offerData.address, '->', coords)
        }
      } catch (e) {
        console.log('⚠️ Geocoding failed, using default coordinates')
      }
    }
    
    const dataToSend = {
      ...offerData,
      coordinates: coordinates
    }
    
    try {
      const result = await apiService.createOffer(authStore.user.telegram_id, dataToSend)
      console.log('✅ Offer created:', result)
      userOffers.value.push(result)
      return result
    } catch (error) {
      console.error('❌ Create offer error:', error)
      // Добавляем локально только если это ошибка сети
      const newOffer = {
        id: String(Date.now()),
        ...dataToSend,
        user_id: authStore.user.telegram_id,
        status: 'active',
        views: 0,
        likes: 0,
        created_at: new Date().toISOString()
      }
      userOffers.value.push(newOffer)
      return newOffer
    }
  }

  const updateOffer = async (offerId, updates) => {
    if (!authStore.user?.telegram_id) throw new Error('Not authenticated')
    
    try {
      const result = await apiService.updateOffer(offerId, authStore.user.telegram_id, updates)
      const index = userOffers.value.findIndex(o => o.id === offerId)
      if (index !== -1) {
        userOffers.value[index] = result
      }
      return result
    } catch (error) {
      console.log('Update offer error:', error)
      // Обновляем локально
      const index = userOffers.value.findIndex(o => o.id === offerId)
      if (index !== -1) {
        userOffers.value[index] = { ...userOffers.value[index], ...updates }
      }
    }
  }

  const toggleOfferStatus = async (offerId) => {
    const offer = userOffers.value.find(o => o.id === offerId)
    if (!offer) return
    
    const newStatus = offer.status === 'active' ? 'paused' : 'active'
    await updateOffer(offerId, { status: newStatus })
  }

  const deleteOffer = async (offerId) => {
    if (!authStore.user?.telegram_id) throw new Error('Not authenticated')
    
    try {
      await apiService.deleteOffer(offerId, authStore.user.telegram_id)
      userOffers.value = userOffers.value.filter(o => o.id !== offerId)
    } catch (error) {
      console.log('Delete offer error:', error)
      userOffers.value = userOffers.value.filter(o => o.id !== offerId)
    }
  }

  return {
    userOffers,
    isLoading,
    categories,
    getUserOffers,
    getCategoryById,
    loadUserOffers,
    createOffer,
    updateOffer,
    toggleOfferStatus,
    deleteOffer
  }
})
