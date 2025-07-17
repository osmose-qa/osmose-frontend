const SpritezeroWebpackPlugin = require('spritezero-webpack-plugin');
const path = require('path');

module.exports = (env, argv) => {
    return {
        entry: {
        },
        output: {
            path: path.resolve(__dirname, '../public/assets'),
        },
        plugins: [
            new SpritezeroWebpackPlugin({
                source: 'images/**/*.svg',
                output: 'marker-gl-',
            })
        ],
    }
};
