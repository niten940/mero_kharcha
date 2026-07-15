<!-- src/pages/PrivacyPage.vue -->
<template>
  <q-page class="privacy-page q-pa-lg flex flex-center">
    <div class="privacy-card bg-white q-pa-xl">
      <h1 class="text-h4 text-weight-bold q-mb-md">Privacy Policy</h1>
      <p class="text-subtitle2 text-grey-7 q-mb-xl">Last Updated: July 2026</p>

      <div class="privacy-content q-gutter-y-md">
        <section>
          <h2 class="text-h6 text-weight-bold">1. What Information We Collect</h2>
          <p>
            We keep things minimal. We collect your **name** and **email address** when you register. Any financial data, budgets, or transactions you enter inside <em>Mero Kharcha</em> are stored securely to help you track your spending.
          </p>
        </section>

        <section>
          <h2 class="text-h6 text-weight-bold">2. How We Use Your Data</h2>
          <p>
            Your data is used solely to run and improve the app. We use it to calculate your budget statistics, sync your data across your devices, and send you important security alerts or password reset emails.
          </p>
        </section>

        <section>
          <h2 class="text-h6 text-weight-bold">3. No Selling or Sharing</h2>
          <p>
            Your financial life is private. **We will never sell, rent, or trade your personal information or financial logs to advertisers or third parties.** Period.
          </p>
        </section>

        <section>
          <h2 class="text-h6 text-weight-bold">4. Security of Your Data</h2>
          <p>
            We use modern industry-standard encryption protocols to protect your credentials and data records from unauthorized access. However, please remember that no method of transmission over the internet is 100% secure.
          </p>
        </section>

        <section>
          <h2 class="text-h6 text-weight-bold">5. Your Control & Rights</h2>
          <p>
            You are in control of your data. You can edit your profile details or request the permanent deletion of your account and all associated transaction history at any time through your account settings.
          </p>
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
.privacy-page {
  background-color: #f2f4f3;
  min-height: 100vh;
}
.privacy-card {
  max-width: 800px;
  width: 100%;
  border-radius: 20px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.02), 0 20px 48px rgba(0, 0, 0, 0.04);
}
.privacy-content {
  color: #334155;
  line-height: 1.6;
}
h2 {
  color: #121824;
  margin-top: 20px;
  margin-bottom: 8px;
}
</style>