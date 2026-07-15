<!-- src/pages/TermsPage.vue -->
<template>
  <q-page class="terms-page q-pa-lg flex flex-center">
    <div class="terms-card bg-white q-pa-xl">
      <h1 class="text-h4 text-weight-bold q-mb-md">Terms of Service</h1>
      <p class="text-subtitle2 text-grey-7 q-mb-xl">Last Updated: July 2026</p>

      <div class="terms-content q-gutter-y-md">
        <section>
          <h2 class="text-h6 text-weight-bold">1. What is Mero Kharcha?</h2>
          <p>Mero Kharcha is your personal financial companion designed to help you track your expenses, manage your budgets, and keep an eye on where your money goes. We do not provide professional financial, investment, or tax advice.</p>
        </section>

        <section>
          <h2 class="text-h6 text-weight-bold">2. Your Account & Security</h2>
          <p>You are responsible for safeguarding the password you use to access your account. You agree to provide accurate email and registration information.</p>
        </section>

        <section>
          <h2 class="text-h6 text-weight-bold">3. Your Data & Privacy</h2>
          <p>It’s your money, it’s your data. We respect your privacy and will never sell your personal information or transaction history to third parties.</p>
        </section>
      </div>

      <q-btn 
        flat 
        color="primary" 
        label="Go Back" 
        icon="arrow_back" 
        class="q-mt-xl" 
        @click="$router.back()" 
      />
    </div>
  </q-page>
</template>

<style scoped>
.terms-page {
  background-color: #f2f4f3;
  min-height: 100vh;
}
.terms-card {
  max-width: 800px;
  width: 100%;
  border-radius: 20px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.02), 0 20px 48px rgba(0, 0, 0, 0.04);
}
.terms-content {
  color: #334155;
  line-height: 1.6;
}
h2 {
  color: #121824;
  margin-top: 20px;
  margin-bottom: 8px;
}
</style>