const WPPlugin = require('@jupyterlab/builder').WPPlugin;
const fs = require("fs");
const path = require("path");

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
    },
    plugins: [
        new WPPlugin.JSONLicenseWebpackPlugin({
            outputFilename: "../third-party-licenses.json",
            additionalModules: [
                {
                    name: "@yuuno/jupyterlab",
                    directory: __dirname
                }
            ],
            licenseTextOverrides: {
                "@yuuno/jupyterlab": fs.readFileSync(path.resolve(".", "..", "..", "COPYING")) + "\n--------------------------------\n" + fs.readFileSync(path.resolve(".", "..", "..", "COPYING.EXCEPTIONS"))
            }
        })
    ]
};
