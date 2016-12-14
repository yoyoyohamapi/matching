import * as types from '../types';

module.exports = {
    state: {
        avatar: null, // 头像文件
        clothing: null // 选择的上衣
    },
    mutations: {
        [types.SET_AVATAR](state, payload) {
            state.avatar = payload.avatar;
        },
        [types.SET_CLOTHING](state, payload) {
            state.clothing = payload.clothing;
        },
        [types.SHOW_ERROR](state, payload) {
            state.error = payload.error;
        }
    }
};
