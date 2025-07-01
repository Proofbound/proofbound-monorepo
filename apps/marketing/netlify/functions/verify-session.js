require('dotenv').config();
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);

exports.handler = async (event, context) => {
  try {
    const sessionId = event.queryStringParameters.session_id;
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