<template>
    <div>
        <div class="grid p-fluid">
            <div class="col-12 xl:col-2">
                <h4 for="protocol_selector" class="block mb-2"> Select a protocol </h4>
                <Dropdown v-model="selectedProtocol" editable :options="availableProtocols" optionLabel="name"
                    placeholder="Select a protocol" class="w-full md:w-14rem" @change="updateProtocolData"
                    inputId="protocol_selector" />
            </div>
            <div class="col-12 xl:col-8"></div>
            <div v-if="!metamask.connected" class="col-12 xl:col-2" style="align: right;">
                <Button label="Connect Metamask" raised size="large" @click="connectMetamask" />
            </div>
            <div v-else class="col-12 xl:col-2" style="align: right;">
                <Button label="Disconnect Metamask" raised size="large" @click="terminateMetamask" />
            </div>
        </div>
        <h3>User analytics</h3>
        <div class="grid p-fluid">
            <div class="col-12 xl:col-12">
                <div class="card">
                    <h5>Users distribution</h5>
                    <Chart type="combo" :data="usersDistribution.data" :options="usersDistribution.options" height=50>
                    </Chart>
                </div>
            </div>
            <div class="col-12 xl:col-6">
                <div class="card">
                    <h5>Shap graph</h5>
                    <img :src="shapGraph" style="width: 100%" />
                </div>
            </div>
            <div class="col-12 xl:col-6">
                <div class="card">
                    <h5>Churn probability</h5>
                    <Chart type="line" :data="churn.data" :options="churn.options" height=150></Chart>
                </div>
                <div class="card">
                    <h5>Recorded interactions</h5>
                    <Chart type="combo" :data="valueGenerated.data" :options="valueGenerated.options" height=150></Chart>
                </div>
            </div>
        </div>

        <h3>Airdrop parameters</h3>

        <div class="grid p-fluid" style="margin-top: 1em;">
            <div class="col-12 xl:col-6">
                <div class="flex-auto">
                    <h4 for="campaign_funds" class="block mb-2"> Campaign funds (tokens) </h4>
                    <InputNumber v-model="campaignFunds" inputId="campaign_funds" />
                </div>
                <div class="card">
                    <div class="grid p-fluid">
                        <div class="col-12 xl:col-4">
                            <h3>Return probability</h3>
                        </div>
                        <div class="col-12 xl:col-4">
                            <h3>Allocation</h3>
                        </div>
                    </div>
                    <div v-for="(cohort, index) in    cohorts   " :key="cohort.id">
                        <CohortInput :cohort="cohort" :index="index" @cohortRangeChanged="cohortRangeChanged"
                            @cohortAllocationChanged="cohortAllocationChanged" @deleteCohort="deleteCohort" />
                    </div>
                    <Button icon="pi pi-plus" text rounded aria-label="Filter" @click="addCohort" />
                </div>
            </div>
            <div class="col-12 xl:col-6">
                <div class="grid p-fluid" style="margin-top: 1em;">
                    <div class="col-12 xl:col-6 card">
                        <h5>
                            Value generated in the last window
                        </h5>
                        <h3>
                            {{ totalValueGenerated }} interactions
                        </h3>
                    </div>
                    <div class="col-12 xl:col-6 card">
                        <h5>
                            Total targeted addresses
                        </h5>
                        <h3>
                            {{ targettedAddressesCount }}
                        </h3>
                    </div>
                    <div class="col-12 xl:col-6 card">
                        <h5>
                            Tokens allocated per interaction in the last window
                        </h5>
                        <h3>
                            {{ (campaignFunds / totalValueGenerated).toFixed(2) }} tokens/interaction
                        </h3>
                    </div>
                    <div class="col-12 xl:col-6 card">
                        <h5>
                            Average tokens allocated per address
                        </h5>
                        <h3>
                            {{ targettedAddressesCount !== 0 ? (campaignFunds / targettedAddressesCount).toFixed(2) : 0 }}
                            tokens/address
                        </h3>
                    </div>
                </div>

            </div>
        </div>

        <div class="grid p-fluid" style="margin-top: 1em;">
            <div class="col-12 xl:col-2"></div>
            <div class="col-12 xl:col-2">
                <Button label="Commit airdrop" raised size="large" @click="commitAirdrop" />
            </div>
            <div class="col-12 xl:col-4"></div>
            <div class="col-12 xl:col-2">
                <Button label="Download airdrop parameters" raised size="large" @click="downloadContractData" />
            </div>
            <div class="col-12 xl:col-2"></div>
        </div>

    </div>
