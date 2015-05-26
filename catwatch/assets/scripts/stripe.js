var stripe = function() {
    var $form = $('#payment_form');
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

    jQuery(function ($) {
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