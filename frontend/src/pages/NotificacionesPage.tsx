import {
  useEffect,
  useState,
} from "react";

import {
  apiFetch
} from "../services/api";


interface Notification {
  id: number;
  acceso_id: number;
  destinatario_email: string;
  tipo: string;
  estado: string;
  creado_en: string;
  enviado_en: string | null;
  error: string | null;

  acceso_fecha: string;
  acceso_resultado: string;
  similitud: number | null;

  persona_id: number | null;
  codigo_biometrico: string | null;
  nombre_completo: string | null;

  punto_acceso: string;
}


interface NotificationResponse {
  total: number;
  filtro_tipo: string | null;
  filtro_estado: string | null;
  notificaciones: Notification[];
}


type TypeFilter =
  | "TODOS"
  | "INGRESO"
  | "ALERTA_SEGURIDAD";


type StatusFilter =
  | "TODOS"
  | "ENVIADA"
  | "PENDIENTE"
  | "ERROR";


async function fetchNotifications(
  typeFilter: TypeFilter,
  statusFilter: StatusFilter,
  limit: number
): Promise<NotificationResponse> {

  let url =
    `http://127.0.0.1:8000/api/notificaciones?limit=${limit}`;


  if (
    typeFilter !== "TODOS"
  ) {

    url +=
      `&tipo=${typeFilter}`;

  }


  if (
    statusFilter !== "TODOS"
  ) {

    url +=
      `&estado=${statusFilter}`;

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
        : "No fue posible consultar las notificaciones."
    );

  }


  return result;
}


