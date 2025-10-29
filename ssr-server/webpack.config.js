const path = require('path');
const webpack = require('webpack');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const nodeExternals = require('webpack-node-externals');

const isProduction = process.env.NODE_ENV === 'production';

module.exports = [
  // Server bundle
  {
    name: 'server',
    target: 'node',
    mode: isProduction ? 'production' : 'development',
    entry: './src/server.js',
    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: 'server.js',
      libraryTarget: 'commonjs2'
    },
    externals: [nodeExternals()],
    module: {
      rules: [
        {
          test: /\.(js|jsx)$/,
          exclude: /node_modules/,
          use: {
            loader: 'babel-loader'
          }
        },
        {
          test: /\.css$/,
          use: [
            'style-loader',
            'css-loader'
          ]
        }
      ]
    },
    plugins: [
      new webpack.DefinePlugin({
        'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'development')
      })
    ]
  },
  // Client bundle
  {
    name: 'client',
    target: 'web',
    mode: isProduction ? 'production' : 'development',
    entry: './src/client.jsx',
    output: {
      path: path.resolve(__dirname, 'dist/public'),
      filename: 'client.js',
      publicPath: '/static/'
    },
    module: {
      rules: [
        {
          test: /\.(js|jsx)$/,
          exclude: /node_modules/,
          use: {
            loader: 'babel-loader'
          }
        },
        {
          test: /\.css$/,
          use: [
            MiniCssExtractPlugin.loader,
            'css-loader'
          ]
        }
      ]
    },
    plugins: [
      new MiniCssExtractPlugin({
        filename: 'styles.css'
      }),
      new HtmlWebpackPlugin({
        template: './public/index.html',
        filename: 'index.html',
        inject: false
      }),
      new webpack.DefinePlugin({
        'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'development')
      })
    ],
    optimization: {
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all'
          }
        }
      }
    }
  }
];



