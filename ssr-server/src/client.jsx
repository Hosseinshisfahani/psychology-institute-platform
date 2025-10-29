import React from 'react';
import { hydrateRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import App from './App';

// Get initial data from server
const initialData = window.__INITIAL_DATA__ || {};
const initialState = window.__INITIAL_STATE__ || {};

// Hydrate the app
const container = document.getElementById('root');
if (container) {
  hydrateRoot(
    container,
    <HelmetProvider>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </HelmetProvider>
  );
}

// Clean up global variables
delete window.__INITIAL_DATA__;
delete window.__INITIAL_STATE__;



