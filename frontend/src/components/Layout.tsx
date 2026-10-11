import {
  NavLink,
  Outlet,
  useNavigate,
} from "react-router-dom";

import {
  useAuth
} from "../context/AuthContext";


function Layout() {

  const navigate =
    useNavigate();


  const {
    user,
    logout,
  } = useAuth();


  const handleLogout = () => {

    logout();

    navigate(
      "/login",
      {
        replace: true
      }
    );

  };


  return (

    <div className="app-layout">

      {/* =====================================
          SIDEBAR
      ====================================== */}

      <aside className="sidebar">


        {/* LOGO */}

        <div className="sidebar-brand">

          <div className="brand-icon">
            ◉
          </div>


          <div className="brand-text">

            <strong>
              Control Facial
            </strong>

            <span>
              Sistema de Acceso
            </span>

          </div>

        </div>


        {/* ===================================
            NAVEGACION
        ==================================== */}

        <nav className="sidebar-nav">


          {/* DASHBOARD */}

          <NavLink
            to="/"
            end
            className={
              ({ isActive }) =>
                isActive
                  ? "nav-item active"
                  : "nav-item"
            }
          >

            <span className="nav-icon">
              ▦
            </span>

            <span>
              Dashboard
            </span>

          </NavLink>


          {/* =================================
              SOLO ADMIN
          ================================== */}

          {
            user?.rol === "ADMIN"
            && (

              <>

                {/* PERSONAS */}

                <NavLink
                  to="/personas"
                  className={
                    ({ isActive }) =>
                      isActive
                        ? "nav-item active"
                        : "nav-item"
                  }
                >

                  <span className="nav-icon">
                    ♙
                  </span>

                  <span>
                    Personas
                  </span>

                </NavLink>


                {/* VIVIENDAS */}

                <NavLink
                  to="/viviendas"
                  className={
                    ({ isActive }) =>
                      isActive
                        ? "nav-item active"
                        : "nav-item"
                  }
                >

                  <span className="nav-icon">
                    ⌂
                  </span>

                  <span>
                    Viviendas
                  </span>

                </NavLink>


                {/* USUARIOS */}

                <NavLink
                  to="/usuarios"
                  className={
                    ({ isActive }) =>
                      isActive
                        ? "nav-item active"
                        : "nav-item"
                  }
                >

                  <span className="nav-icon">
                    ⚙
                  </span>

                  <span>
                    Usuarios
                  </span>

                </NavLink>

              </>

            )
          }


          {/* =================================
              ADMIN + SEGURIDAD
          ================================== */}

          {/* ACCESOS */}

          <NavLink
            to="/accesos"
            className={
              ({ isActive }) =>
                isActive
                  ? "nav-item active"
                  : "nav-item"
            }
          >

            <span className="nav-icon">
              ⇄
            </span>

            <span>
              Accesos
            </span>

          </NavLink>


          {/* NOTIFICACIONES */}

          <NavLink
            to="/notificaciones"
            className={
              ({ isActive }) =>
                isActive
                  ? "nav-item active"
                  : "nav-item"
            }
          >

            <span className="nav-icon">
              ◇
            </span>

            <span>
              Notificaciones
            </span>

          </NavLink>

        </nav>


        {/* ===================================
            PARTE INFERIOR
        ==================================== */}

        <div className="sidebar-bottom">


          {/* ESTADO */}

          <div className="system-status">

            <span className="status-dot" />

            <span>
              Sistema conectado
            </span>

          </div>


          {/* USUARIO */}

          <div className="sidebar-user">

            <div className="sidebar-user-avatar">

              {
                user
                  ?.usuario
                  .charAt(0)
                  .toUpperCase()
                ?? "U"
              }

            </div>


            <div className="sidebar-user-info">

              <strong>
                {user?.usuario}
              </strong>

              <span>
                {user?.rol}
              </span>

            </div>

          </div>


          {/* CERRAR SESION */}

          <button
            type="button"
            className="logout-button"
            onClick={
              handleLogout
            }
          >
            Cerrar sesión
          </button>

        </div>

      </aside>


      {/* =====================================
          CONTENIDO
      ====================================== */}

      <main className="main-content">

        <Outlet />

      </main>

    </div>

  );

}


export default Layout;