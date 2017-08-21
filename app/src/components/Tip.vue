<template>
    <div class="tip card" v-if="error">{{error}}</div>
</template>

<script>
import {
    mapState
} from 'vuex';

export default {
    name: 'tip',
    computed: mapState({
        error: state => state.common.error
    })
};
</script>

<style scoped>
.tip.card{
    padding: 10px;
}
</style>
