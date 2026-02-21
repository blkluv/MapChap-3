<template>
  <div class="boost-section">
    <!-- Заголовок -->
    <div class="boost-hero">
      <div class="boost-icon">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
        </svg>
      </div>
      <h3>{{ t('boost_title') }}</h3>
      <p>{{ t('boost_desc') }}</p>
    </div>

    <!-- Выбор объявления -->
    <div v-if="userOffers.length > 0" class="offer-selector">
      <label>Выберите объявление для буста:</label>
      <select v-model="selectedOfferId" class="offer-select">
        <option v-for="offer in userOffers" :key="offer.id" :value="offer.id">
          {{ offer.title }}
        </option>
      </select>
    </div>
    <div v-else class="no-offers-hint">
      <p>Сначала создайте объявление в разделе "Бизнес"</p>
    </div>

    <!-- Как это работает -->
    <div class="how-works">
      <h4>{{ t('boost_how_works') }}</h4>
      <div class="steps">
        <div class="step">
          <span class="step-num">1</span>
          <strong>{{ t('boost_step1') }}</strong>
          <p>{{ t('boost_step1_desc') }}</p>
        </div>
        <div class="step">
          <span class="step-num">2</span>
          <strong>{{ t('boost_step2') }}</strong>
          <p>{{ t('boost_step2_desc') }}</p>
        </div>
        <div class="step">
          <span class="step-num">3</span>
          <strong>{{ t('boost_step3') }}</strong>
          <p>{{ t('boost_step3_desc') }}</p>
        </div>
      </div>
    </div>

    <!-- Тарифы бустов -->
    <div class="boost-plans">
      <div 
        class="boost-card"
        v-for="plan in boostPlans" 
        :key="plan.id"
        :class="{ popular: plan.popular, best: plan.best }"
        @click="selectPlan(plan)"
      >
        <div v-if="plan.popular" class="card-badge">{{ t('boost_popular') }}</div>
        <div v-if="plan.best" class="card-badge best">{{ t('boost_best') }}</div>
        
        <div class="card-header">
          <span class="card-days">{{ plan.days }}</span>
          <h4>{{ plan.days === 1 ? t('day') : t('days') }}</h4>
        </div>
        
        <div class="card-price">
          <span v-if="plan.price" class="price">{{ plan.price }}</span>
          <span v-if="plan.price" class="currency">Stars</span>
          <span v-else class="price-coming">{{ t('boost_price_coming') }}</span>
        </div>
        
        <ul class="card-features">
          <li>+ Push-уведомления</li>
          <li>+ Аналитика</li>
          <li v-if="plan.days >= 5">+ Популярное</li>
          <li v-if="plan.days >= 7">+ VIP статус</li>
        </ul>
        
        <button class="btn btn-primary btn-block" :disabled="!plan.price || isPurchasing || !selectedOfferId">
          {{ isPurchasing ? '...' : t('boost_buy') }}
        </button>
      </div>
    </div>

    <!-- Активные бусты -->
    <div class="active-boosts" v-if="activeBoosts.length > 0">
      <h4>{{ t('boost_active') }}</h4>
      <div class="active-list">
        <div v-for="boost in activeBoosts" :key="boost.id" class="active-card">
          <div class="active-info">
            <span class="active-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
              </svg>
            </span>
            <div>
              <strong>{{ boost.days }} {{ t('days') }}</strong>
              <p>{{ t('boost_expires') }}: {{ formatDate(boost.expires_at) }}</p>
            </div>
          </div>
          <div class="active-stats">
            <span>{{ boost.notifications_sent || 0 }} отпр.</span>
            <button 
              class="send-notif-btn" 
              @click="sendNotification(boost)"
              :disabled="isSendingNotif"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4 20-7z"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="no-boosts">
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/>
      </svg>
      <p>{{ t('boost_no_active') }}</p>
    </div>

    <!-- Информация о Telegram Stars -->
    <div class="stars-info">
      <h4>Оплата через Telegram Stars</h4>
      <p>Telegram Stars — универсальная валюта в Telegram. 1 Star ≈ $0.02</p>
      <ul>
        <li>• Мгновенное зачисление</li>
        <li>• Безопасная оплата через Telegram</li>
        <li>• Работает во всех странах</li>
      </ul>
    </div>

    <!-- Настройка оплаты ИП (для получения денег) -->
    <div class="payment-setup" v-if="showPaymentSetup">
      <h4>{{ t('boost_payment_setup') }}</h4>
      <p class="setup-desc">{{ t('boost_payment_desc') }}</p>
      
      <!-- Тип счёта -->
      <div class="account-type-selector">
        <button 
          class="type-btn" 
          :class="{ active: accountType === 'business' }"
          @click="accountType = 'business'"
        >
          {{ t('boost_bank_account') }}
        </button>
        <button 
          class="type-btn" 
          :class="{ active: accountType === 'ip' }"
          @click="accountType = 'ip'"
        >
          {{ t('boost_ip_account') }}
        </button>
      </div>
      
      <div class="form-group">
        <label>{{ t('boost_bank_account') }}</label>
        <input v-model="paymentDetails.account" type="text" placeholder="1234 5678 9012 3456">
      </div>
      
      <div class="form-group">
        <label>{{ t('boost_bank_name') }}</label>
        <input v-model="paymentDetails.bank" type="text" placeholder="Kapitalbank, Ipak Yuli, Hamkorbank...">
      </div>
      
      <div class="form-group">
        <label>{{ t('boost_holder_name') }}</label>
        <input v-model="paymentDetails.holder" type="text" :placeholder="accountType === 'ip' ? 'ИП Иванов Иван Иванович' : 'ООО Компания'">
      </div>
      
      <div class="form-group" v-if="accountType === 'ip'">
        <label>{{ t('boost_business_id') }}</label>
        <input v-model="paymentDetails.businessId" type="text" :placeholder="t('boost_business_id_placeholder')">
        <span class="field-hint">{{ t('boost_ip_hint') }}</span>
      </div>
      
      <button class="btn btn-primary btn-block" @click="savePaymentDetails" :disabled="!canSavePayment || isSaving">
        {{ isSaving ? t('loading') : t('boost_save_payment') }}
      </button>
      
      <div class="payment-note">
        <p>{{ t('boost_banks_note') }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useLocale } from '../composables/useLocale'
