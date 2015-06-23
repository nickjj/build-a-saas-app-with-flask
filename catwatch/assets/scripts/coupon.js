var rome = require('rome');

var coupon = function () {
    var durationSelector = '#duration';

    var $body = $('body');
    var $duration = $(durationSelector);
    var $durationInMonths = $('#duration-in-months');
    var $redeem_by = $('#redeem_by');

    $body.on('change', durationSelector, function () {
        if ($duration.val() === 'repeating') {
            $durationInMonths.show();
        }
        else {
            $durationInMonths.hide();
        }
    });

    if ($redeem_by.length) {
        rome(redeem_by, {
            min: new Date(),
            inputFormat: 'YYYY-MM-DD HH:mm:ss',
            timeInterval: 300
        });
    }
};

module.exports = coupon;
