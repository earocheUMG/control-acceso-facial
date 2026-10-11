import {
  useEffect,
  useState,
} from "react";

import {
  apiFetch
} from "../services/api";


interface DashboardSummary {
  personas_activas: number;
  viviendas_activas: number;
  accesos_hoy: number;
  autorizados_hoy: number;
  rechazados_hoy: number;
  notificaciones_error: number;
}


interface RecentAccess {
  id: number;
  fecha_hora: string;
  resultado: string;
  similitud: number | null;
  nombre_completo: string | null;
  tipo: string | null;
  punto_acceso: string;
}


interface DashboardResponse {
  resumen: DashboardSummary;
  ultimos_accesos: RecentAccess[];
}


async function fetchDashboard():
Promise<DashboardResponse> {

  const response =
    await apiFetch(
      "http://127.0.0.1:8000/api/dashboard/resumen"
    );


  const result =
    await response.json();


  if (!response.ok) {

    throw new Error(
      typeof result.detail === "string"
        ? result.detail
        : "No fue posible consultar el dashboard."
    );

  }


  return result;
}


function formatDate(
  value: string
) {

  return new Intl.DateTimeFormat(
    "es-GT",
    {
      dateStyle: "short",
      timeStyle: "medium",
    }
  ).format(
    new Date(value)
  );

}


function DashboardPage() {

  const [
    data,
    setData
  ] = useState<DashboardResponse | null>(
    null
  );


  const [
    loading,
    setLoading
  ] = useState(true);


  const [
    error,
    setError
  ] = useState<string | null>(
    null
  );


  // ==========================================
  // CARGA + REFRESCO AUTOMATICO
  // ==========================================

  useEffect(() => {

    let active = true;


    const requestDashboard =
      async () => {

        try {

          const result =
            await fetchDashboard();


          if (!active) {
            return;
          }


          setData(
            result
          );


          setError(
            null
          );


        } catch (err) {

          if (!active) {
            return;
          }


          if (
            err instanceof Error
          ) {

            setError(
              err.message
            );

          }


        } finally {

          if (active) {

            setLoading(
              false
            );

          }

        }

      };


    void requestDashboard();


    const interval =
      window.setInterval(
        () => {

          void requestDashboard();

        },
        10000
      );


    return () => {

      active = false;

      window.clearInterval(
        interval
      );

    };

  }, []);


  // ==========================================
  // ACTUALIZACION MANUAL
  // ==========================================

  const refreshDashboard =
    async () => {

      try {

        setError(
          null
        );


        const result =
          await fetchDashboard();


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

        }

      }

    };


  return (
    <>

      <header className="topbar">

        <div>

          <h2>
            Dashboard
          </h2>

          <p>
            Resumen del sistema
            de control de acceso
          </p>

        </div>


        <button
          type="button"
          className="refresh-button"
          onClick={
            refreshDashboard
          }
        >
          Actualizar
        </button>

      </header>


      {error && (

        <div className="error-message">
          {error}
        </div>

      )}


      {loading && (

        <div className="message">
          Cargando dashboard...
        </div>

      )}


      {!loading && data && (

        <>

          <section className="access-summary">

            <article className="access-summary-card">

              <span>
                Personas activas
              </span>

              <strong>
                {
                  data.resumen
                    .personas_activas
                }
              </strong>

            </article>


            <article className="access-summary-card">

              <span>
                Viviendas
              </span>

              <strong>
                {
                  data.resumen
                    .viviendas_activas
                }
              </strong>

            </article>


            <article className="access-summary-card">

              <span>
                Accesos hoy
              </span>

              <strong>
                {
                  data.resumen
                    .accesos_hoy
                }
              </strong>

            </article>


            <article
              className="
                access-summary-card
                access-summary-success
              "
            >

              <span>
                Autorizados
              </span>

              <strong>
                {
                  data.resumen
                    .autorizados_hoy
                }
              </strong>

            </article>


            <article
              className="
                access-summary-card
                access-summary-danger
              "
            >

              <span>
                Rechazados
              </span>

              <strong>
                {
                  data.resumen
                    .rechazados_hoy
                }
              </strong>

            </article>


            <article className="access-summary-card">

              <span>
                Errores de notificación
              </span>

              <strong>
                {
                  data.resumen
                    .notificaciones_error
                }
              </strong>

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
                  del sistema
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

                            {
                              access
                                .nombre_completo
                              ??
                              "Desconocido"
                            }

                          </td>


                          <td>

                            {
                              access.tipo
                              ??
                              "-"
                            }

                          </td>


                          <td>

                            <span
                              className={
                                access.resultado
                                === "AUTORIZADO"
                                  ? "badge badge-success"
                                  : "badge badge-danger"
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
                                ? Number(
                                    access.similitud
                                  ).toFixed(3)
                                : "-"
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
                                access.fecha_hora
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