import { useUIStore } from '../stores/uiStore'
import { useAuthStore } from '../stores/authStore'
import { apiService } from '../services/api'

export default {
  name: 'BoostPanel',
  props: {
    showPaymentSetup: {
      type: Boolean,
      default: false
    }
  },
  setup() {
    const { t } = useLocale()
    const uiStore = useUIStore()
    const authStore = useAuthStore()
    
    // Тарифные планы с Telegram Stars
    const boostPlans = ref([
      { id: '1day', days: 1, icon: '•', price: 350, currency: 'XTR', popular: false, best: false },
      { id: '5days', days: 5, icon: '•', price: 1200, currency: 'XTR', popular: true, best: false },
      { id: '7days', days: 7, icon: '•', price: 1600, currency: 'XTR', popular: false, best: true }
    ])
    
    // Активные бусты пользователя
    const activeBoosts = ref([])
    const isSendingNotif = ref(false)
    const isSaving = ref(false)
    const isPurchasing = ref(false)
    const accountType = ref('business')
    const selectedOfferId = ref(null)
    
    // Детали оплаты
    const paymentDetails = reactive({
      account: '',
      bank: '',
      holder: '',
      businessId: ''
    })
    
    const canSavePayment = computed(() => {
      return paymentDetails.account.length >= 10 && 
             paymentDetails.bank.length >= 3 && 
             paymentDetails.holder.length >= 3
    })

    // Получаем Telegram WebApp
    const getTelegramWebApp = () => {
      return window.Telegram?.WebApp
    }
    
    const selectPlan = async (plan) => {
      if (!plan.price) {
        uiStore.showNotification(t('boost_price_coming'), 'info')
        return
      }
      
      if (!authStore.user?.telegram_id) {
        uiStore.showNotification('Необходима авторизация', 'error')
        return
      }

      // Проверяем есть ли объявления у пользователя
      if (!selectedOfferId.value) {
        uiStore.showNotification('Сначала выберите объявление для буста', 'info')
        return
      }

      isPurchasing.value = true
      
      try {
        // Создаём invoice на сервере
        const result = await apiService.createInvoice(
          authStore.user.telegram_id,
          plan.id,
          selectedOfferId.value
        )
        
        if (!result.success) {
          throw new Error(result.error || 'Ошибка создания счёта')
        }

        const tg = getTelegramWebApp()
        
        if (tg && result.invoice.invoice_link) {
          // Открываем Telegram Payment
          tg.openInvoice(result.invoice.invoice_link, async (status) => {
            if (status === 'paid') {
              // Подтверждаем платёж на сервере
              try {
                await apiService.confirmPayment({
                  telegram_payment_charge_id: 'tg_' + Date.now(),
                  provider_payment_charge_id: 'stars_' + Date.now(),
                  boost_type: plan.id,
                  offer_id: selectedOfferId.value,
                  telegram_id: authStore.user.telegram_id,
                  total_amount: plan.price,
                  currency: plan.currency
                })
                
                uiStore.showNotification('Буст успешно активирован!', 'success')
                loadActiveBoosts()
              } catch (e) {
                uiStore.showNotification('Ошибка активации буста', 'error')
              }
            } else if (status === 'cancelled') {
              uiStore.showNotification('Оплата отменена', 'info')
            } else if (status === 'failed') {
              uiStore.showNotification('Ошибка оплаты', 'error')
            }
          })
        } else {
          // Fallback без Telegram WebApp (для тестирования)
          uiStore.showNotification(`Telegram Stars: ${plan.price} XTR за ${plan.days} дней`, 'info')
        }
      } catch (error) {
        uiStore.showNotification(error.message || 'Ошибка', 'error')
      } finally {
        isPurchasing.value = false
      }
    }
    
    const sendNotification = async (boost) => {
      if (!authStore.user?.telegram_id || isSendingNotif.value) return
      
      isSendingNotif.value = true
      try {
        const result = await apiService.sendBoostNotification(boost.id, authStore.user.telegram_id)
        uiStore.showNotification(`📢 ${result.message}`, 'success')
        
        // Обновляем счётчик
        const idx = activeBoosts.value.findIndex(b => b.id === boost.id)
        if (idx !== -1) {
          activeBoosts.value[idx].notifications_sent = (activeBoosts.value[idx].notifications_sent || 0) + result.notifications_sent
        }
      } catch (error) {
        uiStore.showNotification(error.message || t('error'), 'error')
      } finally {
        isSendingNotif.value = false
      }
    }
    
    const savePaymentDetails = async () => {
      if (!canSavePayment.value || !authStore.user?.telegram_id || isSaving.value) return
      
      isSaving.value = true
      try {
        await apiService.updatePaymentDetails(authStore.user.telegram_id, {
          bank_account: paymentDetails.account,
          bank_name: paymentDetails.bank,
          holder_name: paymentDetails.holder,
          business_id: paymentDetails.businessId || null
        })
        
        // Также сохраняем в localStorage
        localStorage.setItem('mapchap_payment', JSON.stringify(paymentDetails))
        uiStore.showNotification(t('notif_saved'), 'success')
      } catch (error) {
        // Сохраняем локально если API недоступен
        localStorage.setItem('mapchap_payment', JSON.stringify(paymentDetails))
        uiStore.showNotification(t('notif_saved'), 'success')
      } finally {
        isSaving.value = false
      }
    }
    
    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleDateString()
    }
    
    // Загружаем сохранённые данные оплаты
    const loadPaymentDetails = async () => {
      // Сначала из localStorage
      const saved = localStorage.getItem('mapchap_payment')
      if (saved) {
        try {
          const data = JSON.parse(saved)
          Object.assign(paymentDetails, data)
        } catch {}
      }
      
      // Затем с сервера если авторизованы
      if (authStore.user?.telegram_id) {
        try {
          const result = await apiService.getPaymentDetails(authStore.user.telegram_id)
          if (result.payment_details && Object.keys(result.payment_details).length > 0) {
            paymentDetails.account = result.payment_details.bank_account || ''
            paymentDetails.bank = result.payment_details.bank_name || ''
            paymentDetails.holder = result.payment_details.holder_name || ''
            paymentDetails.businessId = result.payment_details.business_id || ''
          }
        } catch {}
      }
    }
    
    // Загружаем активные бусты
    const loadActiveBoosts = async () => {
      if (!authStore.user?.telegram_id) return
      
      try {
        const result = await apiService.getUserBoosts(authStore.user.telegram_id)
        activeBoosts.value = result.boosts || []
      } catch {
        activeBoosts.value = []
      }
    }
    
    // Загружаем тарифы с сервера
    const loadBoostPlans = async () => {
      try {
        const result = await apiService.getBoostPlans()
        if (result.plans) {
          boostPlans.value = result.plans.map(plan => ({
            id: plan.id,
            days: plan.days,
            icon: '•',
            price: plan.price,
            currency: plan.currency,
            popular: plan.popular,
            best: plan.best
          }))
        }
      } catch {}
    }

    // Загружаем объявления пользователя для выбора
    const userOffers = ref([])
    const loadUserOffers = async () => {
      if (!authStore.user?.telegram_id) return
      try {
        const result = await apiService.getUserOffers(authStore.user.telegram_id)
        userOffers.value = result.offers || []
        // Автоматически выбираем первое объявление
        if (userOffers.value.length > 0 && !selectedOfferId.value) {
          selectedOfferId.value = userOffers.value[0].id
        }
      } catch {}
    }
    
    onMounted(() => {
      loadPaymentDetails()
      loadActiveBoosts()
      loadBoostPlans()
      loadUserOffers()
    })
    
    return {
      t,
      boostPlans,
      activeBoosts,
      paymentDetails,
      canSavePayment,
      isSendingNotif,
      isSaving,
      isPurchasing,
      accountType,
      userOffers,
      selectedOfferId,
      selectPlan,
      sendNotification,
      savePaymentDetails,
      formatDate
    }
  }
}
</script>