</template>
<script>
import BlockViewer from '@/components/BlockViewer.vue';
import CohortInput from '@/components/CohortInput.vue';
import { network_to_contract, network_to_id, protocol_to_network } from '@/contracts.js';
import { MetaMaskSDK } from '@metamask/sdk';
import { ethers } from 'ethers';

import { ref } from 'vue';

async function fetchShapGraph(protocol) {
    return "results/" + protocol + "/beeswarm.png"
}


async function fetchUserStats(protocol) {
    const path = "results/" + protocol + "/prod_data.json"
    const results = await fetch(path)
        .then(response => response.json())
    results.user_probas["0x1b162d4377D52786d2Af4160b2Ec57fE31353696"] = 0.53
    return results
}

const documentStyle = getComputedStyle(document.documentElement);

async function getUsersDistribution(user_probas) {
    // The labels should be by percentile, so from 1 to 100
    const labels = Array.from(Array(100).keys())
    // Classify the users by percentile. The original data is over 1, not 100
    // The original data comes from a dict[str, float] in Python where 0 <= float <= 1
    const total_users = Object.keys(user_probas).length

    const users_by_percentile = labels.map((label) => {
        const lower_bound = label / 100
        const upper_bound = (label + 1) / 100
        const users_in_group = Object.entries(user_probas).filter((user_proba) => {
            const proba = user_proba[1]
            return proba >= lower_bound && proba < upper_bound
        }).length

        return 100 * (users_in_group / total_users)
    })

    return {
        components: {
            CohortInput,
            BlockViewer,
        },
        data: {
            labels: labels,
            datasets: [
                {
                    type: "bar",
                    label: "Users",
                    backgroundColor: documentStyle.getPropertyValue('--primary-500'),
                    borderColor: documentStyle.getPropertyValue('--primary-500'),
                    data: Object.values(users_by_percentile),
                },
            ]
        },
        options: {
            plugins: {
                legend: {
                    display: false,
                }
            },
            scales: {
                y: {
                    // From here: https://www.chartjs.org/docs/latest/axes/labelling.html
                    title: {
                        display: true,
                        text: "% of users"
                    }
                },
                x: {
                    // From here: https://www.chartjs.org/docs/latest/axes/labelling.html
                    title: {
                        display: true,
                        text: "Return probability (%)"
                    }
                },
            },

        },
    }
}

async function getValueGenerated(user_groups) {
    const total_users = user_groups.map((group) => group.count).reduce((acc, c) => acc + c, 0)

    return {
        data: {
            labels: user_groups.map((group) => group.label),
            datasets: [
                {
                    type: "bar",
                    label: "Users",
                    backgroundColor: documentStyle.getPropertyValue('--primary-500'),
                    borderColor: documentStyle.getPropertyValue('--primary-500'),
                    data: user_groups.map((group) => {
                        return 100 * (group.count / total_users)
                    })
                }
            ],
        },
        options: {
            plugins: {
                legend: {
                    display: false,
                }
            },
            scales: {
                y: {
                    // From here: https://www.chartjs.org/docs/latest/axes/labelling.html
                    title: {
                        display: true,
                        text: "% of users"
                    }
                },
                x: {
                    // From here: https://www.chartjs.org/docs/latest/axes/labelling.html
                    title: {
                        display: true,
                        text: "Interactions in the last period"
                    }
                },
            }
        },
    }
}

