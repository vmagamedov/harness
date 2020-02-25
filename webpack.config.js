module.exports = {
  entry: __dirname + '/docs/_static/bootstrap.jsx',
  output: {
    path: __dirname + '/docs/_static',
    filename: 'bootstrap.js'
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader"
        }
      }
    ]
  }
};
