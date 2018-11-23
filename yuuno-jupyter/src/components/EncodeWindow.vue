<template>
    <div class="yuuno--terminal-window">
        <div class="info navbar navbar-default">
            <div class="left">
                <div class="info-group">
                    {{ current }} / {{ length }}
                </div>
            </div>
            <div class="spacer">
                <div class="progress">
                    <div class="bar" :style="{width: `${current/length*100}%`}"></div>
                </div>
            </div>
            <div class="right">
                <div class="info-group" v-if="terminated">
                    <span class="notification_widget btn btn-xs navbar-btn">Terminated</span>
                </div>
                <div class="info-group">
                    <div class="btn-group">
                        <button class="btn btn-xs" :disabled="terminated" @click="interrupt" v-if="!_win32"><i class="fa fa-stop"></i></button>
                        <button class="btn btn-xs" :disabled="terminated" @click="kill"><i class="fa fa-close"></i></button>
                    </div>
                </div>
            </div>
        </div>
        <xterm ref="terminal" @title="updateTitle"></xterm>
    </div>
</template>

<style lang="less" scoped>
.progress {
    height: 100%;

    margin-left: 10px;
    border-right: 1px solid #e7e7e7;
    border-left: 1px solid #e7e7e7;

    background: transparent;

    & > .bar {
        background: linear-gradient(0deg, transparent 40%, #0081dc 40%, #0081dc 60%, transparent 60%);
        height: 100%;
    }
}

.info {
    display: flex;
    justify-content: space-between;

    margin-bottom: 0;
    border-radius: 0;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    border-bottom: 0;
    padding-left: 3px;
    padding-right: 3px;
    
    & > .spacer {
        flex-grow: 1;
        flex-shrink: 1;
    }

    & > .left, & > .right {
        display: flex;
        height: 30px;
        
        flex-grow: 0;
        flex-shrink: 0;
    }

    .navbar-btn {
        margin-right: 0;
    }

    & > .left > .info-group, & > .right > .info-group {
        &:last-child {
            border-right: 0 !important;
            padding-right: 0 !important;
        }

        display: inline-block;
        height: 30px;
        line-height: 30px;
        padding-left: 10px;
        padding-right: 10px;
        border-right: 1px solid #e7e7e7;

        & > .btn-group > .btn {
            padding: 2px 8px;
        }
    }
}
</style>


<script>
import XTerm from './XTerm';

export default {
    name: 'EncodeWindow',
    components: {
        'xterm': XTerm
    },

    props: ['current', 'length', 'terminated', "_win32"],

    data() {
        return {
            title: '',
        }
    },

    methods: {
        updateTitle(title) {
            this.title = title;
        },

        interrupt() {
            this.$emit('interrupt-process');
        },

        kill() {
            this.$emit('kill-process');
        },

        write(data) {
            this.$refs['terminal'].write(data);
        }
    }
}
</script>