<style scoped>
.boost-section {
  padding: 0;
}

.boost-hero {
  text-align: center;
  padding: 24px 16px;
  background: #fff;
  border-radius: 16px;
  margin-bottom: 16px;
}

.boost-icon {
  display: flex;
  justify-content: center;
  margin-bottom: 8px;
  color: #000;
}

.boost-hero h3 {
  margin: 0 0 4px;
  color: #000;
  font-size: 20px;
}

.boost-hero p {
  margin: 0;
  color: rgba(0,0,0,0.7);
  font-size: 13px;
}

/* Выбор объявления */
.offer-selector {
  background: #141414;
  border: 1px solid #2a2a2a;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 16px;
}

.offer-selector label {
  display: block;
  font-size: 12px;
  color: #888;
  margin-bottom: 8px;
}

.offer-select {
  width: 100%;
  padding: 10px 12px;
  background: #0a0a0a;
  border: 1px solid #333;
  border-radius: 8px;
  color: #fff;
  font-size: 14px;
}

.offer-select:focus {
  outline: none;
  border-color: #fff;
}

.no-offers-hint {
  background: #141414;
  border: 1px solid #2a2a2a;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  text-align: center;
}

.no-offers-hint p {
  margin: 0;
  color: #666;
  font-size: 13px;
}

