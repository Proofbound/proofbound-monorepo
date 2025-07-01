require('dotenv').config();

// netlify/functions/hal9-direct.js

const allowedOrigins = [
  'https://proofbound.com',
  'http://localhost:8888', // Common netlify dev port
  'http://localhost:4710'  // Quarto preview port from CLAUDE.md
];

exports.handler = async (event, context) => {
  console.log('=== HAL9 Direct Function Called ===');
  console.log('Method:', event.httpMethod);
  console.log('HAL9_API_KEY present:', !!process.env.HAL9_API_KEY);

  const origin = event.headers.origin;
  const corsHeaders = {
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  };

  if (allowedOrigins.includes(origin)) {
    corsHeaders['Access-Control-Allow-Origin'] = origin;
  }

  // Handle preflight OPTIONS request for CORS
  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 204, headers: corsHeaders, body: '' };
  }

  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  try {
    const { title, author, book_idea, sessionId } = JSON.parse(event.body);
    console.log('Parsed data:', { title, author, sessionId });

    if (!sessionId) {
      return {
        statusCode: 403,
        headers: corsHeaders,
        body: JSON.stringify({ error: 'Payment verification failed: No Session ID provided.' }),
      };
    }

    // Call the new verification endpoint.
    // process.env.URL is automatically set by Netlify to the site's primary URL.
    const verificationUrl = `${process.env.URL}/.netlify/functions/verify-checkout-session`;
    const verificationResponse = await fetch(verificationUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sessionId: sessionId }),
    });

    if (!verificationResponse.ok) {
      const errorBody = await verificationResponse.json();
      console.error('Verification request failed:', errorBody.error);
      return {
        statusCode: 403,
        headers: corsHeaders,
        body: JSON.stringify({ error: `Payment verification failed: ${errorBody.error || 'Unknown reason'}` }),
      };
    }

    console.log('Payment verified successfully. Calling HAL9 API.');
    const response = await fetch('https://api.hal9.com/books/bookgeneratorapi/proxy/toc', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.HAL9_API_KEY}`,
      },
      body: JSON.stringify({ title, author, book_idea }),
    });

    if (!response.ok) {
      const errorBody = await response.text();
      throw new Error(`HAL9 API error: ${response.status} - ${errorBody}`);
    }

    const result = await response.json();

    return {
      statusCode: 200,
      headers: {
        ...corsHeaders,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(result),
    };
  } catch (error) {
    console.error('Error:', error.message);
    return {
      statusCode: 500,
      headers: corsHeaders,
      body: JSON.stringify({ error: error.message }),
    };
  }
};