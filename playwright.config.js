// playwright.config.js
module.exports = {
  webServer: {
    command: 'playwright install chromium',
    timeout: 120 * 1000,
  },
};
