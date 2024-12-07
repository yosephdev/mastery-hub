/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment
*/
console.log('Stripe Elements JS Loaded');
// Get Stripe public key
const stripePublicKey = document.getElementById('id_stripe_public_key').value;
// Get client secret directly from the input field
const clientSecret = document.getElementById('id_client_secret').value;

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

// Create card elements
const elements = stripe.elements();
const card = elements.create('card', {
    style: {
        base: {
            color: '#000',
            fontFamily: '"Inter", sans-serif',
            fontSize: '16px',
            '::placeholder': {
                color: '#aab7c4'
            }
        },
        invalid: {
            color: '#dc3545',
            iconColor: '#dc3545'
        }
    }
});

card.mount('#card-element');

// Handle realtime validation errors
card.addEventListener('change', function(event) {
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
    
    // Disable form and show loading
    card.update({ 'disabled': true });
    document.getElementById('submit-button').disabled = true;
    document.getElementById('payment-form').style.opacity = '0.5';
    
    // Show loading spinner
    document.getElementById('loading-overlay').style.display = 'block';

    try {
        const result = await stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
                billing_details: {
                    name: form.full_name.value,
                    email: form.email.value,
                    phone: form.phone_number.value,
                    address: {
                        line1: form.street_address1.value,
                        line2: form.street_address2.value,
                        city: form.town_or_city.value,
                        country: form.country.value,
                        postal_code: form.postcode.value,
                        state: form.county.value,
                    }
                }
            }
        });

        if (result.error) {
            // Handle payment error
            const errorDiv = document.getElementById('card-errors');
            errorDiv.textContent = result.error.message;
            
            // Re-enable form
            card.update({ 'disabled': false });
            document.getElementById('submit-button').disabled = false;
            document.getElementById('payment-form').style.opacity = '1';
            document.getElementById('loading-overlay').style.display = 'none';
        } else {
            if (result.paymentIntent.status === 'succeeded') {
                form.submit();
            }
        }
    } catch (error) {
        console.error('Payment error:', error);
        // Handle any other errors
        const errorDiv = document.getElementById('card-errors');
        errorDiv.textContent = 'An error occurred processing your payment. Please try again.';
        
        // Re-enable form
        card.update({ 'disabled': false });
        document.getElementById('submit-button').disabled = false;
        document.getElementById('payment-form').style.opacity = '1';
        document.getElementById('loading-overlay').style.display = 'none';
    }
});