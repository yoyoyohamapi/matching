<template>
<div id="app">
    <img src="./assets/logo.jpg" class="logo">
    <div class="container">
        <router-view></router-view>
    </div>
</div>
</template>

<script>
import './assets/global.css';
export default {
    name: 'app'
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
    width: 800px;
}

.logo {
    width: 150px;
}
</style>
