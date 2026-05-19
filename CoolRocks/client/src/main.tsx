import ReactDOM from 'react-dom/client';
import 'leaflet/dist/leaflet.css';
import './index.css';
import App from './App';

// Entry point: mounts the React application into the #root element defined in index.html
ReactDOM.createRoot(document.getElementById('root')!).render(<App />);
