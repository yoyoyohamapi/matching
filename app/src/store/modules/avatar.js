import * as types from '../types';

module.exports = {
    state: {
        skinColor: null
    },
    mutations: {
        [types.SET_SKIN_COLOR](state, payload) {
            state.skinColor = payload.skinColor;
        }
    }
};
