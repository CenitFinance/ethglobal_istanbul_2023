<template>
    <div>
        <div class="grid p-fluid">
            <div class="col-12 xl:col-12">
                <div class="card">
                    <h5>Users distribution</h5>
                    <Chart type="combo" :data="usersDistribution.data" :options="usersDistribution.options"></Chart>
                </div>
            </div>
            <div class="col-12 xl:col-6">
                <div class="card">
                    <h5>Shap graph</h5>
                    <img src="https://dfstudio-d420.kxcdn.com/wordpress/wp-content/uploads/2019/06/digital_camera_photo-1080x675.jpg"
                        style="width: 100%" />
                </div>
            </div>
            <div class="col-12 xl:col-6">
                <div class="card">
                    <h5>Churn</h5>
                    <Chart type="combo" :data="churn.data" :options="churn.options"></Chart>
                </div>
            </div>
            <div class="col-12 xl:col-6">
                <div class="card">
                    <h5>Value generated</h5>
                    <Chart type="combo" :data="valueGenerated.data" :options="valueGenerated.options"></Chart>
                </div>
            </div>
        </div>
        <div class="grid p-fluid" style="margin-top: 1em;">
            <div class="col-12 xl:col-6 offset-xl-3">
                <div class="flex-auto">
                    <label for="campaign_funds" class="font-bold block mb-2"> Campaign funds </label>
                    <InputNumber v-model="campaignFunds" inputId="campaign_funds" />
                </div>
            </div>
        </div>
        <div class="grid p-fluid" style="margin-top: 1em;">
            <div class="col-12 xl:col-6">
                <div class="card">
                    <div class="formgroup-inline">
                        <div class="field">
                            <h3>Return probability</h3>
                        </div>
                        <div class="field">
                            <h3>Allocation</h3>
                        </div>
                    </div>
                    <div v-for="(cohort, index) in    cohorts   " :key="cohort.id">

                        <div class="formgroup-inline">
                            <div class="range-slider-container">
                                <Slider v-model="cohort.return_probability.values" range class="w-14rem"
                                    @change="cohortRangeChanged(cohort, index)" />
                                <div class="value-display min-value"
                                    :style="{ left: cohort.return_probability.values[0] + '%' }">
                                    {{ cohort.return_probability.values[0] }}
                                </div>
                                <div class="value-display max-value"
                                    :style="{ left: cohort.return_probability.values[1] + '%' }">
                                    {{ cohort.return_probability.values[1] }}
                                </div>
                            </div>
                            <div class="slider-container">
                                <Slider v-model="cohort.allocation.value" class="w-14rem"
                                    @change="cohortAllocationChanged(cohort, index)" />
                                <div class="value-display value" :style="{ left: cohort.allocation.value + '%' }">
                                    {{ cohort.allocation.value }}
                                </div>
                            </div>
                            <div class="field">
                                <Button icon="pi pi-times" severity="danger" text rounded aria-label="Cancel"
                                    @click="deleteCohort(index)" />
                            </div>
                        </div>
                    </div>
                    <Button icon="pi pi-plus" text rounded aria-label="Filter" @click="addCohort" />
                </div>
            </div>
        </div>
        <div class="grid p-fluid" style="margin-top: 1em;">
            <div class="col-12 xl:col-2"></div>
            <div class="col-12 xl:col-2">
                <Button label="Commit airdrop" raised size="large" />
            </div>
            <div class="col-12 xl:col-2"></div>
            <div class="col-12 xl:col-2"></div>
            <div class="col-12 xl:col-2">
                <Button label="Download airdrop parameters" raised size="large" />
            </div>
            <div class="col-12 xl:col-2"></div>
        </div>

    </div>
</template>
<script>
import { ref } from 'vue';

