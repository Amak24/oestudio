
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import LoginForm from "./components/LoginForm";
import RegisterForm from "./components/RegisterForm";
import ConcertForm from "./components/ConcertForm";

function Home() {
  return (
    <div style={{ padding: '20px' }}>
      <h1>O Estúdio - Live Concert Streaming</h1>
      <p>Welcome to O Estúdio, your platform for live music streaming!</p>
      <nav style={{ margin: '20px 0' }}>
        <Link to="/login" style={{ margin: '0 10px' }}>Login</Link>
        <Link to="/register" style={{ margin: '0 10px' }}>Register</Link>
        <Link to="/concerts/create" style={{ margin: '0 10px' }}>Create Concert</Link>
      </nav>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<LoginForm />} />
        <Route path="/register" element={<RegisterForm />} />
        <Route path="/concerts/create" element={<ConcertForm />} />
      </Routes>
    </BrowserRouter>
  );
}
