const dotenv = require('dotenv');
dotenv.config();

exports.handler = async (event, context) => {
  try {
    const HAL9_API_KEY = process.env.HAL9_API_KEY;
    if (!HAL9_API_KEY) {
      throw new Error('HAL9_API_KEY is not set');
    }
    const hal9Url = `https://hal9.com/books/bookgeneratorv1?embed&guest&apikey=${HAL9_API_KEY}`;
    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': 'https://proofbound.com',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Cache-Control': 'public, max-age=3600',
      },
      body: JSON.stringify({ url: hal9Url }),
    };
  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        'Access-Control-Allow-Origin': 'https://proofbound.com',
      },
      body: JSON.stringify({ error: error.message }),
    };
  }
};