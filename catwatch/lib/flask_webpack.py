import json

from flask import current_app


class Webpack(object):
    def __init__(self, app=None):
        self.app = app

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Mutate the application passed in as explained here:
        http://flask.pocoo.org/docs/0.10/extensiondev/

        :param app: Flask application
        :return: none
        """

        # Setup a few sane defaults. The stats path allows us to write an
        # informative error if the variable is missing or the path is invalid.
        app.config.setdefault('WEBPACK_STATS_PATH',
                              '/tmp/themostridiculousimpossiblepathtonotexist')

        self._set_asset_paths(app)

        # We only want to refresh the webpack stats in development mode,
        # not everyone sets this setting, so let's assume it's production.
        if app.config.get('DEBUG', False):
            app.before_request(self._refresh_webpack_stats)

        app.add_template_global(self.chunk_url_for)
        app.add_template_global(self.javascript_tag)
        app.add_template_global(self.stylesheet_tag)
        app.add_template_global(self.asset_url_for)

    def _set_asset_paths(self, app):
        """
        Read in the manifest json file which acts as a manifest for assets.
        This allows us to pluck out the asset path as well as hashed names.

        :param app: Flask application
        :return: None
        """
        webpack_stats = app.config['WEBPACK_STATS_PATH']

        try:
            with app.open_resource(webpack_stats) as stats_json:
                stats = json.load(stats_json)

                self.assets_url = stats['publicPath']
                self.asset_chunks = stats['assetsByChunkName']
                self.assets = stats['assets']
        except IOError:
            raise RuntimeError(
                "Flask-Webpack requires the 'WEBPACK_STATS_PATH' config var "
                "to be set and it must be a valid webpack stats json file.")

    def _refresh_webpack_stats(self):
        """
        Refresh the webpack stats so we get the latest version. It's a good
        idea to only use this in development mode.

        :return: None
        """
        self._set_asset_paths(current_app)

    def chunk_url_for(self, endpoint=None, chunk='', endswith='js'):
        """
        Lower level access to a chunk, you need to supply the tag. For example
        you may want to use the hot reloading feature of webpack-dev-server:

            <script src="{{ chunk_url_for('webpack-dev-server') }}"></script>

        :param endpoint: Asset url, this can be a full url or relative path
        :type endpoint: str
        :param chunk: File name to lookup in the hash
        :type chunk: str
        :param endswith: Extension of the file name
        :type endswith: str
        :return: The asset path
        """
        if endpoint is None:
            endpoint = self.assets_url

        assets = self.asset_chunks.get(chunk, '')

        if not isinstance(assets, list):
            assets = assets.split()

        for asset in assets:
            if asset.endswith(endswith):
                return '{0}{1}'.format(endpoint, asset)

    def javascript_tag(self, *args):
        """
        Convenience tag to output 1 or more javascript tags.

        :param *args: 1 or more javascript file names
        :return: Script tag(s) containing the asset
        """
        tags = []

        for arg in args:
            asset_path = self.chunk_url_for(self.assets_url, arg)
            tags.append('<script src="{0}"></script>'.format(asset_path))

        return '\n'.join(tags)

    def stylesheet_tag(self, *args):
        """
        Convenience tag to output 1 or more stylesheet tags.

        :param *args: 1 or more stylesheet file names
        :return: Link tag(s) containing the asset
        """
        tags = []

        for arg in args:
            asset_path = self.chunk_url_for(self.assets_url, arg, 'css')
            tags.append(
                '<link rel="stylesheet" href="{0}">'.format(asset_path))

        return '\n'.join(tags)

    def asset_url_for(self, asset):
        """
        Lookup the hashed asset path of a file name unless it starts with
        something that resembles a web address, then take it as is.

        :param asset: A logical path to an asset
        :type asset: str
        :return: The asset path or None if not found
        """
        if asset.startswith('//') or asset.startswith('http://') or \
                asset.startswith('https://'):
            return asset

        for key in self.assets:
            if key == asset:
                return '{0}{1}'.format(self.assets_url, self.assets[key])

        return None
