/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment
*/
console.log('Stripe Elements JS Loaded');
// Get Stripe public key
const stripePublicKey = document.getElementById('id_stripe_public_key').textContent.trim().slice(1, -1);
// Get client secret directly from the input field
const clientSecret = document.getElementById('id_client_secret').value.trim();

console.log('Debug - JS Public Key:', stripePublicKey);
console.log('Debug - JS Client Secret:', clientSecret);

if (!clientSecret) {
    console.error('Client secret is missing');
    document.getElementById('card-errors').textContent = 'Configuration error. Please contact support.';
    document.getElementById('submit-button').disabled = true;
    throw new Error('Invalid client secret format');
}

// Initialize Stripe
const stripe = Stripe(stripePublicKey);
const elements = stripe.elements();

// Create card element
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

const card = elements.create('card', {style: style});
card.mount('#card-element');

// Handle realtime validation errors on the card element
card.addEventListener('change', function (event) {
    const errorDiv = document.getElementById('card-errors');
    if (event.error) {
        const html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>
        `;
        errorDiv.innerHTML = html;
    } else {
        errorDiv.textContent = '';
    }
});

// Handle form submit
const form = document.getElementById('payment-form');

form.addEventListener('submit', async function(ev) {
    ev.preventDefault();
    
    try {
        // Disable form and show loading
        card.update({ 'disabled': true});
        $('#submit-button').prop('disabled', true);
        $('#payment-form').fadeToggle(100);
        $('#loading-overlay').fadeToggle(100);

        // Get the client secret
        const clientSecret = document.getElementById('id_client_secret').value.trim();
        
        // Confirm the payment
        const { paymentIntent, error } = await stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
                billing_details: {
                    name: $.trim(form.full_name.value),
                    email: $.trim(form.email.value),
                    phone: $.trim(form.phone_number.value),
                    address: {
                        line1: $.trim(form.street_address1.value),
                        line2: $.trim(form.street_address2.value),
                        city: $.trim(form.town_or_city.value),
                        state: $.trim(form.county.value),
                        country: $.trim(form.country.value),
                        postal_code: $.trim(form.postcode.value),
                    }
                }
            }
        });

        if (error) {
            throw error;
        }

        if (paymentIntent.status === 'succeeded') {
            form.submit();
        }

    } catch (error) {
        // Handle any errors
        const errorDiv = document.getElementById('card-errors');
        errorDiv.textContent = error.message || 'An error occurred. Please try again.';
        
        // Reset the form state
        $('#payment-form').fadeToggle(100);
        $('#loading-overlay').fadeToggle(100);
        card.update({ 'disabled': false});
        $('#submit-button').prop('disabled', false);
    }
});