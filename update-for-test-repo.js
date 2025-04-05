// Simple JavaScript file for test repository
console.log("Hello from PC Builder Guide testing integration!");

// Function to display current date
function getCurrentDate() {
  const now = new Date();
  return now.toISOString();
}

// Log current timestamp
console.log(`File created at: ${getCurrentDate()}`);

// Export function for potential use
module.exports = { getCurrentDate }; 