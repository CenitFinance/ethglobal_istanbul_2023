import AppLayout from '@/layout/AppLayout.vue';
import { createRouter, createWebHashHistory } from 'vue-router';

const router = createRouter({
    history: createWebHashHistory(),
    routes: [
        {
            path: '/',
            component: AppLayout,
            children: [
                {
                    path: '/',
                    name: 'protocol',
                    component: () => import('@/views/Protocol.vue')
                },
            ]
        },
        {
            path: '/user',
            component: AppLayout,
            children: [
                {
                    path: '/user',
                    name: 'user',
                    component: () => import('@/views/User.vue')
                },
            ]
        }
    ]
})

export default router;
