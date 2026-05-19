import { useState, useEffect, Component, ReactNode } from 'react';
import PlaceMap from './components/PlaceMap';
import Sidebar from './components/Sidebar';
import { fetchPlaces, getStoredKey, storeKey, getStoredUserId, storeUserId, register, Place } from './api';

// Catches unhandled render errors in the component tree and shows a fallback UI
class ErrorBoundary extends Component<{ children: ReactNode }, { error: Error | null }> {
  state = { error: null };

  // Captures the thrown error and stores it so render() can display the fallback
  static getDerivedStateFromError(error: Error) { return { error }; }

  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: 32, fontFamily: 'monospace' }}>
          <h2 style={{ color: '#e94560' }}>Something went wrong</h2>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: 13, color: '#555' }}>
            {(this.state.error as Error).message}
          </pre>
          {/* Reset error state so the user can try again without a full page reload */}
          <button onClick={() => this.setState({ error: null })} style={{ marginTop: 12, padding: '8px 16px', cursor: 'pointer' }}>
            Try again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

// Root application component
export default function App() {
  // Auth state: API key and user ID are loaded from localStorage on first render
  const [apiKey, setApiKey] = useState<string | null>(getStoredKey());
  const [userId, setUserId] = useState<number | null>(getStoredUserId());

  // Places list shown on the map
  const [places, setPlaces] = useState<Place[]>([]);

  // The place the user has clicked on in the map
  const [selectedPlace, setSelectedPlace] = useState<Place | null>(null);

  // When true, the map enters pin dropping mode and the cursor changes to a crosshair
  const [addingMode, setAddingMode] = useState(false);

  // Coordinates chosen by clicking the map. Drives the AddPlaceForm in the sidebar
  const [pendingCoords, setPendingCoords] = useState<[number, number] | null>(null);

  const [error, setError] = useState<string | null>(null);

  // Fetch all places from the API when the app first mounts
  useEffect(() => {
    fetchPlaces()
      .then(setPlaces)
      .catch(() => setError('Could not load rocks from API.'));
  }, []);

  // Registers a new anonymous user, stores their credentials, and shows the API key once
  async function handleRegister() {
    try {
      const { id, api_key } = await register();
      storeKey(api_key);
      storeUserId(id);
      setApiKey(api_key);
      setUserId(id);
      setError(null);
      alert(`Your API key:\n\n${api_key}\n\nSave this somewhere. It won't be shown again.`);
    } catch {
      setError('Registration failed');
    }
  }

  // Captures the clicked map coordinates when the user is in adding mode
  function handleMapClick(coords: [number, number]) {
    if (!addingMode) return;
    setPendingCoords(coords);
    setSelectedPlace(null);
  }

  // Appends a newly created place to the list and selects it in the sidebar
  function handlePlaceAdded(place: Place) {
    setPlaces(prev => [...prev, place]);
    setSelectedPlace(place);
    setPendingCoords(null);
    setAddingMode(false);
  }

  // Replaces the stale place entry with the freshly updated one
  function handlePlaceUpdated(updated: Place) {
    setPlaces(prev => prev.map(p => p.id === updated.id ? updated : p));
    setSelectedPlace(updated);
  }

  // Removes a deleted place from the list and clears the sidebar selection
  function handlePlaceDeleted(placeId: number) {
    setPlaces(prev => prev.filter(p => p.id !== placeId));
    setSelectedPlace(null);
  }

  // Exits adding mode without creating a place
  function cancelAdding() {
    setAddingMode(false);
    setPendingCoords(null);
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* Top navigation bar with branding, error display, and action buttons */}
      <header style={{
        background: '#1a1a2e', color: 'white',
        padding: '12px 20px', display: 'flex', alignItems: 'center', gap: 12, flexShrink: 0,
      }}>
        <h1 style={{ fontSize: 20, fontWeight: 700, letterSpacing: -0.5 }}>CoolRocks</h1>

        {error && (
          <span style={{ fontSize: 13, color: '#ff6b6b', marginLeft: 8 }}>{error}</span>
        )}

        {/* Right-aligned controls: switches between adding-mode instructions and normal buttons */}
        <div style={{ marginLeft: 'auto', display: 'flex', gap: 10, alignItems: 'center' }}>
          {addingMode ? (
            <>
              <span style={{ fontSize: 13, color: '#e94560' }}>
                Click the map to place a pin...
              </span>
              <button onClick={cancelAdding} style={btnStyle('ghost')}>Cancel</button>
            </>
          ) : (
            <>
              {apiKey && (
                <button onClick={() => setAddingMode(true)} style={btnStyle('primary')}>
                  + Add Rock
                </button>
              )}
              {!apiKey ? (
                <button onClick={handleRegister} style={btnStyle('primary')}>
                  Register (get API key)
                </button>
              ) : (
                <span style={{ fontSize: 13, opacity: 0.5 }}>Logged in</span>
              )}
            </>
          )}
        </div>
      </header>

      {/* Main content area: map fills the remaining space, sidebar is fixed-width */}
      <ErrorBoundary>
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        <PlaceMap
          places={places}
          addingMode={addingMode}
          pendingCoords={pendingCoords}
          onMapClick={handleMapClick}
          onSelectPlace={(p) => { setSelectedPlace(p); setPendingCoords(null); setAddingMode(false); }}
        />
        <Sidebar
          place={selectedPlace}
          pendingCoords={pendingCoords}
          apiKey={apiKey}
          userId={userId}
          noPlaces={places.length === 0}
          onPlaceAdded={handlePlaceAdded}
          onPlaceUpdated={handlePlaceUpdated}
          onPlaceDeleted={handlePlaceDeleted}
          onCancelAdd={cancelAdding}
          onClose={() => setSelectedPlace(null)}
        />
      </div>
      </ErrorBoundary>
    </div>
  );
}

// Returns inline CSS for a header button; 'primary' is filled red, 'ghost' is outlined
function btnStyle(variant: 'primary' | 'ghost'): React.CSSProperties {
  return {
    padding: '7px 14px',
    border: variant === 'ghost' ? '1px solid rgba(255,255,255,0.3)' : 'none',
    background: variant === 'primary' ? '#e94560' : 'transparent',
    color: 'white',
    borderRadius: 6,
    cursor: 'pointer',
    fontSize: 14,
    fontWeight: 500,
  };
}
