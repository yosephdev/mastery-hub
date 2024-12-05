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
    
    card.update({ 'disabled': true});
    document.getElementById('submit-button').disabled = true;
    
    // Show loading state
    $('#payment-form').fadeToggle(100);
    $('#loading-overlay').fadeToggle(100);

    console.log('Attempting payment with client secret:', clientSecret);

    try {
        const result = await stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
                billing_details: {
                    name: form.full_name.value.trim(),
                    email: form.email.value.trim(),
                    phone: form.phone_number.value.trim(),
                    address: {
                        line1: form.street_address1.value.trim(),
                        line2: form.street_address2.value.trim(),
                        city: form.town_or_city.value.trim(),
                        state: form.county.value.trim(),
                        country: form.country.value.trim(),
                        postal_code: form.postcode.value.trim(),
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
            errorDiv.innerHTML = html;
            
            $('#payment-form').fadeToggle(100);
            $('#loading-overlay').fadeToggle(100);
            card.update({ 'disabled': false});
            document.getElementById('submit-button').disabled = false;
        } else {
            if (result.paymentIntent.status === 'succeeded') {
                form.submit();
            }
        }
    } catch (error) {
        console.error('Payment confirmation error:', error);
        const errorDiv = document.getElementById('card-errors');
        errorDiv.textContent = 'An error occurred while processing your payment. Please try again.';
        
        $('#payment-form').fadeToggle(100);
        $('#loading-overlay').fadeToggle(100);
        card.update({ 'disabled': false});
        document.getElementById('submit-button').disabled = false;
    }
});