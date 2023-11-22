<script setup>
import { useLayout } from '@/layout/composables/layout';
import { computed } from 'vue';

const { layoutConfig } = useLayout();

const logoUrl = computed(() => {
    return `layout/images/${layoutConfig.darkTheme.value ? 'logo-white' : 'logo-dark'}.svg`;
});
</script>

<template>
    <a href="https://www.cenit.finance">
        <div class="layout-footer">
            <img src="src/assets/cenit_logo.png" alt="Logo" height="30" width="30" class="mr-2" />
            by
            <span class="font-medium ml-2">Cenit</span>
        </div>
    </a>
</template>
<style lang="scss" scoped></style>
