var navigation = require('./navigation');
var coupon     = require('./coupon');
var stripe     = require('./stripe');
var BulkDelete = require('./bulk-delete');

jQuery(function ($) {
    navigation();
    coupon();
    stripe();

    var bulk_delete = new BulkDelete();
    bulk_delete.listenForEvents();
});