.how-works {
  background: #141414;
  border: 1px solid #2a2a2a;
  border-radius: 14px;
  padding: 16px;
  margin-bottom: 16px;
}

.how-works h4 {
  margin: 0 0 12px;
  font-size: 14px;
  color: #fff;
}

.steps {
  display: flex;
  gap: 12px;
}

.step {
  flex: 1;
  text-align: center;
}

.step-num {
  width: 24px;
  height: 24px;
  background: #fff;
  color: #000;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  margin: 0 auto 4px;
}

.step strong {
  display: block;
  font-size: 12px;
  color: #fff;
  margin-bottom: 2px;
}

.step p {
  margin: 0;
  font-size: 10px;
  color: #666;
}

.boost-plans {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.boost-card {
  flex: 1;
  background: #141414;
  border: 1px solid #2a2a2a;
  border-radius: 14px;
  padding: 16px;
  position: relative;
  cursor: pointer;
  transition: all 0.2s;
}

.boost-card:hover {
  border-color: #fff;
}

.boost-card.popular {
  border-color: #fff;
}

.boost-card.best {
  border-color: #fff;
  background: #1a1a1a;
}

.card-badge {
  position: absolute;
  top: -8px;
  right: 10px;
  padding: 2px 8px;
  background: #fff;
  border-radius: 10px;
  font-size: 9px;
  font-weight: 600;
  color: #000;
}

.card-badge.best {
  background: #fff;
  color: #000;
}

.card-header {
  text-align: center;
  margin-bottom: 12px;
}

.card-days {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  display: block;
}

.card-header h4 {
  margin: 0;
  font-size: 12px;
  color: #888;
}

.card-price {
  text-align: center;
  margin-bottom: 12px;
}

.price {
  font-size: 24px;
  font-weight: 700;
  color: #fff;
}

.currency {
  font-size: 12px;
  color: #888;
  display: block;
}

.price-coming {
  font-size: 12px;
  color: #666;
}

.card-features {
  list-style: none;
  padding: 0;
  margin: 0 0 12px;
}

.card-features li {
  font-size: 11px;
  color: #888;
  margin-bottom: 4px;
}

.active-boosts h4,
.no-boosts {
  margin-bottom: 12px;
}

.active-boosts h4 {
  font-size: 14px;
  color: #fff;
}

.active-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.active-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: 10px;
}

