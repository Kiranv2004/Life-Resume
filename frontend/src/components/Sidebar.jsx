import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider.jsx";
import { useTheme } from "../hooks/useTheme.jsx";

const NAV_ITEMS = [
  { path: "/dashboard", icon: "📊", label: "Dashboard" },
  { path: "/profile",   icon: "👤", label: "Profile" },
  { path: "/connect",   icon: "🔗", label: "Connect" },
  { path: "/progress",  icon: "⚡", label: "Analysis" },
];

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout } = useAuth();
  const { theme, toggle } = useTheme();

  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="sidebar-brand">
        <h2>🧬 Life Resume</h2>
        <span>Behavioral Intelligence</span>
      </div>

      {/* Nav */}
      <nav className="sidebar-nav">
        {NAV_ITEMS.map(item => (
          <button
            key={item.path}
            className={`sidebar-link ${location.pathname === item.path ? "active" : ""}`}
            onClick={() => navigate(item.path)}
          >
            <span className="icon">{item.icon}</span>
            {item.label}
          </button>
        ))}
      </nav>

      {/* Footer */}
      <div className="sidebar-footer">
        <button className="theme-toggle" onClick={toggle}>
          <span className="toggle-icon">{theme === "dark" ? "🌙" : "☀️"}</span>
          {theme === "dark" ? "Dark Mode" : "Light Mode"}
        </button>
        <button className="sidebar-link" onClick={logout} style={{ color: "var(--red)" }}>
          <span className="icon">🚪</span>
          Logout
        </button>
      </div>
    </aside>
  );
}
