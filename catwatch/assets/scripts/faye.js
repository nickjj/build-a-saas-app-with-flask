var faye = function () {
    // Add format method to strings.
    String.prototype.format = function () {
        var args = arguments;
        return this.replace(/{(\d+)}/g, function (match, number) {
            return typeof args[number] != 'undefined'
                ? args[number]
                : match
                ;
        });
    };

    var fayeScriptSelector = '#faye';
    var broadcastSelector = '#broadcast';
    var $broadcast = $(broadcastSelector);
    var $emptyStream = $('#empty_stream');
    var channel = '/cats';
    var maxItems = 10;
    var itemSelector = 'div';
    var fayeURL = $(fayeScriptSelector).data('faye-public-url');
    var tweetTemplate = $('#tweetTemplate').html();

    // Avoid duplicate clients and subscriptions.
    if (typeof window.fayeClient === 'undefined') {
        window.fayeClient = new Faye.Client(fayeURL);
    }
    if (window.fayeSubscription) {
        window.fayeSubscription.unsubscribe();
    }

    window.fayeSubscription = window.fayeClient.subscribe(channel, function (message) {
        $emptyStream.hide();

        var template = tweetTemplate.format(message.user,
            message.type,
            message.tweet);
        $broadcast.prepend(template);

        if ($(broadcastSelector + ' > ' + itemSelector).length > maxItems) {
            $(broadcastSelector + ' ' + itemSelector + ':last').remove();
        }
    });
};

module.exports = faye;
