module.exports = {
    experiments: {
        asyncWebAssembly: true
    },
    resolve: {
        extensions: ['.mjs', '.js', '.svelte'],
        mainFields: ['svelte', 'browser', 'module', 'main'],
        fallback: {
            "fs": false
        },
    },
    module: {
        rules: [
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
    }
};
