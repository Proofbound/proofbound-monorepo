require('dotenv').config();
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

exports.handler = async (event, context) => {
  try {
    const sessionId = event.queryStringParameters.session_id;
    const isDevelopment = process.env.NETLIFY_DEV === 'true' || !process.env.STRIPE_SECRET_KEY;
    
    // In development mode, skip Stripe verification
    if (isDevelopment) {
      // Return the success page content directly
      const fs = require('fs');
      const path = require('path');
      const successPath = path.join(__dirname, '../../docs/success.html');
      
      try {
        const successContent = fs.readFileSync(successPath, 'utf8');
        return {
          statusCode: 200,
          headers: {
            'Content-Type': 'text/html',
          },
          body: successContent,
        };
      } catch (fsError) {
        // If we can't read the file, just redirect
        return {
          statusCode: 302,
          headers: {
            Location: '/success.html?dev=true',
          },
          body: '',
        };
      }
    }
    
    if (!sessionId) {
      return {
        statusCode: 403,
        body: JSON.stringify({ error: 'Missing session_id' }),
      };
    }

    const session = await stripe.checkout.sessions.retrieve(sessionId);
    if (session.payment_status !== 'paid') {
      return {
        statusCode: 403,
        body: JSON.stringify({ error: 'Payment not completed' }),
      };
    }

    // Payment verified, redirect to success.html
    return {
      statusCode: 302,
      headers: {
        Location: '/success.html',
      },
      body: '',
    };
  } catch (error) {
    console.error('Error verifying session:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Failed to verify payment' }),
    };
  }
};