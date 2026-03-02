import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth/AuthProvider.jsx";
import { ThemeProvider } from "./hooks/useTheme.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Connect from "./pages/Connect.jsx";
import Progress from "./pages/Progress.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Profile from "./pages/Profile.jsx";
import Sidebar from "./components/Sidebar.jsx";

const PrivateRoute = ({ children }) => {
  const { token } = useAuth();
  return token ? children : <Navigate to="/login" />;
};

/* Pages that show the sidebar */
const AUTH_PAGES = ["/login", "/register"];

function AppLayout() {
  const { token } = useAuth();
  const location = useLocation();
  const showSidebar = token && !AUTH_PAGES.includes(location.pathname);

  return (
    <div className={showSidebar ? "app-layout" : ""}>
      {showSidebar && <Sidebar />}
      <div className={showSidebar ? "main-content" : ""}>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/connect" element={<PrivateRoute><Connect /></PrivateRoute>} />
          <Route path="/progress" element={<PrivateRoute><Progress /></PrivateRoute>} />
          <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
          <Route path="/profile" element={<PrivateRoute><Profile /></PrivateRoute>} />
        </Routes>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppLayout />
      </AuthProvider>
    </ThemeProvider>
  );
}
