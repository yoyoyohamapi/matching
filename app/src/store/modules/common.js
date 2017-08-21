import * as types from '../types';
import api from '../../api';

module.exports = {
    state: {
        avatar: null, // 头像文件
        clothing: null, // 选择的上衣
        error: null // 当前错误
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
    },
    actions: {
        [types.REQUEST_MATCHINGS]({ commit, state }) {
            const { avatar, clothing } = state;
            const param = {
                avatar: avatar.file,
                clothing
            };
            api.getMatchings(
                param,
                (data) => {
                    const { matchings, skinColor } = data;
                    commit(types.RECEIVE_MATCHINGS, { matchings });
                    commit(types.SET_SKIN_COLOR, { skinColor });
                },
                (error) => commit(types.SHOW_ERROR, { error: error.message || '请求搭配失败' })
            );
        }
    }
};
