// _resources/js.js
async function loadContent() {
  try {
    const response = await fetch('/.netlify/functions');
    if (!response.ok) throw new Error('Failed to fetch Hal9 URL: ' + response.status);
    const data = await response.json();
    document.getElementById('hal9-iframe').src = data.url;
  } catch (error) {
    console.error('Error loading Hal9 iframe:', error);
    document.getElementById('hal9-iframe').src = '';
  }
}
window.addEventListener('load', loadContent);