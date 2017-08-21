<template>
<div class="color card">
    <div class="type" v-for="(hexColors, key) in color">
        <h4>{{map[key]}}</h4>
        <ul>
            <li v-for="hex in hexColors">
                <div v-bind:class="[{actived: skinColor===hex},'hex']" v-bind:style="{ backgroundColor: hex }">
                </div>
                <div class="hexName">
                    {{hex}}
                </div>
            </li>
        </ul>
    </div>
</div>
</template>

<script>
import {
    mapState
} from 'vuex';

export default {
    name: 'color',
    computed: mapState({
        skinColor: state => state.avatar.skinColor
    }),
    props: ['color', 'map']
};
</script>

<style scoped>
.color {
    padding: 5px 10px;
    text-align: left;
}

.color .type h4 {
    margin: 0
}

.color .type ul {
    padding: 5px 0px 10px 10px;
    margin: 0;
}

.color .type ul>li {
    list-style: none;
    display: flex;
}

.color .type ul>li .hex {
    flex: 1 1 50%;
    height: 15px;
    margin-bottom: 5px;
    border: 1px solid #000;
}

.color .type ul>li .hexName {
    flex: 1 1 50%;
    margin-left: 5px;
}

.color .type ul>li .hex.actived {
    border: 3px solid red;
}
</style>
