import {
  Route,
  Routes
} from "react-router-dom";

import Layout from "./components/Layout";

import DashboardPage from "./pages/DashboardPage";
import PersonasPage from "./pages/PersonasPage";
import ViviendasPage from "./pages/ViviendasPage";
import AccesosPage from "./pages/AccesosPage";
import NotificacionesPage from "./pages/NotificacionesPage";

import "./App.css";


function App() {
  return (
    <Routes>

      <Route
        element={
          <Layout />
        }
      >

        <Route
          path="/"
          element={
            <DashboardPage />
          }
        />

        <Route
          path="/personas"
          element={
            <PersonasPage />
          }
        />

        <Route
          path="/viviendas"
          element={
            <ViviendasPage />
          }
        />

        <Route
          path="/accesos"
          element={
            <AccesosPage />
          }
        />

        <Route
          path="/notificaciones"
          element={
            <NotificacionesPage />
          }
        />

      </Route>

    </Routes>
  );
}


export default App;