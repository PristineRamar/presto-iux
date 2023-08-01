import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import {Auth0Provider} from '@auth0/auth0-react'

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <Auth0Provider
      domain='dev-pitplc8pespwsccm.us.auth0.com'
      clientId='bLAF70xVVe6me7UqUuCmalmP8jCLF5Vn'
      redirecturl={window.location.origin}>
    <App />
    </Auth0Provider>
  </React.StrictMode>
);