var webpack = require('webpack');
const TerserPlugin = require('terser-webpack-plugin');
const { VueLoaderPlugin } = require('vue-loader');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const path = require('path');


module.exports = (env, argv) => {
    return {
        entry: {
            "app": "./src/webpack.index.js",
        },
        output: {
            path: path.resolve(__dirname, 'public/assets'),
            filename: "[name]/webpack.bundle-[contenthash].js",
            publicPath: env && env.DEV_SERVER ? "/" : "/assets/",
        },
        devtool: argv.mode === 'development' ? 'source-map' : void 0,
        resolve: {
            extensions: ['.ts', '...'],
            alias: {
                vue: argv.mode === 'development' ? 'vue/dist/vue.js' : 'vue/dist/vue.min.js'
            },
        },
        module: {
            rules: [
                {
                    test: /\.ts$/,
                    loader: 'babel-loader',
                    options: {
                        presets: [['babel-preset-typescript-vue']],
                    }
                },
                /*
                {
                    enforce: "pre",
                    test: /\.js$/,
                    exclude: [
                        /node_modules/,
                        /geobuf-.*\.js/,
                        /sorttable\.js/,
                        /webpack.bundle.*\.js/
                    ],
                    loader: 'eslint-loader',
                    options: {
                        cache: true,
                    }
                },
                */
                {
                    test: /\.js$/,
                    exclude: /node_modules/,
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-env']
                    }
                },
                {
                    test: /\.vue$/,
                    loader: 'vue-loader',
                    options: {
                        hotReload: env && env.DEV_SERVER
                    }
                },
                {
                    test: /\.css$/,
                    use: [
                        { loader: "style-loader" },
                        { loader: "css-loader" },
                    ]
                },
                {
                    test: /\.(png|gif)$/,
                    type: 'asset/resource',
                },
                {
                    test: /\.po$/,
                    type: "json",
                    use: [{
                        loader: "po-loader",
                        options: {
                            format: "mf",
                            "fallback-to-msgid": true,
                        }
                    }]
                },
            ]
        },
        optimization: {
            minimizer: [
                new TerserPlugin({
                    parallel: true,
                    terserOptions: {
                        ecma: 6,
                    },
                }),
            ]
        },
        plugins: [
            new HtmlWebpackPlugin({
                template: "src/index.html",
                chunks: ["app"],
                inject: "body", // Inject all scripts into the body
                filename: "index.html"
            }),
            new webpack.DefinePlugin({
                API_URL: '(window.API_URL || "")',
            }),
            new VueLoaderPlugin(),
        ],
        devServer: {
            historyApiFallback: true,
            open: "en/map/",
            compress: true,
            host: "0.0.0.0"
        },
    }
};
