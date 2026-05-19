// Base path for all API requests (proxied by Vite to the backend)
const BASE = '/api';

// Types

// Represents a place (location) stored in the backend
export interface Place {
  id: number;
  name: string;
  description?: string;
  category?: string;
  city?: string;
  latitude: number;
  longitude: number;
  trust_score: number;
  user_id?: number;
}

// Represents a user review for a place
export interface Review {
  id: number;
  rating: number;
  text?: string;
  timestamp: string;
  user_id?: number;
}

// Represents an image attached to a place
export interface PlaceImage {
  id: number;
  image_url: string;
  place_id?: number;
  user_id?: number;
  description?: string | null;
  timestamp?: string;
  trust_score?: number;
}

// Auth helpers

// Retrieves the stored API key from localStorage, or null if not set
export function getStoredKey(): string | null {
  return localStorage.getItem('api_key');
}

// Persists the API key to localStorage so it survives page reloads
export function storeKey(key: string) {
  localStorage.setItem('api_key', key);
}

// Retrieves the stored user ID from localStorage, parsed as a number
export function getStoredUserId(): number | null {
  const v = localStorage.getItem('user_id');
  return v !== null ? Number(v) : null;
}

// Persists the user ID to localStorage
export function storeUserId(id: number) {
  localStorage.setItem('user_id', String(id));
}

// Builds the Authorization + Content-Type headers required for authenticated requests
function authHeaders(key: string): HeadersInit {
  return { 'Content-Type': 'application/json', Authorization: `Bearer ${key}` };
}

// Headers for unauthenticated requests that send a JSON body
const jsonHeaders: HeadersInit = { 'Content-Type': 'application/json' };

// Throws an error with the response body text if the HTTP status is not 2xx
async function checkOk(res: Response): Promise<void> {
  if (!res.ok) {
    const body = await res.text().catch(() => '');
    throw new Error(body || res.statusText);
  }
}

// Users

// Registers a new anonymous user and returns their generated id and API key
export async function register(): Promise<{ id: number; api_key: string }> {
  const res = await fetch(`${BASE}/users/`, { method: 'POST', headers: jsonHeaders });
  await checkOk(res);
  return res.json();
}

// Places

// Fetches all places belonging to the "coolrocks" application
export async function fetchPlaces(): Promise<Place[]> {
  const res = await fetch(`${BASE}/places/?application=coolrocks`);
  await checkOk(res);
  return res.json();
}

// Fetches a single place by its ID
export async function fetchPlace(placeId: number): Promise<Place> {
  const res = await fetch(`${BASE}/places/${placeId}/`);
  await checkOk(res);
  return res.json();
}

// Creates a new place. Requires authentication via API key
export async function createPlace(
  data: { name: string; description?: string; latitude: number; longitude: number; category?: string },
  key: string
): Promise<Place> {
  const res = await fetch(`${BASE}/places/`, {
    method: 'POST',
    headers: authHeaders(key),
    body: JSON.stringify({ ...data, application: 'coolrocks' }),
  });
  await checkOk(res);
  return res.json();
}

// Updates an existing places metadata. Requires the user to own the place
export async function updatePlace(
  placeId: number,
  data: Partial<{ name: string; description: string; category: string }>,
  key: string
): Promise<Place> {
  const res = await fetch(`${BASE}/places/${placeId}/`, {
    method: 'PUT',
    headers: authHeaders(key),
    body: JSON.stringify(data),
  });
  await checkOk(res);
  return res.json();
}

// Deletes a place by ID. Requires the user to own the place
export async function deletePlace(placeId: number, key: string): Promise<void> {
  const res = await fetch(`${BASE}/places/${placeId}/`, { method: 'DELETE', headers: authHeaders(key) });
  await checkOk(res);
}

// Reviews

// Fetches all reviews for a given place
export async function fetchReviews(placeId: number): Promise<Review[]> {
  const res = await fetch(`${BASE}/places/${placeId}/reviews/`);
  await checkOk(res);
  return res.json();
}

// Posts a new review for a place. Requires authentication
export async function createReview(
  placeId: number,
  data: { rating: number; text: string },
  key: string
): Promise<Review> {
  const res = await fetch(`${BASE}/places/${placeId}/reviews/`, {
    method: 'POST',
    headers: authHeaders(key),
    body: JSON.stringify(data),
  });
  await checkOk(res);
  return res.json();
}

// Images

// Fetches all images associated with a given place
export async function fetchImages(placeId: number): Promise<PlaceImage[]> {
  const res = await fetch(`${BASE}/places/${placeId}/images/`);
  await checkOk(res);
  return res.json();
}

// Uploads an image file for a place using multipart/form-data. Requires authentication
export async function uploadImage(placeId: number, file: File, key: string): Promise<void> {
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(`${BASE}/places/${placeId}/images/`, {
    method: 'POST',
    // Omit Content-Type so the browser sets the correct multipart boundary automatically
    headers: { Authorization: `Bearer ${key}` },
    body: form,
  });
  await checkOk(res);
}