async function getChurn(user_groups) {

    return {
        data: {
            labels: user_groups.map((group) => group.label),
            datasets: [
                {
                    type: 'line',
                    label: 'Median',
                    data: user_groups.map((group) => 100 * group.median),
                    backgroundColor: 'blue',
                    borderColor: 'blue',
                },
                {
                    type: 'line',
                    label: '75th Percentile',
                    data: user_groups.map((group) => 100 * group.pct75),
                    backgroundColor: 'transparent',
                    borderColor: 'red',
                    borderWidth: 2,
                    borderDash: [5, 5],
                },
                {
                    type: 'line',
                    label: '25th Percentile',
                    data: user_groups.map((group) => 100 * group.pct25),
                    backgroundColor: 'transparent',
                    borderColor: 'green',
                    borderWidth: 2,
                    borderDash: [5, 5],
                },
            ],
        },
        options: {
            plugins: {
                legend: {
                    display: false,
                }
            },
            scales: {
                y: {
                    // From here: https://www.chartjs.org/docs/latest/axes/labelling.html
                    title: {
                        display: true,
                        text: "Probability of churn (%)"
                    }
                },
                x: {
                    // From here: https://www.chartjs.org/docs/latest/axes/labelling.html
                    title: {
                        display: true,
                        text: "Interactions in the last period"
                    }
                },
            },

        },
    }
}

async function getAvailableProtocols() {
    return [
        "polygon",
        "arbitrum",
        "base",
        "celo",
        "gnosis",
        "layer_zero",
        "optimism",
        "zksync",
    ]
}

async function getArtifact() {
    console.log("Getting artifact")
    const response = await fetch("ZkMLAirdrop.json");
    console.log(response)
    return await response.json()
}

