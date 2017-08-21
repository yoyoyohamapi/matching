<template>
<div id="avatarCard" class="panel card">
    <div class="avatar">
        <!--  -->
        <div class="hidden">
            <input type="file" id="avatarInput" name="avatar" />
        </div>
        <div v-if="!avatar" class="button button-large" id="upload">上传头像</div>
        <div v-else>
            <img id="avatarImage" :src="avatar.url"></img>
        </div>
    </div>
    <transition name="slide-fade">
        <div class="clothing-list" v-if="avatar">
            <div class="button item" v-clothing="clothing" v-for="clothing in clothings" :key="clothing.value">
                {{clothing.title}}
            </div>
        </div>
    </transition>
</div>
</template>

<script>
/* global FileReader */
import clothings from '../../constants/clothings';
import Rx from 'rxjs/Rx';
import {
    mapState
} from 'vuex';

import {
    SET_AVATAR,
    SET_CLOTHING
} from '../../store/types';

export default {
    name: 'avatar',
    data() {
        return {
            clothings
        };
    },
    computed: mapState({
        avatar: state => state.common.avatar,
        clothing: state => state.common.clothing
    }),
    directives: {
        clothing(el, binding, vnode) {
            // 选择
            const self = vnode.context;
            const clothing = binding.value;
            const clickStream$ = Rx.Observable.fromEvent(el, 'click').map(() => clothing);
            self.$subscribeTo(clickStream$, (clothing) => {
                self.$store.commit(SET_CLOTHING, {
                    clothing: clothing.value
                });
                self.$router.replace('matching');
            });
        }
    },
    subscriptions() {
        // 显示文件选择框的点击流
        const showFileSelectorClick$ = this.$fromDOMEvent('#upload', 'click');
        showFileSelectorClick$.subscribe(() => {
            this.$el.querySelector('#avatarInput').click();
        });
        // 头像改变流
        const avatarChange$ = this.$fromDOMEvent('#avatarInput', 'change')
            .pluck('target', 'files', 0).distinctUntilChanged();
        // 头像读取流
        const avatar$ = avatarChange$.flatMap((file) => {
            return Rx.Observable.create((observer) => {
                const reader = new FileReader();
                reader.readAsDataURL(file);
                reader.onload = function onload() {
                    // push avatar url for observer
                    // ---(url)-----(url)--------
                    const avatar = {
                        file,
                        url: this.result
                    };
                    observer.next(avatar);
                };
                reader.onerror = function onerror(e) {
                    observer.onError(e);
                };
            });
        });
        avatar$.subscribe((avatar) => {
            this.$store.commit(SET_AVATAR, {
                avatar
            });
        });
    }
};
</script>

<style scoped>
.panel {
    width: 550px;
}

.avatar {
    justify-content: center;
    align-items: center;
    width: 450px;
    height: 450px;
    display: -webkit-flex;
    display: flex;
    -webkit-order: 1;
    order: 2;
}

.avatar img {
    width: 400px;
    height: 400px;
}

.avatar .button {
    color: red;
    font-weight: 700;
    border: 1px solid red;
}

.clothing-list {
    width: 100px;
    height: 450px;
    -webkit-order: 2;
    order: 2;
    display: flex;
    display: -webkit-flex;
    flex-direction: column;
    background-color: #3D4456;
}

.clothing-list .item {
    flex-grow: 1;
    background-color: #3D4456;
    color: white;
}

.slide-fade-enter-active {
    transition: all 0.3s ease;
}

.slide-fade-enter,
.slide-fade-leave-active {
    margin-left: -100px;
    opacity: 0;
}
</style>
