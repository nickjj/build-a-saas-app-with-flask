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
        $redeem_by.datetimepicker({
            widgetParent: '.dt',
            format: 'YYYY-MM-DD HH:mm:ss',
            icons: {
                time: 'fa fa-clock-o',
                date: 'fa fa-calendar',
                up: 'fa fa-arrow-up',
                down: 'fa fa-arrow-down',
                previous: 'fa fa-chevron-left',
                next: 'fa fa-chevron-right',
                clear: 'fa fa-trash'
            }
        });
    }
};

module.exports = coupon;
