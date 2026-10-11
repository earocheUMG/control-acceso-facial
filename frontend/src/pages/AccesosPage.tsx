import {
  useEffect,
  useState,
} from "react";

import {
  apiFetch
} from "../services/api";


interface Access {
  id: number;
  fecha_hora: string;
  resultado: string;
  similitud: number | null;
  puerta_abierta: boolean;
  metodo: string;
  motivo: string | null;
  captura_path: string | null;

  persona_id: number | null;
  codigo_biometrico: string | null;
  nombre_completo: string | null;
  tipo_persona: string | null;

  punto_acceso_id: number;
  punto_acceso: string;
  ubicacion_punto: string | null;

  viviendas: string;

  total_notificaciones: number;
  notificaciones_enviadas: number;
  notificaciones_error: number;
}


interface AccessResponse {
  total: number;
  filtro_resultado: string | null;
  accesos: Access[];
}


type Filter =
  | "TODOS"
  | "AUTORIZADO"
  | "RECHAZADO";


async function fetchAccesses(
  filter: Filter,
  limit: number
): Promise<AccessResponse> {

  let url =
    `http://127.0.0.1:8000/api/accesos?limit=${limit}`;


  if (
    filter !== "TODOS"
  ) {

    url +=
      `&resultado=${filter}`;

  }


  const response =
    await apiFetch(
      url
    );


  const result =
    await response.json();


  if (!response.ok) {

    throw new Error(
      typeof result.detail === "string"
        ? result.detail
        : "No fue posible consultar los accesos."
    );

  }


  return result;
}


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


function AccesosPage() {

  const [
    accesses,
    setAccesses
  ] = useState<Access[]>([]);


  const [
    filter,
    setFilter
  ] = useState<Filter>(
    "TODOS"
  );


  const [
    limit,
    setLimit
  ] = useState(50);


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


    const request =
      async () => {

        try {

          const data =
            await fetchAccesses(
              filter,
              limit
            );


          if (!active) {
            return;
          }


          setAccesses(
            data.accesos
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


    void request();


    const interval =
      window.setInterval(
        () => {

          void request();

        },
        10000
      );


    return () => {

      active = false;

      window.clearInterval(
        interval
      );

    };

  }, [
    filter,
    limit
  ]);


  const refreshAccesses =
    async () => {

      try {

        const data =
          await fetchAccesses(
            filter,
            limit
          );


        setAccesses(
          data.accesos
        );


        setError(
          null
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


  const authorizedCount =
    accesses.filter(
      (access) =>
        access.resultado
        === "AUTORIZADO"
    ).length;


  const rejectedCount =
    accesses.filter(
      (access) =>
        access.resultado
        === "RECHAZADO"
    ).length;


  return (
    <>

      <header className="topbar">

        <div>

          <h2>
            Accesos
          </h2>

          <p>
            Bitácora de ingresos
            e intentos de acceso
          </p>

        </div>


        <button
          type="button"
          className="refresh-button"
          onClick={
            refreshAccesses
          }
        >
          Actualizar
        </button>

      </header>


      <section className="access-summary">

        <article className="access-summary-card">

          <span>
            Registros mostrados
          </span>

          <strong>
            {accesses.length}
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
            {authorizedCount}
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
            {rejectedCount}
          </strong>

        </article>

      </section>


      <section className="access-toolbar">

        <div className="access-filters">

          <button
            type="button"
            className={
              filter === "TODOS"
                ? "filter-button active"
                : "filter-button"
            }
            onClick={
              () =>
                setFilter(
                  "TODOS"
                )
            }
          >
            Todos
          </button>


          <button
            type="button"
            className={
              filter === "AUTORIZADO"
                ? "filter-button active success"
                : "filter-button"
            }
            onClick={
              () =>
                setFilter(
                  "AUTORIZADO"
                )
            }
          >
            Autorizados
          </button>


          <button
            type="button"
            className={
              filter === "RECHAZADO"
                ? "filter-button active danger"
                : "filter-button"
            }
            onClick={
              () =>
                setFilter(
                  "RECHAZADO"
                )
            }
          >
            Rechazados
          </button>

        </div>


        <div className="access-limit">

          <label>
            Mostrar:
          </label>

          <select
            value={
              limit
            }
            onChange={
              (event) =>
                setLimit(
                  Number(
                    event.target.value
                  )
                )
            }
          >

            <option value={10}>
              10
            </option>

            <option value={25}>
              25
            </option>

            <option value={50}>
              50
            </option>

            <option value={100}>
              100
            </option>

          </select>

        </div>

      </section>


      {error && (

        <div className="error-message">
          {error}
        </div>

      )}


      {loading && (

        <div className="message">
          Cargando accesos...
        </div>

      )}


      {!loading && !error && (

        <section className="panel">

          <div className="panel-header">

            <div>

              <h3>
                Bitácora de accesos
              </h3>

              <p>
                Actualización automática
                cada 10 segundos
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

                  <th>ID</th>
                  <th>Persona</th>
                  <th>Vivienda</th>
                  <th>Resultado</th>
                  <th>Similitud</th>
                  <th>Puerta</th>
                  <th>Notificación</th>
                  <th>Punto</th>
                  <th>Fecha</th>

                </tr>

              </thead>


              <tbody>

                {
                  accesses.map(
                    (access) => (

                      <tr
                        key={
                          access.id
                        }
                      >

                        <td>

                          <span className="access-id">
                            #{access.id}
                          </span>

                        </td>


                        <td>

                          <div className="person-cell">

                            <div
                              className={
                                access.nombre_completo
                                  ? "person-avatar"
                                  : "person-avatar unknown"
                              }
                            >

                              {
                                access
                                  .nombre_completo
                                  ?.charAt(0)
                                  .toUpperCase()
                                ?? "?"
                              }

                            </div>


                            <div>

                              <strong>

                                {
                                  access
                                    .nombre_completo
                                  ??
                                  "Persona desconocida"
                                }

                              </strong>


                              <div className="secondary-text">

                                {
                                  access
                                    .codigo_biometrico
                                  ? `Código ${access.codigo_biometrico}`
                                  : "Sin identificar"
                                }

                              </div>

                            </div>

                          </div>

                        </td>


                        <td>
                          {
                            access.viviendas
                            || "-"
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

                          <span className="similarity-value">

                            {
                              access.similitud
                              !== null
                                ? Number(
                                    access.similitud
                                  ).toFixed(3)
                                : "-"
                            }

                          </span>

                        </td>


                        <td>

                          {
                            access.puerta_abierta
                              ? (

                                <span className="door-open">
                                  ABIERTA
                                </span>

                              )
                              : (

                                <span className="door-closed">
                                  CERRADA
                                </span>

                              )
                          }

                        </td>


                        <td>

                          {
                            access
                              .total_notificaciones
                            === 0
                              ? (

                                <span className="secondary-text">
                                  Sin notificación
                                </span>

                              )
                              : access
                                  .notificaciones_error
                                > 0
                                ? (

                                  <span className="badge badge-danger">
                                    ERROR
                                  </span>

                                )
                                : (

                                  <span className="badge badge-success">
                                    ENVIADA
                                  </span>

                                )
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


          {
            accesses.length === 0
            && (

              <div className="empty-state">
                No existen registros
                para el filtro seleccionado.
              </div>

            )
          }

        </section>

      )}

    </>
  );

}


export default AccesosPage;