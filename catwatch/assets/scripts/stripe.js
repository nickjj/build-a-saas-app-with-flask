var typewatch = require('./typewatch');

var stripe = function () {
    var $body = $('body');
    var $form = $('#payment_form');
    var $couponCode = $('#coupon_code');
    var $couponCodeStatus = $('#coupon_code_status');
    var $stripeKey = $('#stripe_key');
    var $paymentErrors = $('.payment-errors');
    var $spinner = $('.spinner');

    var errors = {
        'missing_name': 'You must enter your name.'
    };

    // This identifies your website in the createToken call below.
    Stripe.setPublishableKey($stripeKey.val());

    var stripeResponseHandler = function (status, response) {
        $paymentErrors.hide();

        if (response.error) {
            $spinner.hide();
            $paymentErrors.text(response.error.message);
            $form.find('button').prop('disabled', false);
            $paymentErrors.show();
        }
        else {
            // Token contains id, last 4 digits, and card type.
            var token = response.id;

            // Insert the token into the form so it gets submit to the server.
            var field = '<input type="hidden" id="stripe_token" name="stripe_token" />';
            $form.append($(field).val(token));

            // Process the payment.
            $spinner.show();
            $form.get(0).submit();
        }
    };

    var discountType = function (percent_off, amount_off) {
        if (percent_off) {
            return `${percent_off}%`;
        }

        return `$${amount_off}`;
    };

    var discountDuration = function (duration, duration_in_months) {
        switch (duration) {
            case 'forever':
            {
                return 'forever';
            }
            case 'once':
            {
                return 'first payment';
            }
            default:
            {
                return `for ${duration_in_months} months`;
            }
        }
    };

    var checkCouponCode = function (csrfToken) {
        return $.ajax({
                type: 'POST',
                url: '/subscription/coupon_code',
                data: {coupon_code: $('#coupon_code').val()},
                dataType: 'json',
                beforeSend: function (xhr) {
                    xhr.setRequestHeader('X-CSRFToken', csrfToken);
                    return $couponCodeStatus.text('')
                        .removeClass('alert--success alert--warn alert--error').hide();
                }
            }).done(function (data, status, xhr) {
                var code = xhr.responseJSON.data;
                var amount = `${discountType(code.percent_off,
                                             code.amount_off)} off`;
                var duration = discountDuration(code.duration,
                                                code.duration_in_months);

                return $couponCodeStatus.addClass('alert--success')
                    .text(`${amount} ${duration}`);
            }).fail(function (xhr, status, error) {
                var status_class = 'alert--error';
                if (xhr.status === 404) {
                    status_class = 'alert--warn';
                }

                return $couponCodeStatus.addClass(status_class)
                    .text(xhr.responseJSON.error);
            }).always(function (xhr, status, error) {
                $couponCodeStatus.show();
                return $couponCode.val();
            });
    };

    jQuery(function ($) {
        var lookupDelayInMS = 300;
        var csrfToken = $('meta[name=csrf-token]').attr('content');

        $body.on('keyup', '#coupon_code', function () {
            if ($couponCode.val().length === 0) {
                return false;
            }

            typewatch(function() {
                checkCouponCode(csrfToken);
            }, lookupDelayInMS);
        });

        $body.on('submit', $('form').closest('button'), function () {
            $spinner.show();
        });

        $form.submit(function () {
            var $form = $(this);
            var $name = $('#name');
            $spinner.show();
            $paymentErrors.hide();

            // Custom check to make sure their name exists.
            if ($name.val().length === 0) {
                $paymentErrors.show();
                $spinner.hide();
                $paymentErrors.text(errors.missing_name);
                return false;
            }

            // Disable the submit button to prevent repeated clicks.
            $form.find('button').prop('disabled', true);

            Stripe.card.createToken($form, stripeResponseHandler);

            // Prevent the form from submitting with the default action.
            return false;
        });
    });
};

module.exports = stripe;
