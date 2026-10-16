import {
  useEffect,
  useState,
} from "react";

import type {
  FormEvent
} from "react";

import {
  apiFetch
} from "../services/api";


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


async function fetchHouses():
Promise<HousesResponse> {

  const response =
    await apiFetch(
      "http://127.0.0.1:8000/api/viviendas"
    );


  const result =
    await response.json();


  if (!response.ok) {

    throw new Error(
      typeof result.detail === "string"
        ? result.detail
        : "No fue posible consultar las viviendas."
    );

  }


  return result;
}


async function fetchHouseDetail(
  houseId: number
): Promise<HouseDetailResponse> {

  const response =
    await apiFetch(
      `http://127.0.0.1:8000/api/viviendas/${houseId}`
    );


  const result =
    await response.json();


  if (!response.ok) {

    throw new Error(
      typeof result.detail === "string"
        ? result.detail
        : "No fue posible consultar el detalle."
    );

  }


  return result;
}


async function createHouse(
  code: string,
  address: string
): Promise<void> {

  const normalizedAddress =
    address.trim();


  const response =
    await apiFetch(
      "http://127.0.0.1:8000/api/viviendas",
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify(
          {
            codigo: code.trim(),
            direccion:
              normalizedAddress
                ? normalizedAddress
                : null,
          }
        ),
      }
    );


  const result =
    await response.json();


  if (!response.ok) {

    throw new Error(
      typeof result.detail === "string"
        ? result.detail
        : "No fue posible crear la vivienda."
    );

  }
}


