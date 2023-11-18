<template>
    <div>
        <div class="grid p-fluid">
            <div class="col-12 xl:col-2">
                <h4 for="protocol_selector" class="block mb-2"> Select a protocol </h4>
                <Dropdown v-model="selectedProtocol" editable :options="availableProtocols" optionLabel="name"
                    placeholder="Select a protocol" class="w-full md:w-14rem" @change="updateProtocolData"
                    inputId="protocol_selector" />
            </div>
            <div class="col-12 xl:col-8">
                <div v-if="!metamask.connected" class="grid p-fluid">
                    <Message severity="error">Please, connect your Metamask account to get personalized results</Message>
                </div>
            </div>
            <div v-if="!metamask.connected" class="col-12 xl:col-2" style="align: right;">
                <Button label="Connect Metamask" raised size="large" @click="connectMetamask" />
            </div>
            <div v-else class="col-12 xl:col-2" style="align: right;">
                <Button label="Disconnect Metamask" raised size="large" @click="terminateMetamask" />
            </div>
        </div>
        <div v-if="metamask.connected" class="grid p-fluid">
            <div class="col-12 xl:col-6">
                <div class="grid p-fluid">
                    <div class="col-12 xl:col-2"></div>
                    <div class="col-12 xl:col-8">
                        <div class="card">
                            You have a {{ 100 * returnProbability }}% probability of returning to the protocol
                        </div>
                    </div>
                    <div class="col-12 xl:col-2"></div>
                    <div class="col-12 xl:col-2"></div>
                    <div class="col-12 xl:col-8">
                        <div class="card">
                            You are in the {{ percentile }} percentile of users by probability of returning to the protocol
                        </div>
                    </div>
                    <div class="col-12 xl:col-2"></div>
                    <div class="col-12 xl:col-2"></div>
                    <div class="col-12 xl:col-8">
                        <div class="card">
                            You are elegible for {{ tokens }} tokens
                        </div>
                    </div>
                    <div class="col-12 xl:col-2"></div>
                    <div class="col-12 xl:col-2"></div>
                    <div class="col-12 xl:col-8">
                        <Button label="Claim tokens" raised size="large" @click="sendTransaction" />
                    </div>
                    <div class="col-12 xl:col-2"></div>
                </div>
            </div>
            <div class="col-12 xl:col-6">
                <div class="card">
                    <h5>Shap graph</h5>
                    <img :src="shapGraph" style="width: 100%" />
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import { MetaMaskSDK } from '@metamask/sdk';
import { ref } from 'vue';

async function getAvailableProtocols() {
    const url = "http://127.0.0.1:8000/protocols"

    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data; // Return the data
    } catch (error) {
        console.error('There was an error fetching the data:', error);
        return null; // Return null or appropriate error handling
    }
}

async function fetchUserStats(protocol) {
    const url = "http://127.0.0.1:8000/results/" + protocol

    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data; // Return the data
    } catch (error) {
        console.error('There was an error fetching the data:', error);
        return null; // Return null or appropriate error handling
    }
}

async function fetchShapGraph(protocol, address) {
    const url = "http://127.0.0.1:8000/graphs/shap/" + protocol + "/" + address

    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data; // Return the data
    } catch (error) {
        console.error('There was an error fetching the data:', error);
        return null; // Return null or appropriate error handling
    }
}

export default {
    data() {
        return {
            availableProtocols: [],
            selectedProtocol: null,
            metamask: {
                sdk: null,
                provider: null,
                address: null,
            },
            returnProbability: null,
            percentile: null,
            tokens: null,
            shapGraph: null,
        }
    },
    created() {
        this.metamask.sdk = new MetaMaskSDK({
            dappMetadata: {
                url: window.location.href,
                name: "Smart incentives dashboard",
            },
            checkInstallationImmediately: false,
        })
    },
    methods: {
        async updateUserStats() {
            const userStats = await fetchUserStats(this.selectedProtocol.code)
            this.userStats = userStats
        },
        async getAddress() {
            const accounts = await this.metamask.provider.request({
                method: "eth_requestAccounts",
            });
            return accounts[0];
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
        async getAddress() {
            const accounts = await this.metamask.provider.request({
                method: "eth_requestAccounts",
            });
            return accounts[0];
        },
        async updateAddress() {
            this.metamask.address = await this.getAddress()
        },
        async updateUserReturnProbability() {
            this.returnProbability = this.userStats.user_probas[this.metamask.address]
        },
        async updateUserPercentile() {
            const users_below = Object.values(this.userStats.user_probas).filter(
                (user_proba) => {
                    return user_proba > this.returnProbability
                }
            ).length
            const total_users = Object.values(this.userStats.user_probas).length

            this.percentile = 100 * users_below / total_users
        },
        async updateUserTokens() {
            // TODO: Get real data
            const airdrop_amount = 10000
            const airdrop_ratio = 0.02
            this.tokens = airdrop_amount * airdrop_ratio
        },
        async updateUserData() {
            await this.updateUserStats()
            await this.updateUserReturnProbability()
            await this.updateUserPercentile()
            await this.updateUserTokens()
            await this.updateShapGraph()
        },
        async updateShapGraph() {
            const shapGraph = await fetchShapGraph(this.selectedProtocol.code, this.metamask.address)
            const imageBase64 = shapGraph.image
            const fullShapGraph = "data:image/png;base64, " + imageBase64
            this.shapGraph = fullShapGraph
        },
        async connectMetamask() {
            this.metamask.provider = await this.metamask.sdk.getProvider();
            await this.getAddress()
            this.metamask.connected = true

        },
        async terminateMetamask() {
            await this.metamask.sdk.terminate()
            this.metamask.connected = false
        },
        async sendTransaction() {
            const contractAddress = "0xB2e3618B865b4f200B2d1803640d00557452aE1E";
            const data = '0x03ca98cb0000000000000000000000000000000000000000000000000000000000000010';
            if (!this.metamask.provider) {
                this.metamask.provider = await this.metamask.sdk.getProvider();
            }
            this.metamask.provider.request({
                method: "eth_sendTransaction",
                params: [
                    {
                        from: await this.getAddress(),
                        to: contractAddress,
                        data: data,
                    }
                ]
            })
        },
        async updateProtocolData() {
            await this.updateUserData()
        }
    },
    async mounted() {
        await this.initAvailableProtocols()
        await this.updateUserData()
        await this.metamask.sdk.init();
        this.metamask.provider = await this.metamask.sdk.getProvider();
    }
}

</script>