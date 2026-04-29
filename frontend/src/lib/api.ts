/**
 * Centralized API configuration for GrowwPulse frontend.
 * 
 * Uses NEXT_PUBLIC_API_URL environment variable if set,
 * otherwise falls back to the production Render URL.
 * For local dev, set NEXT_PUBLIC_API_URL=http://localhost:8000 in .env.local
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://growwrivews.onrender.com';

export function getApiUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}

export default API_BASE_URL;
