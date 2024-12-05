/*
Core logic/payment flow for this comes from here:
https://stripe.com/docs/payments/accept-a-payment
CSS from here:
https://stripe.com/docs/stripe-js
*/

// Get Stripe public key and client secret
const stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
const clientSecret = document.getElementById('id_client_secret').textContent.trim();

if (!clientSecret) {
    console.error('Client secret is missing');
    return;
}

console.log('Stripe Public Key:', stripePublicKey);
console.log('Client Secret:', clientSecret);

// Initialize Stripe
const stripe = Stripe(stripePublicKey);
const elements = stripe.elements();

// Style the card element
const style = {
    base: {
        color: '#000',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4'
        }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};

const card = elements.create('card', { style: style });
card.mount('#card-element');

// Handle realtime validation errors
card.addEventListener('change', ({ error }) => {
    const errorDiv = document.getElementById('card-errors');
    if (error) {
        const html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${error.message}</span>
        `;
        $(errorDiv).html(html);
    } else {
        errorDiv.textContent = '';
    }
});

const form = document.getElementById('payment-form');

form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    card.update({ 'disabled': true });
    $('#submit-button').attr('disabled', true);
    $('#payment-form').fadeToggle(100);
    $('#loading-overlay').fadeToggle(100);

    const saveInfo = Boolean($('#id-save-info').attr('checked'));
    const csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    const postData = {
        'csrfmiddlewaretoken': csrfToken,
        'client_secret': clientSecret,
        'save_info': saveInfo,
    };

    try {
        await $.post('/your-endpoint/', postData);
        const result = await stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
                billing_details: {
                    name: $.trim(form.full_name.value),
                    email: $.trim(form.email.value),
                    address: {
                        line1: $.trim(form.street_address1.value),
                        line2: $.trim(form.street_address2.value),
                        city: $.trim(form.town_or_city.value),
                        country: $.trim(form.country.value),
                        state: $.trim(form.county.value),
                    }
                }
            }
        });

        if (result.error) {
            const errorDiv = document.getElementById('card-errors');
            const html = `
                <span class="icon" role="alert">
                <i class="fas fa-times"></i>
                </span>
                <span>${result.error.message}</span>`;
            $(errorDiv).html(html);
            $('#payment-form').fadeToggle(100);
            $('#loading-overlay').fadeToggle(100);
            card.update({ 'disabled': false });
            $('#submit-button').attr('disabled', false);
        } else if (result.paymentIntent.status === 'succeeded') {
            form.submit();
        }
    } catch (error) {
        console.error('Error during payment process:', error);
    }
});
