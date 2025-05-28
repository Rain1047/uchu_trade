import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE || (window.location.hostname === 'localhost' ? 'http://localhost:8000' : '/');

const http = axios.create({
  baseURL: API_BASE,
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json'
  }
});

export default http; 