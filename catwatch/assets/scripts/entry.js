var coupon = require('./coupon');
var stripe = require('./stripe');
var BulkDelete = require('./bulk-delete');
var faye = require('./faye');

$(document).ready(function() {
    coupon();
    stripe();

    var bulk_delete = new BulkDelete();
    bulk_delete.listenForEvents();

    if (window.location.pathname === '/live_stream') {
        faye();
    }
});
