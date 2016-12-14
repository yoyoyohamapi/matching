import Vue from 'vue';
import App from './App';
import Matching from './components/matching/App';
import Index from './components/index/App';
import VueRouter from 'vue-router';
import Rx from 'rxjs/Rx';
import VueRx from 'vue-rx';
import Vuex from 'vuex';

import store from './store';

Vue.use(VueRouter);
Vue.use(Vuex);
Vue.use(VueRx, Rx);

const routes = [
    { path: '/matching', component: Matching },
    { path: '/', component: Index }
];

/* eslint-disable no-new */
const router = new VueRouter({
    routes
});

/* eslint-disable no-new */
new Vue({
    el: '#app',
    template: '<App/>',
    store,
    components: { App },
    router
});
