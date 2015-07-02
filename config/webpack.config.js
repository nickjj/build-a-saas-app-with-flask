var fs = require('fs');
var path = require('path');

// Webpack and third party plugins.
var webpack = require('webpack');
var ExtractTextPlugin = require('extract-text-webpack-plugin');
var AutoPrefixerPlugin = require('autoprefixer-core');
var ManifestRevisionPlugin = require('manifest-revision-webpack-plugin');

// Environment detection.
var node_env = process.env.NODE_ENV || 'development';

/*
 Configuration settings
 ------------------------------------------------------------------------------
 */

// Where is your project located relative to this config?
var context = path.join(__dirname, '..');

// Where are your source assets located?
var rootAssetPath = './catwatch/assets';
var contextRoot = path.join(context, rootAssetPath);

// Which human languages do you want to support? (regex)
var languages = /en|es/;

// Where will the files get built to?
var buildOutputPath = './build/public';

// How should certain asset types be configured?
var assets = {
    fonts: {
        path: 'fonts',
        filename: '[path][name].[hash].[ext]'
    },
    images: {
        path: 'images',
        filename: '[path][name].[hash].[ext]'
    },
    scripts: {
        path: 'scripts',
        filename: '[name].[chunkhash].js',
        chunkFilename: '[id].[chunkhash].js'
    },
    styles: {
        path: 'styles',
        filename: '[name].[chunkhash].css'
    }
};

// Which top level JS and CSS files should get output?
var chunks = {
    app_js: [
        path.join(contextRoot, assets.scripts.path, 'entry.js')
    ],
    app_css: [
        path.join(contextRoot, assets.styles.path, 'default.scss')
    ],
    vendor_js: [
        'bootstrap',
        'moment',
        path.join(contextRoot, assets.scripts.path,
            'vendor', 'eonasdan-bootstrap-datetimepicker.4.14.30.min.js')
    ],
    vendor_css: [
        // Bootstrap configuration settings:
        // https://gist.github.com/anonymous/ef4593b01915d647ed88
        // http://getbootstrap.com/customize/?id=ef4593b01915d647ed88
        path.join(contextRoot, assets.styles.path,
            'vendor', 'bootstrap.3.3.5.min.css'),
        path.join(contextRoot, assets.styles.path,
            'vendor', 'font-awesome.4.3.0.css'),
        path.join(contextRoot, assets.styles.path,
            'vendor', 'eonasdan-bootstrap-datetimepicker.4.14.30.min.css')
    ]
};

// Avoid parsing this code to speed up rebuilds.
var noParse = [
    path.join(contextRoot, assets.scripts.path, 'vendor'),
    path.join(contextRoot, assets.styles.path, 'vendor')
];

// Where will assets get served in development mode? This depends on running
// the webpack dev server.
var publicPath = process.env.PUBLIC_PATH || 'http://localhost:2992/assets/';

/*
 Do not edit past this line unless you are tinkering with webpack.
 ------------------------------------------------------------------------------
 */

// Plugins that will load in all environments.
var plugins = [
    // http://webpack.github.io/docs/list-of-plugins.html#noerrorsplugin
    new webpack.NoErrorsPlugin(),

    // http://webpack.github.io/docs/list-of-plugins.html#commonschunkplugin
    new webpack.optimize.CommonsChunkPlugin('vendor_js', 'vendor_js.js'),

    // https://github.com/webpack/extract-text-webpack-plugin
    new ExtractTextPlugin(assets.styles.filename),

    // http://webpack.github.io/docs/list-of-plugins.html#contextreplacementplugin
    new webpack.ContextReplacementPlugin(/moment[\/\\]locale$/, languages),

    // https://github.com/nickjj/manifest-revision-webpack-plugin
    new ManifestRevisionPlugin(path.join('build', 'manifest.json'), {
        rootAssetPath: rootAssetPath,
        ignorePaths: ['/fonts', '/styles', '/scripts']
    })
];

// Development environment only plugins.
if (node_env !== 'development') {
    var developmentPlugins = [
        // http://webpack.github.io/docs/list-of-plugins.html#uglifyjsplugin
        new webpack.optimize.UglifyJsPlugin({compressor: {warnings: false}}),

        // http://webpack.github.io/docs/list-of-plugins.html#dedupeplugin
        new webpack.optimize.DedupePlugin()
    ];

    plugins.push(developmentPlugins[0])
}

module.exports = {
    context: path.join(__dirname, '../'),
    entry: chunks,
    output: {
        path: buildOutputPath,
        publicPath: publicPath,
        filename: assets.scripts.filename,
        chunkFilename: assets.scripts.chunkFilename
    },
    externals: {
        'jquery': 'jQuery'
    },
    resolve: {
        // Allow requiring files without supplying the extension.
        extensions: ['', '.js', '.scss']
    },
    module: {
        noParse: noParse,
        loaders: [
            {
                test: /\.js$/i, loader: 'babel-loader?stage=0',
                exclude: /node_modules/
            },
            {
                test: /\.s?css$/i,
                loader: ExtractTextPlugin.extract('style-loader',
                    'css-loader!postcss-loader!sass-loader?includePaths[]=' + path.join(contextRoot, assets.styles.path))
            },
            {
                test: /\.(jpe?g|png|gif|svg([\?]?.*))$/i,
                loaders: [
                    'file?context=' + rootAssetPath + '&name=' + assets.images.filename,
                    'image?bypassOnDebug&optimizationLevel=7&interlaced=false'
                ]
            },
            {
                test: /\.(woff([\?]?.*)|woff2([\?]?.*))$/i,
                loader: 'url-loader?limit=100000'
            },
            {
                test: /\.(ttf([\?]?.*)|eot([\?]?.*))$/i,
                loader: 'file-loader?context=' + rootAssetPath + '&name=' + assets.fonts.filename
            }
        ]
    },
    plugins: plugins,
    postcss: [AutoPrefixerPlugin()]
};
