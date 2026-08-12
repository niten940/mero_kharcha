<template>
  <q-page class="settings-page">
    <!-- Top bar -->
    <div class="row items-center q-px-md q-py-sm top-bar">
      <q-btn flat round dense icon="arrow_back" @click="$router.back()" />
      <div class="text-h6 text-weight-bold col text-center">Settings</div>
      <q-avatar size="36px">
        <img :src="user.avatarUrl" v-if="user.avatarUrl" />
        <q-icon v-else name="person" />
      </q-avatar>
    </div>

    <div class="q-px-md q-pb-xl">
      <!-- ACCOUNT & SECURITY -->
      <section-label text="ACCOUNT & SECURITY" />
      <q-list class="settings-card">
        <q-item clickable v-ripple @click="goTo('profile-details')">
          <q-item-section avatar>
            <q-avatar size="34px" color="green-1" text-color="primary">
              <q-icon name="person" size="18px" />
            </q-avatar>
          </q-item-section>
          <q-item-section>Profile details</q-item-section>
          <q-item-section side>
            <q-icon name="chevron_right" color="grey-6" />
          </q-item-section>
        </q-item>

        <q-separator inset="item" />

        <q-item clickable v-ripple @click="goTo('change-password')">
          <q-item-section avatar>
            <q-avatar size="34px" color="green-1" text-color="primary">
              <q-icon name="password" size="18px" />
            </q-avatar>
          </q-item-section>
          <q-item-section>Change Password</q-item-section>
          <q-item-section side>
            <q-icon name="chevron_right" color="grey-6" />
          </q-item-section>
        </q-item>

        <q-separator inset="item" />

        <q-item>
          <q-item-section avatar>
            <q-avatar size="34px" color="green-1" text-color="primary">
              <q-icon name="shield" size="18px" />
            </q-avatar>
          </q-item-section>
          <q-item-section>
            <div>Two-Factor Authentication</div>
            <div class="text-caption text-grey-6">
              Adds an extra layer of security
            </div>
          </q-item-section>
          <q-item-section side>
            <q-toggle v-model="settings.twoFactor" color="primary" />
          </q-item-section>
        </q-item>
      </q-list>

      <!-- PREFERENCES -->
      <section-label text="PREFERENCES" />
      <q-list class="settings-card">
        <q-item>
          <q-item-section avatar>
            <q-avatar size="34px" color="green-1" text-color="primary">
              <q-icon name="event" size="18px" />
            </q-avatar>
          </q-item-section>
          <q-item-section>Calendar System</q-item-section>
          <q-item-section side>
            <q-btn-toggle
              v-model="settings.calendarSystem"
              toggle-color="primary"
              dense
              rounded
              no-caps
              :options="[
                { label: 'B.S.', value: 'BS' },
                { label: 'A.D.', value: 'AD' }
              ]"
            />
          </q-item-section>
        </q-item>

        <q-separator inset="item" />

        <q-item clickable v-ripple>
          <q-item-section avatar>
            <q-avatar size="34px" color="primary" text-color="white">
              <q-icon name="payments" size="18px" />
            </q-avatar>
          </q-item-section>
          <q-item-section>Currency display</q-item-section>
          <q-item-section side>
            <q-select
              v-model="settings.currency"
              :options="currencyOptions"
              dense
              borderless
              options-dense
              class="inline-select"
            />
          </q-item-section>
        </q-item>

        <q-separator inset="item" />

        <q-item clickable v-ripple>
          <q-item-section avatar>
            <q-avatar size="34px" color="green-1" text-color="primary">
              <q-icon name="language" size="18px" />
            </q-avatar>
          </q-item-section>
          <q-item-section>Language</q-item-section>
          <q-item-section side>
            <q-select
              v-model="settings.language"
              :options="languageOptions"
              dense
              borderless
              options-dense
              class="inline-select"
            />
          </q-item-section>
        </q-item>
      </q-list>

      <!-- NOTIFICATIONS -->
      <section-label text="NOTIFICATIONS" />
      <q-list class="settings-card">
        <q-item>
          <q-item-section avatar>
            <q-avatar size="34px" color="green-1" text-color="primary">
              <q-icon name="notifications" size="18px" />
            </q-avatar>
          </q-item-section>
          <q-item-section>Budget alerts</q-item-section>
          <q-item-section side>
            <q-toggle v-model="settings.budgetAlerts" color="primary" />
          </q-item-section>
        </q-item>

        <q-separator inset="item" />

        <q-item>
          <q-item-section avatar>
            <q-avatar size="34px" color="green-1" text-color="primary">
              <q-icon name="receipt_long" size="18px" />
            </q-avatar>
          </q-item-section>
          <q-item-section>Bill reminders</q-item-section>
          <q-item-section side>
            <q-toggle v-model="settings.billReminders" color="primary" />
          </q-item-section>
        </q-item>

        <q-separator inset="item" />

        <q-item>
          <q-item-section avatar>
            <q-avatar size="34px" color="green-1" text-color="primary">
              <q-icon name="show_chart" size="18px" />
            </q-avatar>
          </q-item-section>
          <q-item-section>Monthly reports</q-item-section>
          <q-item-section side>
            <q-toggle v-model="settings.monthlyReports" color="primary" />
          </q-item-section>
        </q-item>
      </q-list>

      <!-- DATA & SYNC -->
      <section-label text="DATA & SYNC" />
      <q-list class="settings-card">
        <q-item clickable v-ripple @click="goTo('linked-accounts')">
          <q-item-section avatar>
            <q-avatar size="34px" color="green-1" text-color="primary">
              <q-icon name="link" size="18px" />
            </q-avatar>
          </q-item-section>
          <q-item-section>
            <div>Manage linked accounts</div>
            <div class="text-caption text-grey-6">
              {{ linkedAccounts.banks }} Banks, {{ linkedAccounts.wallets }} Wallets connected
            </div>
          </q-item-section>
          <q-item-section side>
            <q-icon name="chevron_right" color="grey-6" />
          </q-item-section>
        </q-item>

        <q-separator inset="item" />

        <q-item clickable v-ripple @click="exportCsv">
          <q-item-section avatar>
            <q-avatar size="34px" color="green-1" text-color="primary">
              <q-icon name="file_download" size="18px" />
            </q-avatar>
          </q-item-section>
          <q-item-section>Export data to CSV</q-item-section>
          <q-item-section side>
            <q-icon name="chevron_right" color="grey-6" />
          </q-item-section>
        </q-item>

        <q-separator inset="item" />

        <q-item clickable v-ripple @click="goTo('backup-restore')">
          <q-item-section avatar>
            <q-avatar size="34px" color="green-1" text-color="primary">
              <q-icon name="sync_alt" size="18px" />
            </q-avatar>
          </q-item-section>
          <q-item-section>Backup / Restore</q-item-section>
          <q-item-section side>
            <q-icon name="chevron_right" color="grey-6" />
          </q-item-section>
        </q-item>
      </q-list>

      <!-- ABOUT -->
      <section-label text="ABOUT" />
      <q-list class="settings-card">
        <q-item clickable v-ripple @click="openLink('privacy')">
          <q-item-section avatar>
            <q-avatar size="34px" color="green-1" text-color="primary">
              <q-icon name="verified_user" size="18px" />
            </q-avatar>
          </q-item-section>
          <q-item-section>Privacy Policy</q-item-section>
          <q-item-section side>
            <q-icon name="chevron_right" color="grey-6" />
          </q-item-section>
        </q-item>

        <q-separator inset="item" />

        <q-item clickable v-ripple @click="openLink('terms')">
          <q-item-section avatar>
            <q-avatar size="34px" color="green-1" text-color="primary">
              <q-icon name="description" size="18px" />
            </q-avatar>
          </q-item-section>
          <q-item-section>Terms of Service</q-item-section>
          <q-item-section side>
            <q-icon name="chevron_right" color="grey-6" />
          </q-item-section>
        </q-item>
      </q-list>
    </div>
  </q-page>
