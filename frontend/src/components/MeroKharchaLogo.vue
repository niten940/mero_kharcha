<template>
  <div class="mero-kharcha-logo">
    <div class="logo-top">
      <span class="mero">Mer</span>

      <!-- Coin mark: single circle with color transition + रू glyph + leaf -->
      <svg
        class="rupee-mark"
        viewBox="0 0 200 200"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <!-- Gradient for the single continuous circle -->
          <linearGradient id="circleGradient" x1="0%" y1="100%" x2="0%" y2="0%">
            <stop offset="0%" stop-color="#10294B" />
            <stop offset="15%" stop-color="#10294B" />
            <stop offset="55%" stop-color="#087A5B" />
            <stop offset="80%" stop-color="#008a64" />
          </linearGradient>

          <!-- Gradient for the Devanagari रू glyph -->
          <linearGradient id="glyphGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#13294B" />
            <!-- <stop offset="55%" stop-color="#13294B" />
            <stop offset="65%" stop-color="#087A5B" />
            <stop offset="100%" stop-color="#087A5B" /> -->
          </linearGradient>
        </defs>

        <!-- Single unified circle around the rupees symbol -->
        <path
       
          d="M 47 65 
          a 40 40 0 1 0 1 0"
          fill="none"
          stroke="url(#circleGradient)"
          stroke-width="13"
          stroke-linecap="round"
        />

        <!-- रू glyph dropped in as real Devanagari type -->
        <text
          x="47"
          y="125"
          text-anchor="middle"
          font-family="'Noto Sans Devanagari', 'Mangal', sans-serif"
          font-size="52"
          font-weight="700"
          fill="url(#glyphGradient)"
        >रू</text>

        <!-- Leaf pair sitting right in the upper-right gap -->
        <!-- <g transform="translate(126, 30) rotate(18)">
          <path
            d="M0,0
               C14,-16 30,-18 44,-6
               C32,-2 20,4 8,14
               C2,10 -2,5 0,0 Z"
            fill="#087A5B"
          />
          <path
            d="M4,16
               C18,2 36,-1 48,10
               C36,15 24,22 12,30
               C6,26 2,21 4,16 Z"
            fill="#087A5B"
          />
        </g> -->
      </svg>
    </div>

    <div class="kharcha">
      Kharcha
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@700&display=swap');

.mero-kharcha-logo {
  /* Change this single value to scale the whole logo up or down */
  --logo-size: 30px;

  display: inline-flex;
  flex-direction: column;
  align-items: flex-start;

  font-family: 'Poppins', sans-serif;
  user-select: none;
}

/* "Mer" + coin mark row */
.logo-top {
  display: flex;
  align-items: center;
  height: var(--logo-size);
}

.mero {
  font-size: calc(var(--logo-size) * 0.62);
  line-height: 1;
  font-weight: 600;
  letter-spacing: auto;
  color: #13294b;
}

.rupee-mark {
  width: var(--logo-size);
  height: var(--logo-size);
  flex-shrink: 0;
  /* Small defined gap between "Mer" and the coin mark */
  margin-left: calc(var(--logo-size) * 0.03);
}

/* "Kharcha" row */
.kharcha {
  /* Defined gap under the top row */
  margin-top: calc(var(--logo-size) * -0.12);
  margin-left: calc(var(--logo-size) * 0.02);

  font-size: calc(var(--logo-size) * 0.68);
  line-height: 1;
  font-weight: 500;
  letter-spacing: auto;

  color: #087a5b;
}
</style>