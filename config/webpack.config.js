var fs = require('fs');
var path = require('path');

var webpack = require('webpack');
var ExtractTextPlugin = require('extract-text-webpack-plugin');
var ManifestRevisionPlugin = require('manifest-revision-webpack-plugin');

var rootAssetPath = './catwatch/assets';

module.exports = {
    context: path.join(__dirname, '../'),
    entry: {
        app_js: [rootAssetPath + '/scripts/entry.js'],
        app_css: [
            rootAssetPath + '/styles/main.scss',
            rootAssetPath + '/styles/vendor/font-awesome.4.3.0.css'
        ]
    },
    output: {
        // Everything will get built to this directory.
        path: './build/public',
        // Assets will be served from this path as its base. This could be
        // swapped out to be a CDN later.
        publicPath: 'http://localhost:2992/assets/',
        filename: '[name].[chunkhash].js',
        chunkFilename: '[id].[chunkhash].js'
    },
    resolve: {
        // Allow requiring files without supplying the extension.
        extensions: ['', '.js', '.scss']
    },
    module: {
        loaders: [
            // Add loaders for a wide array of common extensions.
            {
                test: /\.js$/i, loader: 'babel-loader?stage=0',
                exclude: /node_modules/
            },
            {
                test: /\.s?css$/i,
                // Extract the file name so that we can later output a css
                // file separately in the plugins section.
                loader: ExtractTextPlugin.extract('style-loader', 'css-loader!sass-loader?includePaths[]=' + 'catwatch/assets')
            },
            {
                test: /\.(jpe?g|png|gif|svg([\?]?.*))$/i,
                loaders: [
                    // Optimize images, the filename will get md5'd by default.
                    'file?context=' + rootAssetPath + '&name=[path][name].[hash].[ext]',
                    'image?bypassOnDebug&optimizationLevel=7&interlaced=false'
                ]
            },
            {test: /\.(woff([\?]?.*)|woff2([\?]?.*))$/i, loader: 'url-loader?limit=100000'},
            {
                test: /\.(ttf([\?]?.*)|eot([\?]?.*))$/i,
                loader: 'file-loader?context=' + rootAssetPath + '&name=[path][name].[hash].[ext]'
            },
            {
                test: /\.(wav|mp3)$/i,
                loader: 'file-loader?context=' + rootAssetPath + '&name=[path][name].[hash].[ext]'
            },
            {
                test: /\.(html)$/i,
                loader: 'file-loader?context=' + rootAssetPath + '&name=[path][name].[hash].[ext]'
            },
            {
                test: /\.(md|markdown)$/i,
                loader: 'file-loader?context=' + rootAssetPath + '&name=[path][name].[hash].[ext]'
            }
        ]
    },
    plugins: [
        //new webpack.optimize.CommonsChunkPlugin('common',
        //    'common.[chunkhash].js'),
        new ExtractTextPlugin('[name].[chunkhash].css'),
        new webpack.optimize.UglifyJsPlugin({compressor: {warnings: false}}),
        new webpack.optimize.DedupePlugin(),
        new webpack.DefinePlugin({
            'process.env': {NODE_ENV: JSON.stringify('production')}
        }),
        new webpack.NoErrorsPlugin(),
        new ManifestRevisionPlugin(path.join('build', 'manifest.json'), {
            rootAssetPath: rootAssetPath,
            ignorePaths: ['/fonts', '/styles', '/scripts']
        })
    ]
};