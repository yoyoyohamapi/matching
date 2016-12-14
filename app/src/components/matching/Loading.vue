<template>
<div class="loading">
    <img src="../../assets/loading.png" class="img"></img>
    <div class="title">正在获得推荐</div>
</div>
</template>

<script>
export default {
    name: 'loading'
};
</script>

<style scoped>
@keyframes pound {
    0% {  -webkit-transform:translateY(-20px);}
    50% { -webkit-transform:translateY(-5px);}
    100% { -webkit-transform:translateY(0px);}
}

@keyframes breathe {
    0% {opacity: 0}
    50% { opacity: .5;}
    100% { opacity: 1;}
}

.loading {
}

.loading .img {
    width: 100px;
    margin: 0 auto;
    animation: pound 1s infinite linear;
}

.loading .title {
    color: #0089D0;
    font-weight: 700;
    font-size: 16px;
    animation: breathe 1s infinite linear;
}
</style>
