import {
  useEffect,
  useState
} from "react";


interface DashboardSummary {
  personas_activas: number;
  viviendas_activas: number;
  accesos_hoy: number;
  autorizados_hoy: number;
  rechazados_hoy: number;
  notificaciones_error: number;
}


interface Access {
  id: number;
  fecha_hora: string;
  resultado: string;
  similitud: number | null;
  nombre_completo: string | null;
  tipo_persona: string | null;
  punto_acceso: string;
}


interface DashboardResponse {
  resumen: DashboardSummary;
  ultimos_accesos: Access[];
}


const API_URL =
  "http://127.0.0.1:8000/api/dashboard/resumen";


function formatDate(
  date: string
) {
  return new Intl.DateTimeFormat(
    "es-GT",
    {
      dateStyle: "short",
      timeStyle: "medium",
    }
  ).format(
    new Date(date)
  );
}


function DashboardPage() {

  const [data, setData] =
    useState<DashboardResponse | null>(
      null
    );

  const [error, setError] =
    useState<string | null>(
      null
    );

  const [loading, setLoading] =
    useState(true);


  const loadDashboard =
    async () => {

      try {

        setError(null);

        const response =
          await fetch(
            API_URL
          );

        if (!response.ok) {

          throw new Error(
            "No fue posible consultar la API."
          );

        }

        const result:
          DashboardResponse =
            await response.json();

        setData(
          result
        );

      } catch (err) {

        if (
          err instanceof Error
        ) {

          setError(
            err.message
          );

        } else {

          setError(
            "Ocurrió un error inesperado."
          );

        }

      } finally {

        setLoading(
          false
        );

      }

    };


  useEffect(() => {

    loadDashboard();

    const interval =
      window.setInterval(
        loadDashboard,
        10000
      );

    return () => {

      window.clearInterval(
        interval
      );

    };

  }, []);


  return (
    <>

      <header className="topbar">

        <div>

          <h2>
            Dashboard
          </h2>

          <p>
            Sistema de Control de
            Acceso Facial
          </p>

        </div>


        <button
          className="refresh-button"
          onClick={
            loadDashboard
          }
        >
          Actualizar
        </button>

      </header>


      {loading && (
        <div className="message">
          Cargando información...
        </div>
      )}


      {error && (
        <div className="error-message">
          {error}
        </div>
      )}


      {data && (
        <>

          <section className="stats-grid">

            <article className="stat-card">

              <div className="stat-icon">
                👤
              </div>

              <div>

                <span className="stat-label">
                  Personas activas
                </span>

                <strong>
                  {
                    data.resumen
                      .personas_activas
                  }
                </strong>

              </div>

            </article>


            <article className="stat-card">

              <div className="stat-icon">
                🏠
              </div>

              <div>

                <span className="stat-label">
                  Viviendas
                </span>

                <strong>
                  {
                    data.resumen
                      .viviendas_activas
                  }
                </strong>

              </div>

            </article>


            <article className="stat-card">

              <div className="stat-icon">
                ↔
              </div>

              <div>

                <span className="stat-label">
                  Accesos hoy
                </span>

                <strong>
                  {
                    data.resumen
                      .accesos_hoy
                  }
                </strong>

              </div>

            </article>


            <article
              className="
                stat-card
                authorized
              "
            >

              <div className="stat-icon">
                ✓
              </div>

              <div>

                <span className="stat-label">
                  Autorizados
                </span>

                <strong>
                  {
                    data.resumen
                      .autorizados_hoy
                  }
                </strong>

              </div>

            </article>


            <article
              className="
                stat-card
                rejected
              "
            >

              <div className="stat-icon">
                !
              </div>

              <div>

                <span className="stat-label">
                  Rechazados
                </span>

                <strong>
                  {
                    data.resumen
                      .rechazados_hoy
                  }
                </strong>

              </div>

            </article>


            <article
              className="
                stat-card
                notification
              "
            >

              <div className="stat-icon">
                ✉
              </div>

              <div>

                <span className="stat-label">
                  Errores de notificación
                </span>

                <strong>
                  {
                    data.resumen
                      .notificaciones_error
                  }
                </strong>

              </div>

            </article>

          </section>


          <section className="panel">

            <div className="panel-header">

              <div>

                <h3>
                  Últimos accesos
                </h3>

                <p>
                  Actividad reciente
                  registrada por el sistema
                </p>

              </div>


              <span className="live-indicator">

                <span />

                En línea

              </span>

            </div>


            <div className="table-container">

              <table>

                <thead>

                  <tr>

                    <th>
                      Persona
                    </th>

                    <th>
                      Tipo
                    </th>

                    <th>
                      Resultado
                    </th>

                    <th>
                      Similitud
                    </th>

                    <th>
                      Punto de acceso
                    </th>

                    <th>
                      Fecha
                    </th>

                  </tr>

                </thead>


                <tbody>

                  {
                    data.ultimos_accesos.map(
                      (access) => (

                        <tr
                          key={
                            access.id
                          }
                        >

                          <td>

                            <div className="person-cell">

                              <div className="person-avatar">

                                {
                                  access
                                    .nombre_completo
                                    ?.charAt(0)
                                    .toUpperCase()
                                  ?? "?"
                                }

                              </div>


                              <strong>

                                {
                                  access
                                    .nombre_completo
                                  ??
                                  "Persona desconocida"
                                }

                              </strong>

                            </div>

                          </td>


                          <td>

                            {
                              access
                                .tipo_persona
                              ?? "N/A"
                            }

                          </td>


                          <td>

                            <span
                              className={
                                access.resultado
                                === "AUTORIZADO"
                                  ?
                                    "badge badge-success"
                                  :
                                    "badge badge-danger"
                              }
                            >

                              {
                                access.resultado
                              }

                            </span>

                          </td>


                          <td>

                            {
                              access.similitud
                              !== null
                                ?
                                  Number(
                                    access.similitud
                                  ).toFixed(3)
                                :
                                  "N/A"
                            }

                          </td>


                          <td>

                            {
                              access
                                .punto_acceso
                            }

                          </td>


                          <td>

                            {
                              formatDate(
                                access
                                  .fecha_hora
                              )
                            }

                          </td>

                        </tr>

                      )
                    )
                  }

                </tbody>

              </table>

            </div>

          </section>

        </>
      )}

    </>
  );
}


export default DashboardPage;