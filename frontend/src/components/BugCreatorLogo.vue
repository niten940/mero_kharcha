<template>
  <div class="logo-container">
    <img
      :src="logo"
      alt="Bug Creator"
      class="bug-creator-logo"
    />
  </div>
</template>

<script setup>
import logo from '@/images/Bug_Creator.png'
</script>

<style scoped>


.bug-creator-logo {
  width: 100px;
  max-width: 550px;
  height: auto;
  display: centred;
  object-fit: contain;
}
</style>