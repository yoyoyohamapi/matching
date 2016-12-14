<template>
    <div class="matching">
        <!-- 上装 -->
        <div class="clothing item">
            <!-- 图片 -->
            <div class="img">
                <img :src="matching.clothing.image"></img>
            </div>
            <!-- 直达链接 -->
            <div class="to">
                <a :href="matching.clothing.url">直达链接</a>
            </div>
        </div>
        <!-- 下装 -->
        <div class="pants item">
            <div class="img">
                <img :src="matching.pants.image"></img>
            </div>
            <div class="to">
                <a :href="matching.pants.url">直达链接</a>
            </div>
        </div>
        <!-- 匹配分数 -->
        <div class="score">
            <h2>{{matching.score}}</h2>
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

.matching > .item {
    width: 80px;
    margin-right: 10px;
    border: 1px solid #eee;
    display: -webkit-flex;
    display: flex;
    flex-direction: column;
}

.matching > .item img{
    width: 80px;
}
</style>
