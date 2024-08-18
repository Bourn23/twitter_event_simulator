const axios = require('axios');

function getToken(id) {
  return ((Number(id) / 1e15) * Math.PI)
    .toString(6 ** 2)
    .replace(/(0+|\.)/g, '');
}

async function fetchTweetData(tweetId) {
  const token = getToken(tweetId);
  const url = `https://cdn.syndication.twimg.com/tweet-result?id=${tweetId}&token=${token}`;

  try {
    const response = await axios.get(url);
    const data = response.data;
    console.log(data);
  } catch (error) {
    console.error('Error fetching tweet data:', error);
  }
}

// Example usage
const tweetId = '1628832338187636740'; // Replace with actual tweet ID
fetchTweetData(tweetId);