<template>
  <div class="analytics-page">
    <!-- Header -->
    <div class="analytics-header">
      <button class="back-btn" @click="$router.back()">
        <i class="fas fa-arrow-left"></i>
      </button>
      <h1>Аналитика</h1>
      <div class="period-selector">
        <button 
          v-for="p in periods" 
          :key="p.value"
          :class="['period-btn', { active: period === p.value }]"
          @click="period = p.value; loadData()"
        >
          {{ p.label }}
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <i class="fas fa-spinner fa-spin"></i>
      <span>Загрузка аналитики...</span>
    </div>

    <!-- Dashboard Content -->
    <div v-else-if="dashboard" class="analytics-content">
      <!-- Summary Cards -->
      <div class="summary-cards">
        <div class="summary-card views">
          <div class="card-icon">
            <i class="fas fa-eye"></i>
          </div>
          <div class="card-content">
            <span class="card-value">{{ formatNumber(dashboard.summary.total_views) }}</span>
            <span class="card-label">Просмотров</span>
            <span :class="['trend', dashboard.summary.trend_direction]">
              <i :class="trendIcon(dashboard.summary.trend_direction)"></i>
              {{ Math.abs(dashboard.summary.trend_percent) }}%
            </span>
          </div>
        </div>

        <div class="summary-card visitors">
          <div class="card-icon">
            <i class="fas fa-users"></i>
          </div>
          <div class="card-content">
            <span class="card-value">{{ formatNumber(dashboard.summary.unique_visitors) }}</span>
            <span class="card-label">Уникальных</span>
          </div>
        </div>

        <div class="summary-card favorites">
          <div class="card-icon">
            <i class="fas fa-heart"></i>
          </div>
          <div class="card-content">
            <span class="card-value">{{ dashboard.summary.total_favorites }}</span>
            <span class="card-label">В избранном</span>
          </div>
        </div>

        <div class="summary-card boosts">
          <div class="card-icon">
            <i class="fas fa-rocket"></i>
          </div>
          <div class="card-content">
            <span class="card-value">{{ dashboard.summary.active_boosts }}</span>
            <span class="card-label">Активных бустов</span>
          </div>
        </div>
      </div>

      <!-- Views Chart -->
      <div class="chart-section">
        <h3>Просмотры по дням</h3>
        <div class="chart-container">
          <div class="bar-chart">
            <div 
              v-for="(day, i) in dashboard.chart_data" 
              :key="i"
              class="bar-wrapper"
            >
              <div 
                class="bar" 
                :style="{ height: getBarHeight(day.views) + '%' }"
                :title="`${day.date}: ${day.views} просмотров`"
              >
                <span class="bar-value" v-if="day.views > 0">{{ day.views }}</span>
              </div>
              <span class="bar-label">{{ formatDate(day.date) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Recommendations -->
      <div v-if="dashboard.recommendations?.length" class="recommendations-section">
        <h3>Рекомендации</h3>
        <div class="recommendations-list">
          <div 
            v-for="(rec, i) in dashboard.recommendations" 
            :key="i"
            :class="['recommendation-card', rec.type, rec.priority]"
          >
            <div class="rec-icon">
              <i :class="getRecIcon(rec.type)"></i>
            </div>
            <div class="rec-content">
              <h4>{{ rec.title }}</h4>
              <p>{{ rec.text }}</p>
            </div>
            <button 
              v-if="rec.action === 'buy_boost'"
              class="rec-action"
              @click="goToBoost(rec.offer_ids)"
            >
              Буст
            </button>
          </div>
        </div>
      </div>

      <!-- Offers List -->
      <div class="offers-section">
        <h3>Ваши объявления</h3>
        <div class="offers-list">
          <div 
            v-for="offer in dashboard.offers" 
            :key="offer.id"
            class="offer-analytics-card"
            @click="viewOfferAnalytics(offer.id)"
          >
            <div class="offer-info">
              <h4>{{ offer.title }}</h4>
              <span class="offer-category">{{ getCategoryName(offer.category) }}</span>
            </div>
            <div class="offer-stats">
              <div class="stat">
                <i class="fas fa-eye"></i>
                <span>{{ offer.views }}</span>
              </div>
              <div v-if="offer.has_boost" class="boost-badge">
                <i class="fas fa-rocket"></i>
                <span>Буст</span>
              </div>
            </div>
            <i class="fas fa-chevron-right arrow"></i>
          </div>
        </div>
      </div>

      <!-- Top & Low Performers -->
      <div class="performers-section" v-if="dashboard.top_performers?.length">
        <div class="performers-block top">
          <h3><i class="fas fa-trophy"></i> Топ объявления</h3>
          <div class="performers-list">
            <div v-for="(offer, i) in dashboard.top_performers" :key="offer.id" class="performer-item">
              <span class="rank">{{ i + 1 }}</span>
              <span class="name">{{ offer.title }}</span>
              <span class="views">{{ offer.views }} <i class="fas fa-eye"></i></span>
            </div>
          </div>
        </div>

        <div class="performers-block low" v-if="dashboard.need_attention?.length">
          <h3><i class="fas fa-exclamation-triangle"></i> Требуют внимания</h3>
          <div class="performers-list">
            <div v-for="offer in dashboard.need_attention" :key="offer.id" class="performer-item">
              <span class="name">{{ offer.title }}</span>
              <span class="views low">{{ offer.views }} <i class="fas fa-eye"></i></span>
              <button class="boost-btn-small" @click.stop="goToBoost([offer.id])">
                <i class="fas fa-rocket"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Offer Detail Analytics Modal -->
    <div v-if="selectedOffer" class="offer-modal" @click.self="selectedOffer = null">
      <div class="modal-content">
        <button class="close-btn" @click="selectedOffer = null">
          <i class="fas fa-times"></i>
        </button>
        
        <h2>{{ selectedOffer.offer_title }}</h2>
        
        <div class="modal-summary">
          <div class="modal-stat">
            <span class="value">{{ selectedOffer.summary.total_views }}</span>
            <span class="label">Просмотров</span>
          </div>
          <div class="modal-stat">
            <span class="value">{{ selectedOffer.summary.unique_visitors }}</span>
            <span class="label">Уникальных</span>
          </div>
          <div class="modal-stat">
            <span class="value">{{ selectedOffer.summary.conversion_rate }}%</span>
            <span class="label">Конверсия</span>
          </div>
          <div class="modal-stat">
            <span class="value">{{ selectedOffer.summary.peak_hour }}</span>
            <span class="label">Пиковый час</span>
          </div>
        </div>

        <div class="modal-trend" :class="selectedOffer.summary.trend_direction">
          <i :class="trendIcon(selectedOffer.summary.trend_direction)"></i>
          {{ Math.abs(selectedOffer.summary.trend_percent) }}% по сравнению с прошлым периодом
        </div>

        <!-- Hour chart -->
        <div class="hour-chart">
          <h4>Активность по часам</h4>
          <div class="hours-grid">
            <div 
              v-for="hour in selectedOffer.charts.views_by_hour"
              :key="hour.hour"
              class="hour-bar"
              :style="{ opacity: getHourOpacity(hour.views) }"
              :title="`${hour.hour}: ${hour.views}`"
            >
              <span class="hour-label">{{ hour.hour.split(':')[0] }}</span>
            </div>
          </div>
        </div>

        <!-- Boost info -->
        <div v-if="selectedOffer.boost" class="boost-info active">
          <i class="fas fa-rocket"></i>
          <div>
            <strong>Буст активен</strong>
            <span>Осталось {{ selectedOffer.boost.days_left }} дней</span>
          </div>
        </div>
        <div v-else class="boost-info inactive">
          <i class="fas fa-rocket"></i>
          <div>
            <strong>Нет активного буста</strong>
            <span>Увеличьте просмотры в 3-5 раз</span>
          </div>
          <button @click="goToBoost([selectedOffer.offer_id]); selectedOffer = null">
            Активировать
          </button>
        </div>

        <!-- Recommendations -->
        <div class="modal-recommendations">
          <div 
            v-for="(rec, i) in selectedOffer.recommendations" 
            :key="i"
            :class="['rec-item', rec.type]"
          >
            <i :class="getRecIcon(rec.type)"></i>
            <span>{{ rec.text }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { apiService } from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const dashboard = ref(null)
const selectedOffer = ref(null)
const period = ref('30d')

const periods = [
  { value: '7d', label: '7 дней' },
  { value: '30d', label: '30 дней' },
  { value: '90d', label: '90 дней' }
]

const categories = {
  food: 'Еда',
  shopping: 'Магазины',
  grocery: 'Продукты',
  beauty: 'Красота',
  services: 'Услуги',
  medical: 'Медицина',
  pharmacy: 'Аптеки',
  fitness: 'Фитнес',
  entertainment: 'Развлечения',
  education: 'Образование',
  auto: 'Авто',
  hotel: 'Отели',
  furniture: 'Мебель'
}

const loadData = async () => {
  loading.value = true
  try {
    const response = await api.get(`/api/analytics/dashboard/${userStore.telegramId}?period=${period.value}`)
    dashboard.value = response.data
  } catch (error) {
    console.error('Error loading analytics:', error)
  } finally {
    loading.value = false
  }
}

const viewOfferAnalytics = async (offerId) => {
  try {
    const response = await api.get(`/api/analytics/offer/${offerId}?telegram_id=${userStore.telegramId}&period=${period.value}`)
    selectedOffer.value = response.data
  } catch (error) {
    console.error('Error loading offer analytics:', error)
  }
}

const formatNumber = (num) => {
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}

const getBarHeight = (views) => {
  if (!dashboard.value?.chart_data?.length) return 0
  const maxViews = Math.max(...dashboard.value.chart_data.map(d => d.views))
  return maxViews > 0 ? (views / maxViews * 100) : 0
}

const getHourOpacity = (views) => {
  if (!selectedOffer.value) return 0.2
  const maxViews = Math.max(...selectedOffer.value.charts.views_by_hour.map(h => h.views))
  return maxViews > 0 ? Math.max(0.2, views / maxViews) : 0.2
}

const trendIcon = (direction) => {
  switch (direction) {
    case 'up': return 'fas fa-arrow-up'
    case 'down': return 'fas fa-arrow-down'
    default: return 'fas fa-minus'
  }
}

const getRecIcon = (type) => {
  switch (type) {
    case 'boost': return 'fas fa-rocket'
    case 'content': return 'fas fa-edit'
    case 'engagement': return 'fas fa-heart'
    case 'alert': return 'fas fa-exclamation-triangle'
    case 'opportunity': return 'fas fa-lightbulb'
    case 'success': return 'fas fa-check-circle'
    default: return 'fas fa-info-circle'
  }
}

const getCategoryName = (cat) => categories[cat] || cat

const goToBoost = (offerIds) => {
  router.push({ name: 'boost', query: { offers: offerIds?.join(',') } })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.analytics-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
  padding: 16px;
  padding-bottom: 100px;
}

.analytics-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.back-btn {
  background: rgba(255,255,255,0.1);
  border: none;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  cursor: pointer;
}

.analytics-header h1 {
  flex: 1;
  color: white;
  font-size: 24px;
  margin: 0;
}

.period-selector {
  display: flex;
  gap: 8px;
}

.period-btn {
  background: rgba(255,255,255,0.1);
  border: none;
  color: rgba(255,255,255,0.6);
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.period-btn.active {
  background: #6366f1;
  color: white;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 50vh;
  color: rgba(255,255,255,0.6);
  gap: 12px;
}

.loading-state i {
  font-size: 32px;
}

/* Summary Cards */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.summary-card {
  background: rgba(255,255,255,0.05);
  border-radius: 16px;
  padding: 16px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.card-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.summary-card.views .card-icon { background: rgba(99, 102, 241, 0.2); color: #6366f1; }
.summary-card.visitors .card-icon { background: rgba(34, 197, 94, 0.2); color: #22c55e; }
.summary-card.favorites .card-icon { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
.summary-card.boosts .card-icon { background: rgba(249, 115, 22, 0.2); color: #f97316; }

.card-content {
  display: flex;
  flex-direction: column;
}

.card-value {
  color: white;
  font-size: 24px;
  font-weight: 700;
}

.card-label {
  color: rgba(255,255,255,0.5);
  font-size: 12px;
}

.trend {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
}

.trend.up { color: #22c55e; }
.trend.down { color: #ef4444; }
.trend.stable { color: rgba(255,255,255,0.5); }

/* Chart */
.chart-section {
  background: rgba(255,255,255,0.05);
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 24px;
}

.chart-section h3 {
  color: white;
  font-size: 16px;
  margin: 0 0 16px 0;
}

.bar-chart {
  display: flex;
  align-items: flex-end;
  gap: 4px;
  height: 150px;
  overflow-x: auto;
  padding-bottom: 24px;
}

.bar-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 30px;
  flex: 1;
}

.bar {
  width: 100%;
  background: linear-gradient(to top, #6366f1, #818cf8);
  border-radius: 4px 4px 0 0;
  min-height: 4px;
  position: relative;
  transition: height 0.3s;
}

.bar-value {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  color: white;
  font-size: 10px;
  white-space: nowrap;
}

.bar-label {
  color: rgba(255,255,255,0.4);
  font-size: 10px;
  margin-top: 8px;
  white-space: nowrap;
}

/* Recommendations */
.recommendations-section {
  margin-bottom: 24px;
}

.recommendations-section h3 {
  color: white;
  font-size: 16px;
  margin: 0 0 12px 0;
}

.recommendation-card {
  background: rgba(255,255,255,0.05);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
  border-left: 3px solid;
}

.recommendation-card.boost { border-color: #f97316; }
.recommendation-card.content { border-color: #6366f1; }
.recommendation-card.engagement { border-color: #ef4444; }
.recommendation-card.alert { border-color: #eab308; }
.recommendation-card.opportunity { border-color: #22c55e; }
.recommendation-card.success { border-color: #22c55e; }

.recommendation-card.high { background: rgba(239, 68, 68, 0.1); }

.rec-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255,255,255,0.1);
  color: white;
}

.rec-content {
  flex: 1;
}

.rec-content h4 {
  color: white;
  font-size: 14px;
  margin: 0 0 4px 0;
}

.rec-content p {
  color: rgba(255,255,255,0.6);
  font-size: 12px;
  margin: 0;
}

.rec-action {
  background: #f97316;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

/* Offers List */
.offers-section h3 {
  color: white;
  font-size: 16px;
  margin: 0 0 12px 0;
}

.offer-analytics-card {
  background: rgba(255,255,255,0.05);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: background 0.3s;
}

.offer-analytics-card:hover {
  background: rgba(255,255,255,0.08);
}

.offer-info {
  flex: 1;
}

.offer-info h4 {
  color: white;
  font-size: 14px;
  margin: 0 0 4px 0;
}

.offer-category {
  color: rgba(255,255,255,0.5);
  font-size: 12px;
}

.offer-stats {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat {
  display: flex;
  align-items: center;
  gap: 4px;
  color: rgba(255,255,255,0.7);
  font-size: 14px;
}

.boost-badge {
  background: rgba(249, 115, 22, 0.2);
  color: #f97316;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 11px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.arrow {
  color: rgba(255,255,255,0.3);
}

/* Performers */
.performers-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
  margin-top: 24px;
}

.performers-block {
  background: rgba(255,255,255,0.05);
  border-radius: 16px;
  padding: 16px;
}

.performers-block h3 {
  color: white;
  font-size: 14px;
  margin: 0 0 12px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.performers-block.top h3 i { color: #eab308; }
.performers-block.low h3 i { color: #ef4444; }

.performer-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.performer-item:last-child {
  border-bottom: none;
}

.rank {
  width: 24px;
  height: 24px;
  background: rgba(234, 179, 8, 0.2);
  color: #eab308;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
}

.performer-item .name {
  flex: 1;
  color: white;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.performer-item .views {
  color: rgba(255,255,255,0.6);
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.performer-item .views.low {
  color: #ef4444;
}

.boost-btn-small {
  background: #f97316;
  border: none;
  color: white;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
}

/* Modal */
.offer-modal {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.8);
  display: flex;
  align-items: flex-end;
  z-index: 1000;
}

.modal-content {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  width: 100%;
  max-height: 85vh;
  border-radius: 24px 24px 0 0;
  padding: 24px;
  overflow-y: auto;
}

.close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  background: rgba(255,255,255,0.1);
  border: none;
  color: white;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
}

.modal-content h2 {
  color: white;
  font-size: 20px;
  margin: 0 0 24px 0;
  padding-right: 40px;
}

.modal-summary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.modal-stat {
  text-align: center;
}

.modal-stat .value {
  display: block;
  color: white;
  font-size: 24px;
  font-weight: 700;
}

.modal-stat .label {
  color: rgba(255,255,255,0.5);
  font-size: 11px;
}

.modal-trend {
  text-align: center;
  padding: 12px;
  border-radius: 12px;
  margin-bottom: 20px;
  font-size: 14px;
}

.modal-trend.up { background: rgba(34, 197, 94, 0.2); color: #22c55e; }
.modal-trend.down { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
.modal-trend.stable { background: rgba(255,255,255,0.1); color: rgba(255,255,255,0.6); }

.hour-chart h4 {
  color: white;
  font-size: 14px;
  margin: 0 0 12px 0;
}

.hours-grid {
  display: flex;
  gap: 2px;
  margin-bottom: 20px;
}

.hour-bar {
  flex: 1;
  height: 40px;
  background: #6366f1;
  border-radius: 4px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding-bottom: 4px;
}

.hour-label {
  color: white;
  font-size: 8px;
}

.boost-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-radius: 12px;
  margin-bottom: 20px;
}

.boost-info.active {
  background: rgba(34, 197, 94, 0.2);
}

.boost-info.inactive {
  background: rgba(249, 115, 22, 0.2);
}

.boost-info i {
  font-size: 24px;
  color: #f97316;
}

.boost-info div {
  flex: 1;
}

.boost-info strong {
  display: block;
  color: white;
  font-size: 14px;
}

.boost-info span {
  color: rgba(255,255,255,0.6);
  font-size: 12px;
}

.boost-info button {
  background: #f97316;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
}

.modal-recommendations {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rec-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  border-radius: 10px;
  background: rgba(255,255,255,0.05);
  color: rgba(255,255,255,0.8);
  font-size: 13px;
}

.rec-item i {
  width: 20px;
  color: #6366f1;
}

.rec-item.boost i { color: #f97316; }
.rec-item.success i { color: #22c55e; }
.rec-item.alert i { color: #eab308; }
</style>
