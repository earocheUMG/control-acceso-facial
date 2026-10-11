import {
  Route,
  Routes
} from "react-router-dom";

import Layout
  from "./components/Layout";

import ProtectedRoute
  from "./components/ProtectedRoute";

import AdminRoute
  from "./components/AdminRoute";

import DashboardPage
  from "./pages/DashboardPage";

import PersonasPage
  from "./pages/PersonasPage";

import ViviendasPage
  from "./pages/ViviendasPage";

import AccesosPage
  from "./pages/AccesosPage";

import NotificacionesPage
  from "./pages/NotificacionesPage";

import UsuariosPage
  from "./pages/UsuariosPage";

import LoginPage
  from "./pages/LoginPage";

import "./App.css";


function App() {

  return (

    <Routes>

      {/* =====================================
          LOGIN
      ====================================== */}

      <Route
        path="/login"
        element={
          <LoginPage />
        }
      />


      {/* =====================================
          SISTEMA AUTENTICADO
      ====================================== */}

      <Route
        element={

          <ProtectedRoute>

            <Layout />

          </ProtectedRoute>

        }
      >


        {/* ===================================
            ADMIN + SEGURIDAD
        ==================================== */}

        <Route
          path="/"
          element={
            <DashboardPage />
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


        {/* ===================================
            SOLO ADMIN
        ==================================== */}

        <Route
          path="/personas"
          element={

            <AdminRoute>

              <PersonasPage />

            </AdminRoute>

          }
        />


        <Route
          path="/viviendas"
          element={

            <AdminRoute>

              <ViviendasPage />

            </AdminRoute>

          }
        />


        <Route
          path="/usuarios"
          element={

            <AdminRoute>

              <UsuariosPage />

            </AdminRoute>

          }
        />


      </Route>


    </Routes>

  );

}


export default App;