export default {
    data() {
        return {
            usersDistribution: {
                data: {
                    labels: ['Q1', 'Q2', 'Q3', 'Q4'],
                    datasets: [
                        {
                            type: "bar",
                            label: 'Sales',
                            data: [540, 325, 702, 620],
                            backgroundColor: 'rgba(255, 159, 64, 0.2)',
                            borderColor: 'rgb(255, 159, 64)',
                            borderWidth: 1
                        },
                        {
                            type: "line",
                            label: 'Sales_line',
                            data: [540, 325, 702, 620],
                            backgroundColor: 'rgba(255, 159, 64, 0.2)',
                            borderColor: 'rgb(255, 159, 64)',
                            borderWidth: 1,
                            tension: 0.4,
                        }
                    ]
                },
                options: {
                    plugins: {
                        legend: {
                            display: false,
                        }
                    }
                },
            },
            churn: {
                data: {
                    labels: ['Q1', 'Q2', 'Q3', 'Q4'],
                    datasets: [
                        {
                            type: "bar",
                            label: 'Sales',
                            data: [540, 325, 702, 620],
                            backgroundColor: 'rgba(255, 159, 64, 0.2)',
                            borderColor: 'rgb(255, 159, 64)',
                            borderWidth: 1
                        },
                        {
                            type: "line",
                            label: 'Sales_line',
                            data: [540, 325, 702, 620],
                            backgroundColor: 'rgba(255, 159, 64, 0.2)',
                            borderColor: 'rgb(255, 159, 64)',
                            borderWidth: 1,
                            tension: 0.4,
                        }
                    ]
                },
                options: {
                    plugins: {
                        legend: {
                            display: false,
                        }
                    }
                },
            },
            valueGenerated: {
                data: {
                    labels: ['Q1', 'Q2', 'Q3', 'Q4'],
                    datasets: [
                        {
                            type: "bar",
                            label: 'Sales',
                            data: [540, 325, 702, 620],
                            backgroundColor: 'rgba(255, 159, 64, 0.2)',
                            borderColor: 'rgb(255, 159, 64)',
                            borderWidth: 1
                        },
                        {
                            type: "line",
                            label: 'Sales_line',
                            data: [540, 325, 702, 620],
                            backgroundColor: 'rgba(255, 159, 64, 0.2)',
                            borderColor: 'rgb(255, 159, 64)',
                            borderWidth: 1,
                            tension: 0.4,
                        }
                    ]
                },
                options: {
                    plugins: {
                        legend: {
                            display: false,
                        }
                    }
                },
            },
            campaignFunds: ref(0),
            cohorts: [],
        }
    },
    methods: {
        addCohort() {
            var new_min;
            if (this.cohorts.length === 0) {
                new_min = 0
            } else {
                const prev_cohort = this.cohorts[this.cohorts.length - 1]
                const prev_cohort_min = prev_cohort.return_probability.values[0]
                new_min = Math.round((100 + prev_cohort_min) / 2)
                prev_cohort.return_probability.values[1] = new_min
            }

            const allocation = this.cohorts.length === 0 ? 100 : 0

            this.cohorts.push({
                return_probability: {
                    values: ref([new_min, 100]),
                    min: 0,
                    max: 100,
                    range: true,
                    label: 'Return Probability',
                },
                allocation: {
                    value: ref(allocation),
                    min: 0,
                    max: 100,
                }
            })
        },
        deleteCohort(index) {
            if (this.cohorts.length === 1) {
                this.cohorts = []
                return
            } else if (index === 0 && this.cohorts.length > 1) {
                const next_cohort = this.cohorts[index + 1]
                next_cohort.return_probability.values[0] = 0
            } else if (index === this.cohorts.length - 1 && this.cohorts.length > 1) {
                const prev_cohort = this.cohorts[index - 1]
                prev_cohort.return_probability.values[1] = 100
            } else {
                const this_cohort = this.cohorts[index]
                const midpoint = (this_cohort.return_probability.values[0] + this_cohort.return_probability.values[1]) / 2
                const prev_cohort = this.cohorts[index - 1]
                prev_cohort.return_probability.values[1] = midpoint
                const next_cohort = this.cohorts[index + 1]
                next_cohort.return_probability.values[0] = midpoint
            }

            this.cohorts.splice(index, 1)

            const already_allocated = this.cohorts.filter((_, i) => i < index).reduce((acc, c) => acc + c.allocation.value, 0)
            const remaining_allocation = 100 - already_allocated
            this.adjustCohortsAllocations(index, remaining_allocation)
        },
        cohortRangeChanged(cohort, index) {
            var new_min;

            if (index === 0) {
                new_min = 0
            } else {
                new_min = Math.min(
                    cohort.return_probability.values[0],
                    cohort.return_probability.values[1],
                )
            }

            var new_max
            if (index === this.cohorts.length - 1) {
                new_max = 100
            } else {
                new_max = Math.max(
                    cohort.return_probability.values[0],
                    cohort.return_probability.values[1],
                )
            }

            cohort.return_probability.values = [new_min, new_max]


            if (index > 0) {
                const prev_index = index - 1
                const prev_cohort = this.cohorts[prev_index]
                const next_cohort_changed = prev_cohort.return_probability.values[1] !== new_min
                if (next_cohort_changed) {
                    prev_cohort.return_probability.values[1] = new_min
                    this.cohortRangeChanged(prev_cohort, index - 1)
                }

            }

            if (index < this.cohorts.length - 1) {
                const next_index = index + 1
                const next_cohort = this.cohorts[next_index]
                const next_cohort_changed = next_cohort.return_probability.values[0] !== new_max
                if (next_cohort_changed) {
                    next_cohort.return_probability.values[0] = new_max
                    this.cohortRangeChanged(next_cohort, index + 1)
                }
            }
        },
        cohortAllocationChanged(cohort, index) {
            const total_allocation_above = this.cohorts.filter((_, i) => i < index).reduce((acc, c) => acc + c.allocation.value, 0)
            if (total_allocation_above + cohort.allocation.value > 100) {
                cohort.allocation.value = 100 - total_allocation_above
            }

            if (index === this.cohorts.length - 1) {
                cohort.allocation.value = 100 - total_allocation_above
            }

            const remaining_allocation = 100 - (total_allocation_above + cohort.allocation.value)
            const total_allocation_below = this.cohorts.filter((_, i) => i > index).reduce((acc, c) => acc + c.allocation.value, 0)

            for (let i = index + 1; i < this.cohorts.length; i++) {
                const cohort = this.cohorts[i]
                var new_allocation_ratio;

                if (total_allocation_below === 0) {
                    new_allocation_ratio = 1 / (this.cohorts.length - index)
                } else {
                    new_allocation_ratio = cohort.allocation.value / total_allocation_below
                }
                const new_allocation = Math.round(new_allocation_ratio * remaining_allocation)
                cohort.allocation.value = new_allocation
            }
        },
        adjustCohortsAllocations(index, remaining_allocation) {
            const current_cohort = this.cohorts[index]
            if (index === this.cohorts.length - 1) {
                current_cohort.allocation.value = remaining_allocation
                return
            }

            if (remaining_allocation === 0) {
                for (let i = index; i < this.cohorts.length; i++) {
                    const cohort = this.cohorts[i]
                    cohort.allocation.value = 0
                }
                return
            }

            const current_allocation_assigned_forward = this.cohorts.filter((_, i) => i >= index).reduce((acc, c) => acc + c.allocation.value, 0)
            if (current_allocation_assigned_forward === 0) {
                for (let i = index; i < this.cohorts.length; i++) {
                    const cohort = this.cohorts[i]
                    cohort.allocation.value = Math.round(remaining_allocation / (this.cohorts.length - index))
                }
                return
            }

            const current_cohort_allocation_ratio = current_cohort.allocation.value / current_allocation_assigned_forward
            const new_current_cohort_allocation = Math.round(current_cohort_allocation_ratio * remaining_allocation)
            current_cohort.allocation.value = new_current_cohort_allocation

            this.adjustCohortsAllocations(index + 1, remaining_allocation - new_current_cohort_allocation)
        }
    }
}
</script>
<style>
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
