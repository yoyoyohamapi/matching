<template>
<div class="panel card">
    <!-- 没有获得匹配结果的时候显示loading -->
    <loading v-if="isLoading"></loading>
    <div v-else class="matching">
        <div class="items">
            <matchingItem v-bind:matching="matching" v-for="matching in matchings"></matchingItem>
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
}
</style>
