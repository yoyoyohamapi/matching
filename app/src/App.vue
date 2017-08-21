<template>
<div id="app">
    <div class="tipContainer">
        <tip></tip>
    </div>
    <div class="container">
        <a href="/">
            <img src="./assets/logo.jpg" class="logo">
        </a>
        <router-view></router-view>
    </div>
    <div class="skinColor">
        <color v-bind:color="skinColor" v-bind:map="skinColorMap"></color>
    </div>
</div>
</template>

<script>
import './assets/global.css';
import Tip from './components/Tip';
import Color from './components/Color';
import skinColor from '../../config/face_color.json';

const skinColorMap = {
    'cold_white': '白皙',
    'red_white': '红润',
    'wheat': '小麦色',
    'yellow': '偏黄',
    'black': '黝黑'
};

export default {
    name: 'app',
    data() {
        return {
            skinColor,
            skinColorMap
        };
    },
    components: {
        Tip,
        Color
    }
};
</script>

<style>
#app {
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: #2c3e50;
    margin: 0 auto;
    margin-top: 60px;
    width: 1200px;
    display: flex;
    -webkit-align-items: center;
    align-items: center;
    -webkit-justify-content: center;
    justify-content: center;
}

.logo {
    width: 150px;
}

.tipContainer {
    position: fixed;
    left: 0;
    top: 0;
    width: 100%;
}

.skinColor {
    width: 200px;
    margin-top: 150px;
    margin-left: 50px;
}
</style>
