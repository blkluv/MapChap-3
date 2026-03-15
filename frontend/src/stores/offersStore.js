import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiService } from '../services/api.js'

export const useOffersStore = defineStore('offers', () => {
  // State
  const offers = ref([])
  const selectedCategory = ref('all')
  const searchQuery = ref('')
  const userLocation = ref(null)
  const mapBounds = ref(null)
  const selectedOffer = ref(null)
  const isLoading = ref(false)

  // Categories
  const categories = ref([
    { id: 'food', name: 'Food & Restaurants', icon: '🍕', color: '#FF6B6B' },
    { id: 'shopping', name: 'Shopping', icon: '🛍️', color: '#4ECDC4' },
    { id: 'beauty', name: 'Beauty Salons', icon: '💄', color: '#FFD166' },
    { id: 'services', name: 'Services', icon: '🔧', color: '#06D6A0' },
    { id: 'medical', name: 'Medical', icon: '⚕️', color: '#118AB2' },
    { id: 'furniture', name: 'Furniture & Decor', icon: '🛋️', color: '#073B4C' },
    { id: 'pharmacy', name: 'Pharmacies', icon: '💊', color: '#EF476F' },
    { id: 'entertainment', name: 'Entertainment', icon: '🎭', color: '#7209B7' },
    { id: 'education', name: 'Education', icon: '📚', color: '#F72585' },
    { id: 'auto', name: 'Auto Services', icon: '🚗', color: '#4361EE' },
    { id: 'hotel', name: 'Hotels', icon: '🏨', color: '#4CC9F0' }
  ])

  // Computed
  const filteredOffers = computed(() => {
    let result = offers.value

    if (selectedCategory.value && selectedCategory.value !== 'all') {
      result = result.filter(o => o.category === selectedCategory.value)
    }

    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      result = result.filter(o =>
        o.title?.toLowerCase().includes(query) ||
        o.description?.toLowerCase().includes(query) ||
        o.address?.toLowerCase().includes(query)
      )
    }

    return result
  })

  // Actions
  const fetchOffers = async (params = {}) => {
    isLoading.value = true
    try {
      const result = await apiService.getOffers(params)
      offers.value = result.offers || []
      console.log(`📍 Loaded ${offers.value.length} offers`)
    } catch (error) {
      console.log('Fetch offers error:', error)
      // Mock data - All locations within 1 mile of MLK Home in Atlanta
      offers.value = [
        {
          id: '1',
          title: 'Sweet Auburn Market',
          description: 'Fresh local produce and Southern specialties',
          category: 'food',
          address: '209 Edgewood Ave SE, Atlanta, GA',
          phone: '(404) 555-0123',
          coordinates: { type: 'Point', coordinates: [-84.3782, 33.7545] },
          views: 1245,
          likes: 89,
          rating: 4.8,
          status: 'active',
          effectUrl: 'https://www.tiktok.com/effect/123456'
        },
        {
          id: '2',
          title: 'Auburn Avenue Rib Shack',
          description: 'Authentic Atlanta BBQ since 1985',
          category: 'food',
          address: '305 Auburn Ave NE, Atlanta, GA',
          phone: '(404) 555-0234',
          coordinates: { type: 'Point', coordinates: [-84.3745, 33.7555] },
          views: 856,
          likes: 67,
          rating: 4.9,
          status: 'active',
          effectUrl: 'https://www.tiktok.com/effect/789012'
        },
        {
          id: '3',
          title: 'Sweet Auburn Curb Market',
          description: 'Historic market with local vendors and food hall',
          category: 'shopping',
          address: '209 Edgewood Ave SE, Atlanta, GA',
          phone: '(404) 555-0345',
          coordinates: { type: 'Point', coordinates: [-84.3785, 33.7542] },
          views: 2100,
          likes: 156,
          rating: 4.7,
          status: 'active',
          effectUrl: 'https://www.tiktok.com/effect/901234'
        },
        {
          id: '4',
          title: 'Ponce City Market',
          description: 'Historic mixed-use development with a food hall, rooftop amusement park, and stunning city views',
          category: 'shopping',
          address: '675 Ponce de Leon Ave NE, Atlanta, GA',
          phone: '(404) 555-0456',
          coordinates: { type: 'Point', coordinates: [-84.3658, 33.7724] },
          views: 8900,
          likes: 1240,
          rating: 4.8,
          status: 'active',
          effectUrl: 'https://www.tiktok.com/effect/345678'
      },
     {
         id: '5',
         title: 'Krog Street Market',
         description: 'Vibrant food hall in a restored 1920s warehouse with artisan vendors and Beltline access',
         category: 'food',
         address: '99 Krog St NE, Atlanta, GA',
         phone: '(404) 555-0567',
         coordinates: { type: 'Point', coordinates: [-84.3642, 33.7510] },
         views: 5600,
         likes: 890,
         rating: 4.7,
         status: 'active',
        effectUrl: 'https://www.tiktok.com/effect/567890'
     }
      ]
    } finally {
      isLoading.value = false
    }
  }

  const setSelectedCategory = (category) => {
    selectedCategory.value = category
    console.log(`🏷️ Category selected: ${category}`)
  }

  const setSearchQuery = (query) => {
    searchQuery.value = query
  }

  const searchByAddress = (address) => {
    console.log(`🔍 Searching: ${address}`)
    // TODO: Implement geocoding search
  }

  const setUserLocation = (location) => {
    userLocation.value = location
    console.log('📍 User location updated')
  }

  const setMapBounds = (bounds) => {
    mapBounds.value = bounds
  }

  const setSelectedOffer = (offer) => {
    selectedOffer.value = offer
  }

  // New method to get effect URL for an offer
  const getEffectUrl = (offerId) => {
    const offer = offers.value.find(o => o.id === offerId)
    return offer?.effectUrl || null
  }

  return {
    offers,
    selectedCategory,
    searchQuery,
    userLocation,
    mapBounds,
    selectedOffer,
    isLoading,
    categories,
    filteredOffers,
    fetchOffers,
    setSelectedCategory,
    setSearchQuery,
    searchByAddress,
    setUserLocation,
    setMapBounds,
    setSelectedOffer,
    getEffectUrl
  }
})
