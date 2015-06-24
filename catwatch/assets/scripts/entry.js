var moment = require('moment');

var coupon = require('./coupon');
var stripe = require('./stripe');
var BulkDelete = require('./bulk-delete');
var faye = require('./faye');

$(document).ready(function () {
    moment.locale($('body').data('locale'));

    coupon();
    stripe();

    var bulk_delete = new BulkDelete();
    bulk_delete.listenForEvents();

    if (window.location.pathname === '/live_stream') {
        faye();
    }

    $('.from-now').each(function (i, e) {
        (function updateTime() {
            var time = moment($(e).data('datetime'));
            $(e).text(time.fromNow());
            $(e).attr('title', time.format('MMMM Do YYYY, h:mm:ss a Z'));
            setTimeout(updateTime, 1000);
        })();
    });

    $('.short-date').each(function (i, e) {
        var time = moment($(e).data('datetime'));
        $(e).text(time.format('MMM Do YYYY'));
        $(e).attr('title', time.format('MMMM Do YYYY, h:mm:ss a Z'));
    });
});