export default {
    data() {
        return {
            availableProtocols: [],
            selectedProtocol: null,
            usersDistribution: {},
            churn: {},
            valueGenerated: {},
            campaignFunds: ref(0),
            cohorts: [
                {
                    return_probability: {
                        values: ref([0, 100]),
                        min: 0,
                        max: 100,
                        range: true,
                    },
                    allocation: {
                        value: ref(100),
                        min: 0,
                        max: 100,
                    }
                }
            ],
            shapGraph: null,
            userStats: {
                probs: {},
                groups: [],
            },
            totalValueGenerated: 0,
            targettedAddressesCount: 0,
            metamask: {
                sdk: null,
                provider: null,
                connected: false,
            }
        }
    },
    created() {
        this.metamask.sdk = new MetaMaskSDK({
            dappMetadata: {
                url: window.location.href,
                name: "Smart incentives dashboard",
            },
            checkInstallationImmediately: false,
            checkInstallationOnAllCalls: true,
        })
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
                },
                allocation: {
                    value: ref(allocation),
                    min: 0,
                    max: 100,
                }
            })
            this.updateTargettedAddressesCount()
        },
        deleteCohort(index) {
            if (this.cohorts.length === 1) {
                this.cohorts = []
                this.updateTargettedAddressesCount()
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
            this.updateTargettedAddressesCount()
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

            this.updateTargettedAddressesCount()
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

            this.updateTargettedAddressesCount()
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
        },
        async updateShapGraph() {
            this.shapGraph = await fetchShapGraph(this.selectedProtocol.code)
        },
        async updateUserStats() {
            const userStats = await fetchUserStats(this.selectedProtocol.code)
            this.userStats = userStats
        },
        async updateUsersDistribution() {
            const usersDistribution = await getUsersDistribution(this.userStats.user_probas)
            this.usersDistribution = usersDistribution
        },
        async updateValueGenerated() {
            const valueGenerated = await getValueGenerated(this.userStats.user_groups)
            this.valueGenerated = valueGenerated
        },
        async updateChurn() {
            const churn = await getChurn(this.userStats.user_groups)
            this.churn = churn
        },
        async getContractData() {
            const total_allocation = this.campaignFunds
            const allocations_by_cohort = this.cohorts.map((cohort) => {
                const min_return_probability = cohort.return_probability.values[0] / 100
                const max_return_probability = cohort.return_probability.values[1] / 100
                const allocation_ratio = cohort.allocation.value / 100
                const cohort_allocation = total_allocation * allocation_ratio

                const number_of_addresses = Object.values(this.userStats.user_probas).filter((user_proba) => {
                    return user_proba >= min_return_probability && user_proba < max_return_probability
                }).length

                const tokens_per_address = number_of_addresses !== 0 ? cohort_allocation / number_of_addresses : 0
                return {
                    zkMLPoints: Math.floor(max_return_probability * 10000),
                    allocation: ethers.utils.parseEther(tokens_per_address.toString()),
                }
            })
            return allocations_by_cohort
        },
        async downloadContractData() {
            const contractData = await this.getContractData()
            const jsonStr = JSON.stringify(contractData, null, 2);
            const blob = new Blob([jsonStr], { type: "application/json" });
            const url = URL.createObjectURL(blob);

            const link = document.createElement('a');
            link.href = url;
            link.download = "airdrop_parameters.json";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            URL.revokeObjectURL(url);
        },
        async getAddress() {
            const accounts = await this.metamask.provider.request({
                method: "eth_requestAccounts",
                params: [],
            });
            return accounts[0];
        },
        updateTotalValueGenerated() {
            const total_value_generated = this.userStats.user_groups.reduce((acc, group) => acc + group.value_generated, 0)
            this.totalValueGenerated = total_value_generated
        },
        updateTargettedAddressesCount() {
            const targettedAccounts = this.cohorts.map((cohort) => {
                if (cohort.allocation.value === 0) {
                    return 0
                }
                const min_return_probability = cohort.return_probability.values[0] / 100
                const max_return_probability = cohort.return_probability.values[1] / 100
                const number_of_addresses = Object.values(this.userStats.user_probas).filter((user_proba) => {
                    return user_proba >= min_return_probability && user_proba < max_return_probability
                }).length
                return number_of_addresses
            })
            this.targettedAddressesCount = targettedAccounts.reduce((acc, c) => acc + c, 0)
        },
        async initAvailableProtocols() {
            const availableProtocols = await getAvailableProtocols()
            this.availableProtocols = availableProtocols.map(
                (protocol) => {
                    return {
                        name: protocol,
                        code: protocol,
                    }
                }
            )
            this.selectedProtocol = ref(this.availableProtocols[0])
        },
        async updateProtocolData() {
            await this.updateShapGraph()
            await this.updateUserStats()
            await this.updateUsersDistribution()
            await this.updateValueGenerated()
            await this.updateChurn()
            await this.updateTotalValueGenerated()
            this.updateTargettedAddressesCount()
            if (this.metamask.connected) {
                await this.syncNetwork()
            }
        },
        async connectMetamask() {
            this.metamask.provider = await this.metamask.sdk.getProvider();
            await this.getAddress()
            this.metamask.connected = true
            await this.syncNetwork()
        },
        async getSigner() {
            const provider = new ethers.providers.Web3Provider(window.ethereum);
            return await provider.getSigner();
        },
        getContractAddress() {
            return network_to_contract[protocol_to_network[this.selectedProtocol.code]]
        },
        async commitAirdrop() {
            if (!this.metamask.connected) {
                await this.connectMetamask()
            }
            // if (!this.metamask.provider) {
            //     this.metamask.provider = await this.metamask.sdk.getProvider();
            //     await this.getAddress()
            //     this.metamask.connected = true
            // }
            await this.syncNetwork()
            const allocationParameters = await this.getContractData()
            const artifact = await getArtifact()
            const signer = await this.getSigner()
            const zkMLAirdropContract = new ethers.Contract(this.getContractAddress(), artifact.abi, signer);
            await (await zkMLAirdropContract.submitAirdropParameters(allocationParameters)).wait()
        },
        async terminateMetamask() {
            await this.metamask.sdk.terminate()
            this.metamask.connected = false
            this.metamask.provider = null
        },
        async syncNetwork() {
            console.log("Syncing network")
            const current_chain = await this.metamask.provider.request({
                method: "eth_chainId",
            });
            const protocol_chain = network_to_id[protocol_to_network[this.selectedProtocol.code]]

            if (current_chain !== protocol_chain) {
                await this.metamask.provider.request({
                    method: "wallet_switchEthereumChain",
                    params: [{ chainId: protocol_chain }],
                });
            }
        }
    },
    async mounted() {
        await this.initAvailableProtocols()
        await this.updateProtocolData()
        await this.metamask.sdk.init();
    }
}
</script>

