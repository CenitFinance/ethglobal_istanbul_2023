<script setup>
import { defineEmits, defineProps } from "vue";

const props = defineProps({
    cohort: {
        type: Object,
        default: null,
    },
    index: {
        type: Number,
        default: null,
    },
});

const emit = defineEmits(
    [
        "cohortRangeChanged",
        "cohortAllocationChanged",
        "deleteCohort",
    ]
)

function cohortRangeChanged(cohort, index) {
    emit("cohortRangeChanged", cohort, index);
}

function cohortAllocationChanged(cohort, index) {
    emit("cohortAllocationChanged", cohort, index);
}

function deleteCohort(index) {
    emit("deleteCohort", index);
}

</script >

<template>
    <div class="formgroup-inline">

        <div class="range-slider-container">
            <Slider v-model="cohort.return_probability.values" range class="w-14rem"
                @change="cohortRangeChanged(cohort, index)" />
            <div class="value-display min-value" :style="{ left: cohort.return_probability.values[0] + '%' }">
                {{ cohort.return_probability.values[0] }}
            </div>
            <div class="value-display max-value" :style="{ left: cohort.return_probability.values[1] + '%' }">
                {{ cohort.return_probability.values[1] }}
            </div>
        </div>
        <div class="slider-container">
            <Slider v-model="cohort.allocation.value" class="w-14rem" @change="cohortAllocationChanged(cohort, index)" />
            <div class="value-display value" :style="{ left: cohort.allocation.value + '%' }">
                {{ cohort.allocation.value }}
            </div>
        </div>
        <div class="field">
            <Button icon="pi pi-times" severity="danger" text rounded aria-label="Cancel" @click="deleteCohort(index)" />
        </div>
    </div>
</template>

<style scoped>
.range-slider-container {
    position: relative;
    margin-left: 1rem;
    margin-right: 1rem;
}

.slider-container {
    position: relative;
    margin-left: 1rem;
    margin-right: 1rem;
}

.formgroup-inline {
    display: flex;
    align-items: center;
}

.value-display {
    position: absolute;
    top: -30px;
    /* Adjust as needed */
    transform: translateX(-50%);
    /* Add more styling as needed */
}
</style>