.active-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.active-icon {
  font-size: 24px;
}

.active-info strong {
  display: block;
  color: #22c55e;
  font-size: 14px;
}

.active-info p {
  margin: 0;
  font-size: 11px;
  color: #888;
}

.active-stats {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #888;
}

.send-notif-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: #22c55e;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.send-notif-btn:hover {
  background: #16a34a;
}

.send-notif-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.no-boosts {
  text-align: center;
  padding: 24px;
  background: #141414;
  border-radius: 14px;
}

.no-boosts span {
  font-size: 32px;
  display: block;
  margin-bottom: 8px;
}

.no-boosts p {
  margin: 0;
  color: #666;
  font-size: 13px;
}

.payment-setup {
  background: #141414;
  border: 1px solid #2a2a2a;
  border-radius: 14px;
  padding: 16px;
  margin-top: 16px;
}

.payment-setup h4 {
  margin: 0 0 8px;
  font-size: 14px;
  color: #fff;
}

.setup-desc {
  margin: 0 0 16px;
  font-size: 12px;
  color: #666;
}

.account-type-selector {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.type-btn {
  flex: 1;
  padding: 10px;
  background: #0a0a0a;
  border: 1px solid #2a2a2a;
  border-radius: 10px;
  color: #888;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.type-btn.active {
  background: #fff;
  border-color: #fff;
  color: #000;
}

.form-group {
  margin-bottom: 12px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 12px;
  color: #888;
}

.form-group input {
  width: 100%;
  padding: 10px 12px;
  background: #0a0a0a;
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  color: #fff;
  font-size: 14px;
}

.form-group input:focus {
  outline: none;
  border-color: #fff;
}

.field-hint {
  display: block;
  margin-top: 4px;
  font-size: 11px;
  color: #666;
}

.payment-note {
  margin-top: 12px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.payment-note p {
  margin: 0;
  font-size: 11px;
  color: #888;
  text-align: center;
}

/* Stars info block */
.stars-info {
  background: #141414;
  border: 1px solid #2a2a2a;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
}

.stars-info h4 {
  margin: 0 0 8px;
  font-size: 14px;
  color: #fff;
}

.stars-info p {
  margin: 0 0 12px;
  font-size: 12px;
  color: #888;
}

.stars-info ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.stars-info li {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.btn {
  padding: 12px 16px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #fff;
  color: #000;
}

.btn-primary:hover {
  background: #e0e0e0;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-block {
  width: 100%;
}
</style>
