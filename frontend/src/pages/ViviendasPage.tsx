import {
  useEffect,
  useState,
} from "react";


interface House {
  id: number;
  codigo: string;
  direccion: string | null;
  activa: boolean;
  total_personas: number;
  residentes: number;
  trabajadores: number;
  responsables_notificacion: number;
}


interface HousesResponse {
  total: number;
  viviendas: House[];
}


interface HousePerson {
  id: number;
  codigo_biometrico: string | null;
  nombre_completo: string;
  tipo: string;
  email: string | null;
  telefono: string | null;
  activo: boolean;
  relacion: string;
  es_responsable_notificacion: boolean;
  biometria_configurada: boolean;
}


interface HouseDetailResponse {
  vivienda: {
    id: number;
    codigo: string;
    direccion: string | null;
    activa: boolean;
    creado_en: string;
  };

  personas: HousePerson[];
}


function ViviendasPage() {

  const [houses, setHouses] =
    useState<House[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  const [selectedHouse, setSelectedHouse] =
    useState<HouseDetailResponse | null>(
      null
    );

  const [loadingDetail, setLoadingDetail] =
    useState(false);


  // ==========================================
  // CARGAR VIVIENDAS
  // ==========================================

  const loadHouses =
    async () => {

      try {

        setError(null);

        const response =
          await fetch(
            "http://127.0.0.1:8000/api/viviendas"
          );

        if (!response.ok) {

          throw new Error(
            "No fue posible consultar las viviendas."
          );

        }

        const data:
          HousesResponse =
            await response.json();

        setHouses(
          data.viviendas
        );

      } catch (err) {

        if (
          err instanceof Error
        ) {

          setError(
            err.message
          );

        }

      } finally {

        setLoading(false);

      }

    };


  useEffect(() => {

    loadHouses();

  }, []);


  // ==========================================
  // VER DETALLE
  // ==========================================

  const loadHouseDetail =
    async (
      houseId: number
    ) => {

      try {

        setLoadingDetail(true);
        setError(null);

        const response =
          await fetch(
            `http://127.0.0.1:8000/api/viviendas/${houseId}`
          );

        if (!response.ok) {

          throw new Error(
            "No fue posible consultar el detalle."
          );

        }

        const data:
          HouseDetailResponse =
            await response.json();

        setSelectedHouse(
          data
        );

      } catch (err) {

        if (
          err instanceof Error
        ) {

          setError(
            err.message
          );

        }

      } finally {

        setLoadingDetail(false);

      }

    };


  return (
    <>

      {/* =====================================
          ENCABEZADO
      ====================================== */}

      <header className="topbar">

        <div>

          <h2>
            Viviendas
          </h2>

          <p>
            Viviendas registradas
            y personas asociadas
          </p>

        </div>


        <button
          className="refresh-button"
          onClick={
            loadHouses
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
          Cargando viviendas...
        </div>
      )}


      {!loading && (

        <section className="houses-grid">

          {houses.map(
            (house) => (

              <article
                key={house.id}
                className="house-card"
              >

                <div className="house-card-header">

                  <div className="house-icon">
                    🏠
                  </div>


                  <div>

                    <h3>
                      {house.codigo}
                    </h3>

                    <p>
                      {
                        house.direccion
                        ??
                        "Sin dirección registrada"
                      }
                    </p>

                  </div>

                </div>


                <div className="house-stats">

                  <div>

                    <span>
                      Personas
                    </span>

                    <strong>
                      {house.total_personas}
                    </strong>

                  </div>


                  <div>

                    <span>
                      Residentes
                    </span>

                    <strong>
                      {house.residentes}
                    </strong>

                  </div>


                  <div>

                    <span>
                      Trabajadores
                    </span>

                    <strong>
                      {house.trabajadores}
                    </strong>

                  </div>

                </div>


                <div className="house-responsible">

                  Responsables de notificación:{" "}

                  <strong>
                    {
                      house
                        .responsables_notificacion
                    }
                  </strong>

                </div>


                <button
                  className="primary-button house-button"
                  onClick={
                    () =>
                      loadHouseDetail(
                        house.id
                      )
                  }
                >
                  Ver detalle
                </button>

              </article>

            )
          )}

        </section>

      )}


      {/* =====================================
          DETALLE VIVIENDA
      ====================================== */}

      {selectedHouse && (

        <div className="modal-backdrop">

          <div className="modal house-detail-modal">

            <div className="modal-header">

              <div>

                <h3>
                  {
                    selectedHouse
                      .vivienda.codigo
                  }
                </h3>

                <p>
                  {
                    selectedHouse
                      .vivienda.direccion
                    ??
                    "Sin dirección registrada"
                  }
                </p>

              </div>


              <button
                className="modal-close"
                onClick={
                  () =>
                    setSelectedHouse(
                      null
                    )
                }
              >
                ×
              </button>

            </div>


            <div className="modal-body">

              <h4 className="house-detail-title">
                Personas asociadas
              </h4>


              {
                selectedHouse.personas.length
                === 0
                ? (

                  <div className="message">
                    No existen personas
                    asociadas.
                  </div>

                )
                : (

                  <div className="table-container">

                    <table>

                      <thead>

                        <tr>

                          <th>
                            Persona
                          </th>

                          <th>
                            Relación
                          </th>

                          <th>
                            Biometría
                          </th>

                          <th>
                            Notificación
                          </th>

                        </tr>

                      </thead>


                      <tbody>

                        {
                          selectedHouse
                            .personas
                            .map(
                              (person) => (

                                <tr
                                  key={
                                    person.id
                                  }
                                >

                                  <td>

                                    <div className="person-cell">

                                      <div className="person-avatar">

                                        {
                                          person
                                            .nombre_completo
                                            .charAt(0)
                                            .toUpperCase()
                                        }

                                      </div>


                                      <div>

                                        <strong>
                                          {
                                            person
                                              .nombre_completo
                                          }
                                        </strong>

                                        <div className="secondary-text">

                                          {
                                            person
                                              .codigo_biometrico
                                            ?
                                              `Código ${person.codigo_biometrico}`
                                            :
                                              "Sin código biométrico"
                                          }

                                        </div>

                                      </div>

                                    </div>

                                  </td>


                                  <td>
                                    {
                                      person.relacion
                                    }
                                  </td>


                                  <td>

                                    <span
                                      className={
                                        person
                                          .biometria_configurada
                                          ?
                                            "badge badge-success"
                                          :
                                            "badge badge-warning"
                                      }
                                    >

                                      {
                                        person
                                          .biometria_configurada
                                          ?
                                            "CONFIGURADA"
                                          :
                                            "PENDIENTE"
                                      }

                                    </span>

                                  </td>


                                  <td>

                                    {
                                      person
                                        .es_responsable_notificacion
                                      ? (

                                        <span className="badge badge-info">
                                          RESPONSABLE
                                        </span>

                                      )
                                      : (
                                        "-"
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

                )
              }

            </div>

          </div>

        </div>

      )}


      {loadingDetail && (
        <div className="floating-loading">
          Cargando detalle...
        </div>
      )}

    </>
  );
}


export default ViviendasPage;