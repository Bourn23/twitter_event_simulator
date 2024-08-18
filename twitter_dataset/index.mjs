import axios from 'axios';
import fs from 'fs';
import fsPromises from 'fs/promises';
import pLimit from 'p-limit';
import readline from 'readline';

// Function to calculate the token
function getToken(id) {
  return ((Number(id) / 1e15) * Math.PI)
    .toString(6 ** 2)
    .replace(/(0+|\.)/g, '');
}

// Function to add a delay
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Function to generate a random wait time between min and max milliseconds
function randomWaitTime(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

// Function to fetch tweet data with exponential backoff and random jitter
async function fetchTweetDataWithRetry(tweetId, retries = 3, backoffFactor = 300, jitterMin = 100, jitterMax = 500) {
  const token = getToken(tweetId);
  const url = `https://cdn.syndication.twimg.com/tweet-result?id=${tweetId}&token=${token}`;

  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      const response = await axios.get(url);
      return response.data;
    } catch (error) {
      console.error(`Error fetching data for tweet ID ${tweetId} (Attempt ${attempt}/${retries}):`, error);
      if (attempt < retries) {
        const delayTime = backoffFactor * 2 ** (attempt - 1); // Exponential backoff
        const jitter = randomWaitTime(jitterMin, jitterMax); // Random jitter
        console.log(`Retrying in ${delayTime + jitter}ms...`);
        await delay(delayTime + jitter);
      } else {
        console.error(`Failed after ${retries} attempts. Giving up on tweet ID ${tweetId}.`);
        return null;
      }
    }
  }
}

// Function to save results to a JSON file
async function saveResultsToFile(results, index) {
  const fileName = `tweets_chunk_${index}.json`;
  await fsPromises.writeFile(fileName, JSON.stringify(results, null, 2));
  console.log(`Saved ${results.length} tweets to ${fileName}`);
}

// Function to process a batch of tweet IDs with limited concurrency
async function processBatch(tweetIds, concurrencyLimit, failureCounter) {
  const limit = pLimit(concurrencyLimit);
  const fetchPromises = tweetIds.map(tweetId =>
    limit(() => fetchTweetDataWithRetry(tweetId))
  );

  const results = await Promise.all(fetchPromises);

  // Update the failure counter based on failed requests
  const successfulResults = results.filter(data => data !== null);
  failureCounter.count += results.length - successfulResults.length;

  return successfulResults;
}

// Main function to process all tweets with save functionality and failure limit
async function processAllTweets(tweetIds, batchSize, concurrencyLimit) {
  let allResults = [];
  let totalFetched = 0;
  let chunkIndex = 1;
  let failureCounter = { count: 0 };

  for (let i = 0; i < tweetIds.length; i += batchSize) {
    if (failureCounter.count >= 10) {
      console.error('Stopping the process after 10 consecutive failures.');
      break;
    }

    const batch = tweetIds.slice(i, i + batchSize);
    console.log(`Processing batch ${i / batchSize + 1} of ${Math.ceil(tweetIds.length / batchSize)}`);
    
    const batchStartTime = performance.now();
    const batchResults = await processBatch(batch, concurrencyLimit, failureCounter);
    const batchEndTime = performance.now();
    const batchDuration = (batchEndTime - batchStartTime) / 1000; // Convert to seconds

    console.log(`Batch processed in ${batchDuration.toFixed(2)} seconds`);

    allResults = allResults.concat(batchResults);
    totalFetched += batchResults.length;

    // Save to file every 1000 fetches
    if (totalFetched >= 1000) {
      await saveResultsToFile(allResults, chunkIndex);
      chunkIndex++;
      allResults = []; // Reset the results array after saving
      totalFetched = 0; // Reset the fetch counter
    }
  }

  // Save any remaining results
  if (allResults.length > 0) {
    await saveResultsToFile(allResults, chunkIndex);
  }
}

// Function to load tweet IDs from a text file
async function loadTweetIdsFromFile(filePath) {
  const fileStream = fs.createReadStream(filePath);
  const rl = readline.createInterface({
    input: fileStream,
    crlfDelay: Infinity
  });

  const tweetIds = [];
  for await (const line of rl) {
    const tweetId = line.trim();
    if (!isNaN(tweetId) && tweetId !== 'id') { // Skip the header or invalid lines
      tweetIds.push(tweetId);
    }
  }

  return tweetIds;
}

// Example usage
const filePath = 'first_1000_tweets.txt'; // Replace with the path to your tweet ID file
const batchSize = 100; // Number of requests to handle per batch
const concurrencyLimit = 10; // Number of concurrent requests

(async () => {
  const startTime = performance.now();

  try {
    console.log('Starting Twitter scraper...');
    
    const loadStartTime = performance.now();
    const tweetIds = await loadTweetIdsFromFile(filePath);
    const loadEndTime = performance.now();
    const loadDuration = (loadEndTime - loadStartTime) / 1000; // Convert to seconds

    console.log(`Loaded ${tweetIds.length} tweet IDs from file in ${loadDuration.toFixed(2)} seconds.`);

    const processStartTime = performance.now();
    await processAllTweets(tweetIds, batchSize, concurrencyLimit);
    const processEndTime = performance.now();
    const processDuration = (processEndTime - processStartTime) / 1000; // Convert to seconds

    console.log(`All tweet data fetched and saved in ${processDuration.toFixed(2)} seconds.`);

    const endTime = performance.now();
    const totalDuration = (endTime - startTime) / 1000; // Convert to seconds

    console.log(`Total execution time: ${totalDuration.toFixed(2)} seconds.`);
  } catch (error) {
    console.error('Error processing tweets:', error);
  }
})();