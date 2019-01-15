<template>
    <div>
        <table class="metadata-table">
            <template v-if="!!format">
                <tr><td class="metadata-section" colspan="2">Color Format</td></tr>
                <tr><td class="key">Color-Family</td><td class="value">{{ format[0] }}</td></tr>
                <tr><td class="key">Bit-Depth</td><td class="value">{{ format[1] }}bits</td></tr>
                <tr><td class="key">Sample-Type</td><td class="value">{{ format[2] }}</td></tr>

                <template v-if="format[0] === 'YUV'">
                    <tr>
                        <td class="key">Subsampling</td>
                        <td class="value" v-if="     format[3] === 0 && format[4] === 0">4:4:4</td>
                        <td class="value" v-else-if="format[3] === 1 && format[4] === 0">4:2:2</td>
                        <td class="value" v-else-if="format[3] === 1 && format[4] === 1">4:2:0</td>
                        <td class="value" v-else>W:{{ format[3] }} H:{{ format[4] }}</td>
                    </tr>
                </template>
            </template>

            <template v-if="Object.keys(clipmeta).length > 0">
                <tr><td class="metadata-section" colspan="2">Clip Properties</td></tr>
                <tr :key="key" v-for="(value, key) in clipmeta">
                    <td class="key">{{ key }}</td>
                    <td class="value">{{ value }}</td>
                </tr>
            </template>

            <template v-if="Object.keys(table).length > 0">
                <tr><td class="metadata-section" colspan="2">Frame Properties</td></tr>
                <tr :key="key" v-for="(value, key) in table">
                    <td class="key">{{ key }}</td>
                    <td class="value">{{ value }}</td>
                </tr>
            </template>
        </table>
    </div>
</template>
<style lang="less" scoped>
@background-key: rgb(228, 228, 228);
@background-value: lighten(@background-key, 5%);

.metadata-section {
    font-weight: bold;
    border-bottom: 2px solid darken(@background-key, 10%);
}

.metadata-table {
    width: 100%;

    & > tr {
        &:hover {
            & > .key {
                background: lighten(@background-key, 10%);
            }

            & > .value {
                background: lighten(@background-value, 10%);
            }
        }

        & > .key {
            font-weight: bold;
            text-align: left;
            padding-left: 5px;
            background: @background-key;
        }
        & > .value {
            background: @background-value;
        }
    }
}
</style>
<script>
export default {
    name: 'MetadataTable',
    props: ['table', 'format', 'clipmeta']
}
</script>


