/**
 * JS data file
 *
 * @url /test
 *
 * Export data by using the JS file directly.
 */

module.exports = {
  code: function() {
    // simulation error code, 1/10 probability of error code 1.
    return Math.random() < 0.1 ? 1 : 0
  },
  "list|5-10": [{ title: "@title", link: "@url" }]
}