</template>

<script setup>
import { reactive, h, defineComponent } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Small helper component for green section labels
const SectionLabel = defineComponent({
  props: { text: String },
  setup(props) {
    return () =>
      h(
        'div',
        { class: 'text-caption text-weight-bold section-label q-mt-md q-mb-sm' },
        props.text
      )
  }
})

// Replace with real user/settings store bindings
const user = reactive({
  avatarUrl: ''
})

const linkedAccounts = reactive({
  banks: 3,
  wallets: 2
})

const settings = reactive({
  twoFactor: false,
  calendarSystem: 'BS',
  currency: 'NPR (Rs)',
  language: 'English',
  budgetAlerts: true,
  billReminders: true,
  monthlyReports: false
})

const currencyOptions = ['NPR (Rs)', 'USD ($)', 'INR (₹)']
const languageOptions = ['English', 'नेपाली']

function goTo(routeName) {
  router.push({ name: routeName })
}

function exportCsv() {
  // hook this up to your export service
  console.log('exporting data to CSV...')
}

function openLink(type) {
  const routes = {
    privacy: '/privacy-policy',
    terms: '/terms-of-service'
  }
  router.push(routes[type])
}
</script>

<style scoped>
.settings-page {
  background: #f2f3f2;
  min-height: 100vh;
}

.top-bar {
  background: #ffffff;
}

.section-label {
  color: #14532d;
  letter-spacing: 0.5px;
}

.settings-card {
  background: #ffffff;
  border-radius: 14px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.inline-select {
  min-width: 90px;
}

.inline-select :deep(.q-field__control) {
  padding: 0;
}
</style>