function ViviendasPage() {

  const [
    houses,
    setHouses
  ] = useState<House[]>([]);


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


  const [
    selectedHouse,
    setSelectedHouse
  ] = useState<HouseDetailResponse | null>(
    null
  );


  const [
    loadingDetail,
    setLoadingDetail
  ] = useState(false);


  const [
    showCreateModal,
    setShowCreateModal
  ] = useState(false);


  const [
    newHouseCode,
    setNewHouseCode
  ] = useState("");


  const [
    newHouseAddress,
    setNewHouseAddress
  ] = useState("");


  const [
    creatingHouse,
    setCreatingHouse
  ] = useState(false);


  const [
    successMessage,
    setSuccessMessage
  ] = useState<string | null>(
    null
  );


  // ==========================================
  // CARGA INICIAL
  // ==========================================

  useEffect(() => {

    let active = true;


    fetchHouses()
      .then(
        (data) => {

          if (!active) {
            return;
          }


          setHouses(
            data.viviendas
          );


          setError(
            null
          );


          setLoading(
            false
          );

        }
      )
      .catch(
        (err) => {

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


          setLoading(
            false
          );

        }
      );


    return () => {

      active = false;

    };

  }, []);


  const refreshHouses =
    async () => {

      try {

        const data =
          await fetchHouses();


        setHouses(
          data.viviendas
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


  const loadHouseDetail =
    async (
      houseId: number
    ) => {

      try {

        setLoadingDetail(
          true
        );


        setError(
          null
        );


        const data =
          await fetchHouseDetail(
            houseId
          );


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

        setLoadingDetail(
          false
        );

      }

    };


  // ==========================================
  // CREAR VIVIENDA
  // ==========================================

  const openCreateModal =
    () => {

      setNewHouseCode(
        ""
      );


      setNewHouseAddress(
        ""
      );


      setError(
        null
      );


      setSuccessMessage(
        null
      );


      setShowCreateModal(
        true
      );

    };


  const closeCreateModal =
    () => {

      if (creatingHouse) {
        return;
      }


      setShowCreateModal(
        false
      );

    };


  const handleCreateHouse =
    async (
      event: FormEvent<HTMLFormElement>
    ) => {

      event.preventDefault();


      const code =
        newHouseCode
          .trim()
          .toUpperCase();


      if (!code) {

        setError(
          "El código de la vivienda es obligatorio."
        );

        return;

      }


      try {

        setCreatingHouse(
          true
        );


        setError(
          null
        );


        setSuccessMessage(
          null
        );


        await createHouse(
          code,
          newHouseAddress
        );


        await refreshHouses();


        setShowCreateModal(
          false
        );


        setNewHouseCode(
          ""
        );


        setNewHouseAddress(
          ""
        );


        setSuccessMessage(
          `Vivienda ${code} creada correctamente.`
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

        setCreatingHouse(
          false
        );

      }

    };


  return (
    <>

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


        <div
          style={
            {
              display: "flex",
              gap: "0.75rem",
              alignItems: "center",
            }
          }
        >

          <button
            type="button"
            className="primary-button"
            onClick={
              openCreateModal
            }
          >
            + Nueva vivienda
          </button>


          <button
            type="button"
            className="refresh-button"
            onClick={
              refreshHouses
            }
          >
            Actualizar
          </button>

        </div>

      </header>


      {successMessage && (

        <div className="message">
          {successMessage}
        </div>

      )}


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

          {
            houses.map(
              (house) => (

                <article
                  key={
                    house.id
                  }
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
                        {
                          house
                            .total_personas
                        }
                      </strong>

                    </div>


                    <div>

                      <span>
                        Residentes
                      </span>

                      <strong>
                        {
                          house.residentes
                        }
                      </strong>

                    </div>


                    <div>

                      <span>
                        Trabajadores
                      </span>

                      <strong>
                        {
                          house.trabajadores
                        }
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
                    type="button"
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
            )
          }

        </section>

      )}


      {showCreateModal && (

        <div className="modal-backdrop">

          <div className="modal house-detail-modal">

            <div className="modal-header">

              <div>

                <h3>
                  Nueva vivienda
                </h3>

                <p>
                  Registre una nueva vivienda
                  para asociar residentes y trabajadores.
                </p>

              </div>


              <button
                type="button"
                className="modal-close"
                disabled={
                  creatingHouse
                }
                onClick={
                  closeCreateModal
                }
              >
                ×
              </button>

            </div>


            <form
              onSubmit={
                handleCreateHouse
              }
            >

              <div
                className="modal-body"
                style={
                  {
                    display: "grid",
                    gap: "1rem",
                  }
                }
              >

                <label
                  style={
                    {
                      display: "grid",
                      gap: "0.4rem",
                    }
                  }
                >

                  <strong>
                    Código de vivienda *
                  </strong>

                  <input
                    type="text"
                    value={
                      newHouseCode
                    }
                    disabled={
                      creatingHouse
                    }
                    placeholder="Ej. CASA-004"
                    autoFocus
                    required
                    onChange={
                      (event) =>
                        setNewHouseCode(
                          event.target.value
                        )
                    }
                    style={
                      {
                        width: "100%",
                        boxSizing: "border-box",
                        padding: "0.75rem",
                        border: "1px solid #d1d5db",
                        borderRadius: "8px",
                      }
                    }
                  />

                </label>


                <label
                  style={
                    {
                      display: "grid",
                      gap: "0.4rem",
                    }
                  }
                >

                  <strong>
                    Dirección
                  </strong>

                  <input
                    type="text"
                    value={
                      newHouseAddress
                    }
                    disabled={
                      creatingHouse
                    }
                    placeholder="Ej. Sector A, vivienda 4"
                    onChange={
                      (event) =>
                        setNewHouseAddress(
                          event.target.value
                        )
                    }
                    style={
                      {
                        width: "100%",
                        boxSizing: "border-box",
                        padding: "0.75rem",
                        border: "1px solid #d1d5db",
                        borderRadius: "8px",
                      }
                    }
                  />

                </label>


                <div
                  style={
                    {
                      display: "flex",
                      justifyContent: "flex-end",
                      gap: "0.75rem",
                      marginTop: "0.5rem",
                    }
                  }
                >

                  <button
                    type="button"
                    className="refresh-button"
                    disabled={
                      creatingHouse
                    }
                    onClick={
                      closeCreateModal
                    }
                  >
                    Cancelar
                  </button>


                  <button
                    type="submit"
                    className="primary-button"
                    disabled={
                      creatingHouse
                    }
                  >
                    {
                      creatingHouse
                        ? "Guardando..."
                        : "Guardar vivienda"
                    }
                  </button>

                </div>

              </div>

            </form>

          </div>

        </div>

      )}


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
                type="button"
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
                selectedHouse
                  .personas.length === 0
                  ? (

                    <div className="message">
                      No existen personas asociadas.
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
                              .personas.map(
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
                                              person.codigo_biometrico
                                                ? `Código ${person.codigo_biometrico}`
                                                : "Sin código biométrico"
                                            }

                                          </div>

                                        </div>

                                      </div>

                                    </td>


                                    <td>
                                      {person.relacion}
                                    </td>


                                    <td>

                                      <span
                                        className={
                                          person
                                            .biometria_configurada
                                            ? "badge badge-success"
                                            : "badge badge-warning"
                                        }
                                      >

                                        {
                                          person
                                            .biometria_configurada
                                            ? "CONFIGURADA"
                                            : "PENDIENTE"
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
                                          : "-"
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