<template>
  <svg
    viewBox="0 0 200 100"
    class="w-full h-full"
    aria-hidden="true"
    fill="none"
    stroke="currentColor"
    stroke-linecap="round"
    stroke-linejoin="round"
  >
    <!-- Car body (lower section) -->
    <path d="M12 55 L12 72 Q12 76 16 76 L184 76 Q188 76 188 72 L188 55 Z" stroke-width="2.5" />
    <!-- Cabin (upper section) -->
    <path d="M48 55 L62 24 L138 24 L155 55 Z" stroke-width="2.5" />
    <!-- Front windshield -->
    <path d="M136 28 L152 52" stroke-width="1.5" />
    <!-- Rear windshield -->
    <path d="M64 28 L49 52" stroke-width="1.5" />
    <!-- Window divider (B-pillar) -->
    <line x1="100" y1="25" x2="100" y2="54" stroke-width="1.5" />
    <!-- Front wheel -->
    <circle cx="150" cy="76" r="16" stroke-width="2.5" />
    <circle cx="150" cy="76" r="6" stroke-width="1.5" />
    <!-- Rear wheel -->
    <circle cx="50" cy="76" r="16" stroke-width="2.5" />
    <circle cx="50" cy="76" r="6" stroke-width="1.5" />
    <!-- Headlight -->
    <rect x="183" y="58" width="7" height="6" rx="1" stroke-width="1.5" />
    <!-- Taillight -->
    <rect x="10" y="58" width="7" height="6" rx="1" stroke-width="1.5" />
    <!-- Front bumper detail -->
    <line x1="188" y1="68" x2="196" y2="68" stroke-width="1.5" />
  </svg>
</template>