function formatDate(
  date: string | null
) {

  if (!date) {
    return "-";
  }


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


function NotificacionesPage() {

  const [
    notifications,
    setNotifications
  ] = useState<Notification[]>([]);


  const [
    typeFilter,
    setTypeFilter
  ] = useState<TypeFilter>(
    "TODOS"
  );


  const [
    statusFilter,
    setStatusFilter
  ] = useState<StatusFilter>(
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


  useEffect(() => {

    let active = true;


    const request =
      async () => {

        try {

          const data =
            await fetchNotifications(
              typeFilter,
              statusFilter,
              limit
            );


          if (!active) {
            return;
          }


          setNotifications(
            data.notificaciones
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
    typeFilter,
    statusFilter,
    limit
  ]);


  const refreshNotifications =
    async () => {

      try {

        const data =
          await fetchNotifications(
            typeFilter,
            statusFilter,
            limit
          );


        setNotifications(
          data.notificaciones
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


  const sentCount =
    notifications.filter(
      (item) =>
        item.estado === "ENVIADA"
    ).length;


  const pendingCount =
    notifications.filter(
      (item) =>
        item.estado === "PENDIENTE"
    ).length;


  const errorCount =
    notifications.filter(
      (item) =>
        item.estado === "ERROR"
    ).length;


  return (
    <>

      <header className="topbar">

        <div>

          <h2>
            Notificaciones
          </h2>

          <p>
            Historial de correos
            y alertas del sistema
          </p>

        </div>


        <button
          type="button"
          className="refresh-button"
          onClick={
            refreshNotifications
          }
        >
          Actualizar
        </button>

      </header>


      <section className="notification-summary">

        <article className="access-summary-card">

          <span>
            Registros mostrados
          </span>

          <strong>
            {notifications.length}
          </strong>

        </article>


        <article
          className="
            access-summary-card
            access-summary-success
          "
        >

          <span>
            Enviadas
          </span>

          <strong>
            {sentCount}
          </strong>

        </article>


        <article
          className="
            access-summary-card
            notification-summary-warning
          "
        >

          <span>
            Pendientes
          </span>

          <strong>
            {pendingCount}
          </strong>

        </article>


        <article
          className="
            access-summary-card
            access-summary-danger
          "
        >

          <span>
            Errores
          </span>

          <strong>
            {errorCount}
          </strong>

        </article>

      </section>


      <section className="notification-toolbar">

        <div>

          <span className="filter-label">
            Tipo
          </span>


          <div className="access-filters">

            <button
              type="button"
              className={
                typeFilter === "TODOS"
                  ? "filter-button active"
                  : "filter-button"
              }
              onClick={
                () =>
                  setTypeFilter(
                    "TODOS"
                  )
              }
            >
              Todos
            </button>


            <button
              type="button"
              className={
                typeFilter === "INGRESO"
                  ? "filter-button active success"
                  : "filter-button"
              }
              onClick={
                () =>
                  setTypeFilter(
                    "INGRESO"
                  )
              }
            >
              Ingresos
            </button>


            <button
              type="button"
              className={
                typeFilter
                === "ALERTA_SEGURIDAD"
                  ? "filter-button active danger"
                  : "filter-button"
              }
              onClick={
                () =>
                  setTypeFilter(
                    "ALERTA_SEGURIDAD"
                  )
              }
            >
              Alertas
            </button>

          </div>

        </div>


        <div>

          <span className="filter-label">
            Estado
          </span>

          <select
            className="notification-select"
            value={
              statusFilter
            }
            onChange={
              (event) => {

                const value =
                  event.target.value;


                if (
                  value === "TODOS"
                  ||
                  value === "ENVIADA"
                  ||
                  value === "PENDIENTE"
                  ||
                  value === "ERROR"
                ) {

                  setStatusFilter(
                    value
                  );

                }

              }
            }
          >

            <option value="TODOS">
              Todos
            </option>

            <option value="ENVIADA">
              Enviada
            </option>

            <option value="PENDIENTE">
              Pendiente
            </option>

            <option value="ERROR">
              Error
            </option>

          </select>

        </div>


        <div>

          <span className="filter-label">
            Mostrar
          </span>

          <select
            className="notification-select"
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

            <option value={10}>10</option>
            <option value={25}>25</option>
            <option value={50}>50</option>
            <option value={100}>100</option>

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
          Cargando notificaciones...
        </div>

      )}


      {!loading && !error && (

        <section className="panel">

          <div className="panel-header">

            <div>

              <h3>
                Historial de notificaciones
              </h3>

              <p>
                Actualización automática
                cada 10 segundos
              </p>

            </div>

          </div>


          <div className="table-container">

            <table>

              <thead>

                <tr>

                  <th>ID</th>
                  <th>Tipo</th>
                  <th>Persona</th>
                  <th>Destinatario</th>
                  <th>Estado</th>
                  <th>Acceso</th>
                  <th>Punto</th>
                  <th>Creada</th>
                  <th>Enviada</th>

                </tr>

              </thead>


              <tbody>

                {
                  notifications.map(
                    (notification) => (

                      <tr
                        key={
                          notification.id
                        }
                      >

                        <td>

                          <span className="access-id">
                            #{notification.id}
                          </span>

                        </td>


                        <td>

                          <span
                            className={
                              notification.tipo
                              === "INGRESO"
                                ? "badge badge-info"
                                : "badge badge-danger"
                            }
                          >

                            {
                              notification.tipo
                              === "INGRESO"
                                ? "INGRESO"
                                : "ALERTA"
                            }

                          </span>

                        </td>


                        <td>

                          {
                            notification
                              .nombre_completo
                            ??
                            "Desconocido"
                          }

                          <div className="secondary-text">

                            {
                              notification
                                .codigo_biometrico
                              ? `Código ${notification.codigo_biometrico}`
                              : "Sin identificar"
                            }

                          </div>

                        </td>


                        <td>
                          {
                            notification
                              .destinatario_email
                          }
                        </td>


                        <td>

                          <span
                            className={
                              notification.estado
                              === "ENVIADA"
                                ? "badge badge-success"
                                : notification.estado
                                  === "ERROR"
                                  ? "badge badge-danger"
                                  : "badge badge-warning"
                            }
                          >

                            {
                              notification.estado
                            }

                          </span>

                        </td>


                        <td>

                          <span
                            className={
                              notification
                                .acceso_resultado
                              === "AUTORIZADO"
                                ? "badge badge-success"
                                : "badge badge-danger"
                            }
                          >

                            {
                              notification
                                .acceso_resultado
                            }

                          </span>

                        </td>


                        <td>
                          {
                            notification
                              .punto_acceso
                          }
                        </td>


                        <td>
                          {
                            formatDate(
                              notification
                                .creado_en
                            )
                          }
                        </td>


                        <td>
                          {
                            formatDate(
                              notification
                                .enviado_en
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

      )}

    </>
  );

}


export default NotificacionesPage;