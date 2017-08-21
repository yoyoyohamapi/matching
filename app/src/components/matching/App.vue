<template>
<div class="panel card">
    <!-- 没有获得匹配结果的时候显示loading -->
    <loading v-if="isLoading"></loading>
    <div v-else class="matching">
        <div class="items" v-for="(matching, index) in matchings">
            <!-- <div class="style">{{styleMap[index]}}</div> -->
            <matchingItem class="item" v-bind:matching="matching"></matchingItem>
        </div>
    </div>
</div>
</template>

<script>
import MatchingItem from './MatchingItem';
import Loading from './Loading';
import {
    mapState
} from 'vuex';
import {
    REQUEST_MATCHINGS
} from '../../store/types';

export default {
    name: 'matching',
    data() {
        return {
            styleMap: ['简单', '图案', '花哨', '条纹']
        };
    },
    computed: mapState({
        avatar: state => state.common.avatar,
        clothing: state => state.common.clothing,
        matchings: state => state.matching.matchings,
        isLoading: state => state.matching.isLoading
    }),
    created() {
        if (this.avatar === null || this.clothing === null) {
            this.$router.replace('/');
        } else {
            this.$store.dispatch(REQUEST_MATCHINGS, {
                avatar: this.avatar.file,
                clothing: this.clothing
            });
        }
    },
    components: {
        MatchingItem,
        Loading
    }
};
</script>

<style scoped>
.panel {
    width: 550px;
    min-height: 500px;
    padding: 10px;
    text-align: left;
}

.matching .style {
    font-size: 24px;
    margin-left: -40px;
}

.matching .items:not(:last-child) {
    border-bottom: 1px solid #eee;
    margin-bottom: 5px;
}
</style>
