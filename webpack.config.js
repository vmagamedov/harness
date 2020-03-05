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
        include: [
          __dirname + '/docs',
          __dirname + '/node_modules/clipboard/src'
        ],
        use: {
          loader: "babel-loader"
        }
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      }
    ]
  }
};
