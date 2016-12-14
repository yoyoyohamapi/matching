import * as types from '../types';
import api from '../../api';

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
    },
    actions: {
        [types.REQUEST_MATCHINGS]({ commit, state }) {
            const { avatar, clothing } = state;
            const param = {
                avatar,
                clothing
            };
            api.getMatchings(
                param,
                (data) => {
                    const { matchings } = data;
                    commit(types.RECEIVE_MATCHINGS, { matchings });
                },
                (error) => commit(types.SHOW_ERROR, error.message || '请求搭配失败')
            );
        }
    }
};
