import * as types from '../types';

module.exports = {
    state: {
        matchings: [],
        isLoading: true
    },
    mutations: {
        [types.RECEIVE_MATCHINGS](state, payload) {
            state.isLoading = false;
            state.matchings = payload.matchings;
        },
        [types.REQUEST_MATCHINGS](state, payload) {
            state.isLoading = true;
        },
        [types.SHOW_ERROR](state, payload) {
            state.isLoading = false;
        }
    }
};
