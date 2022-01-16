module.exports = {
    entry: "./src/index.ts",
    output: {
        filename: "../../../yuuno_ipython/static/extension/index.js",
        library: {
            type: "amd"
        }
    },
    experiments: {
        asyncWebAssembly: true
    },
    resolve: {
        extensions: ['.mjs', '.js', '.tsx', '.ts', '.svelte'],
        mainFields: ['svelte', 'browser', 'module', 'main'],
        fallback: {
            "fs": false
        },
    },
    externals: [
        "@jupyter-widgets/base"
    ],
    module: {
        rules: [
            {
                test: /\.(png|jpe?g|gif|svg)(\?.*)?$/,
                use: ["url-loader"],
            },
            {
                test: /\.css$/i,
                use: ["style-loader", "css-loader"],
            },
            {
                test: /\.tsx?$/,
                use: 'ts-loader',
                exclude: /node_modules/,
            },
            {
                test: /\.svelte$/,
                use: 'svelte-loader'
            },
            {
                // required to prevent errors from Svelte on Webpack 5+, omit on Webpack 4
                test: /node_modules\/svelte\/.*\.mjs$/,
                resolve: {
                   fullySpecified: false
                }
            },
        ]
    },
};
