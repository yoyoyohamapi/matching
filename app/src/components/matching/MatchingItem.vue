<template>
<div class="matching">
    <!-- 上装 -->
    <div class="clothing item" v-for="clothing in matching">
        <!-- 图片 -->
        <a class="img" target="_blank" :href="clothing.url">
            <img :src="clothing.image"></img>
        </a>
    </div>
</div>
</template>

<script>
export default {
    name: 'matchingItem',
    props: ['matching']
};
</script>

<style scoped>
.matching {
    display: -webkit-flex;
    display: flex;
    flex-direction: row;
    justify-content: flex-start;
    padding: 5px;
}

.matching>.item {
    width: 100px;
    margin-right: 10px;
    border: 1px solid #eee;
    display: -webkit-flex;
    display: flex;
    flex-direction: column;
}

.matching>.item img {
    display: block;
    width: 100%;
}
</style>
