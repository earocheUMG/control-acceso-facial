import { NavLink, Outlet } from "react-router-dom";


function Layout() {
  return (
    <div className="app-layout">

      <aside className="sidebar">

        <div className="brand">
          <div className="brand-icon">
            ◉
          </div>

          <div>
            <h1>
              Control Facial
            </h1>

            <span>
              Sistema de Acceso
            </span>
          </div>
        </div>


        <nav className="navigation">

          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              isActive
                ? "nav-item active"
                : "nav-item"
            }
          >
            <span>▦</span>
            Dashboard
          </NavLink>


          <NavLink
            to="/personas"
            className={({ isActive }) =>
              isActive
                ? "nav-item active"
                : "nav-item"
            }
          >
            <span>●</span>
            Personas
          </NavLink>


          <NavLink
            to="/viviendas"
            className={({ isActive }) =>
              isActive
                ? "nav-item active"
                : "nav-item"
            }
          >
            <span>⌂</span>
            Viviendas
          </NavLink>


          <NavLink
            to="/accesos"
            className={({ isActive }) =>
              isActive
                ? "nav-item active"
                : "nav-item"
            }
          >
            <span>↔</span>
            Accesos
          </NavLink>


          <NavLink
            to="/notificaciones"
            className={({ isActive }) =>
              isActive
                ? "nav-item active"
                : "nav-item"
            }
          >
            <span>✉</span>
            Notificaciones
          </NavLink>

        </nav>


        <div className="sidebar-footer">

          <span className="system-dot" />

          Sistema conectado

        </div>

      </aside>


      <main className="content">

        <Outlet />

      </main>

    </div>
  );
}


export default Layout;