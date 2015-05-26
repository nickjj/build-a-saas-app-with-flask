var navigation = require('./navigation');
var stripe     = require('./stripe');
var BulkDelete = require('./bulk-delete');

jQuery(function ($) {
    navigation();
    stripe();

    var bulk_delete = new BulkDelete();
    bulk_delete.listenForEvents();
});
