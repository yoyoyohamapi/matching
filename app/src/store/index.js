import Vue from 'vue';
import Vuex from 'vuex';
import avatar from './modules/avatar';
import common from './modules/common';
import matching from './modules/matching';

Vue.use(Vuex);

export default new Vuex.Store({
    modules: {
        avatar,
        common,
        matching
    }
});
