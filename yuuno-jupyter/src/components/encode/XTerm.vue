<template>
    <div ref="xterm"></div>
</template>

<script>
import { Terminal } from 'xterm';
import { fit } from 'xterm/lib/addons/fit/fit';
import 'xterm/lib/xterm.css';

export default {
    name: "XTerm",

    mounted() {
        this._xterm = new Terminal();
        this._xterm.open(this.$refs['xterm']);

        ["blur", "focus", "linefeed", "selection", "data", "key", "keypress", "refresh", "resize", "scroll", "title"].forEach(
            (n) => this._xterm.on(n, (...args) => this.$emit(n, args))
        );
        fit(this._xterm);
    },

    beforeDestroy() {
        this._xterm.dispose();
    },

    methods: {
        write(...args) {
            this._xterm.write(...args);
        },

        clear(...args) {
            this._xterm.clear();
        },

        blur() {
            this._xterm.blur();
        },

        focus() {
            this._xterm.focus();
        }
    }

}
</script>

<style>

</style>
