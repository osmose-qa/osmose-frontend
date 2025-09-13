const SpritezeroWebpackPlugin = require('spritezero-webpack-plugin');
const path = require('path');

module.exports = (env, argv) => {
    return {
        entry: {
        },
        output: {
            path: path.resolve(__dirname, '.'),
        },
        plugins: [
            new SpritezeroWebpackPlugin({
                source: '{markers/*.svg,limit.svg}',
                output: 'marker-gl-',
            })
        ],
    }
};
