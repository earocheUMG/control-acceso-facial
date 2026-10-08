import {
  FormEvent,
  useEffect,
  useState,
} from "react";


interface Person {
  id: number;
  codigo_biometrico: string | null;
  nombre_completo: string;
  tipo: string;
  email: string | null;
  telefono: string | null;
  activo: boolean;
  viviendas: string[];
  biometria_configurada: boolean;
}


interface PeopleResponse {
  total: number;
  personas: Person[];
}


interface House {
  id: number;
  codigo: string;
  direccion: string | null;
  activa: boolean;
}


interface HousesResponse {
  total: number;
  viviendas: House[];
}


interface PersonForm {
  nombre_completo: string;
  tipo: string;
  email: string;
  telefono: string;
  vivienda_id: string;
  es_responsable_notificacion: boolean;
}


const initialForm: PersonForm = {
  nombre_completo: "",
  tipo: "RESIDENTE",
  email: "",
  telefono: "",
  vivienda_id: "",
  es_responsable_notificacion: false,
};


function PersonasPage() {

  const [people, setPeople] =
    useState<Person[]>([]);

  const [houses, setHouses] =
    useState<House[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  const [success, setSuccess] =
    useState<string | null>(null);

  const [showModal, setShowModal] =
    useState(false);

  const [saving, setSaving] =
    useState(false);

  const [form, setForm] =
    useState<PersonForm>(
      initialForm
    );


  // ==========================================
  // CARGAR PERSONAS
  // ==========================================

  const loadPeople =
    async () => {

      try {

        const response =
          await fetch(
            "http://127.0.0.1:8000/api/personas"
          );

        if (!response.ok) {

          throw new Error(
            "No fue posible consultar las personas."
          );

        }

        const data:
          PeopleResponse =
            await response.json();

        setPeople(
          data.personas
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


  // ==========================================
  // CARGAR VIVIENDAS
  // ==========================================

  const loadHouses =
    async () => {

      try {

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

      }

    };


  // ==========================================
  // CARGA INICIAL
  // ==========================================

  const loadData =
    async () => {

      setLoading(
        true
      );

      setError(
        null
      );

      await Promise.all([
        loadPeople(),
        loadHouses(),
      ]);

      setLoading(
        false
      );

    };


  useEffect(() => {

    loadData();

  }, []);


  // ==========================================
  // ABRIR FORMULARIO
  // ==========================================

  const openModal = () => {

    setForm(
      initialForm
    );

    setError(
      null
    );

    setSuccess(
      null
    );

    setShowModal(
      true
    );

  };


  // ==========================================
  // CERRAR FORMULARIO
  // ==========================================

  const closeModal = () => {

    if (saving) {
      return;
    }

    setShowModal(
      false
    );

  };


  // ==========================================
  // CAMBIAR TIPO
  // ==========================================

  const handleTypeChange =
    (tipo: string) => {

      setForm(
        (current) => ({
          ...current,
          tipo,

          vivienda_id:
            tipo === "SEGURIDAD"
              ? ""
              : current.vivienda_id,

          es_responsable_notificacion:
            tipo === "RESIDENTE"
              ? current
                  .es_responsable_notificacion
              : false,
        })
      );

    };


  // ==========================================
  // CREAR PERSONA
  // ==========================================

  const handleSubmit =
    async (
      event: FormEvent
    ) => {

      event.preventDefault();

      setError(
        null
      );

      setSuccess(
        null
      );


      if (
        (
          form.tipo === "RESIDENTE"
          ||
          form.tipo === "TRABAJADOR"
        )
        &&
        !form.vivienda_id
      ) {

        setError(
          "Debe seleccionar una vivienda."
        );

        return;

      }


      try {

        setSaving(
          true
        );


        const payload = {

          nombre_completo:
            form.nombre_completo
              .trim(),

          tipo:
            form.tipo,

          email:
            form.email.trim()
              || null,

          telefono:
            form.telefono.trim()
              || null,

          vivienda_id:
            form.tipo === "SEGURIDAD"
              ? null
              : Number(
                  form.vivienda_id
                ),

          es_responsable_notificacion:
            form.tipo === "RESIDENTE"
              ? form
                  .es_responsable_notificacion
              : false,

        };


        const response =
          await fetch(
            "http://127.0.0.1:8000/api/personas",
            {
              method: "POST",

              headers: {
                "Content-Type":
                  "application/json",
              },

              body:
                JSON.stringify(
                  payload
                ),
            }
          );


        const result =
          await response.json();


        if (!response.ok) {

          let message =
            "No fue posible crear la persona.";


          if (
            typeof result.detail
            === "string"
          ) {

            message =
              result.detail;

          } else if (
            Array.isArray(
              result.detail
            )
          ) {

            message =
              result.detail
                .map(
                  (
                    item: {
                      msg?: string;
                    }
                  ) =>
                    item.msg
                    ?? "Dato inválido"
                )
                .join(", ");

          }


          throw new Error(
            message
          );

        }


        setSuccess(
          "Persona creada correctamente. "
          + "La biometría está pendiente de enrolamiento."
        );


        setShowModal(
          false
        );


        await loadPeople();


      } catch (err) {

        if (
          err instanceof Error
        ) {

          setError(
            err.message
          );

        }

      } finally {

        setSaving(
          false
        );

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
            Personas
          </h2>

          <p>
            Personas registradas
            en el sistema
          </p>

        </div>


        <div className="header-actions">

          <button
            className="refresh-button"
            onClick={
              loadData
            }
          >
            Actualizar
          </button>


          <button
            className="primary-button"
            onClick={
              openModal
            }
          >
            + Nueva persona
          </button>

        </div>

      </header>


      {/* =====================================
          MENSAJES
      ====================================== */}

      {success && (
        <div className="success-message">
          {success}
        </div>
      )}


      {error && (
        <div className="error-message">
          {error}
        </div>
      )}


      {loading && (
        <div className="message">
          Cargando personas...
        </div>
      )}


      {/* =====================================
          TABLA
      ====================================== */}

      {!loading && (

        <section className="panel">

          <div className="panel-header">

            <div>

              <h3>
                Personas registradas
              </h3>

              <p>
                Total: {people.length}
              </p>

            </div>

          </div>


          <div className="table-container">

            <table>

              <thead>

                <tr>

                  <th>
                    Código
                  </th>

                  <th>
                    Persona
                  </th>

                  <th>
                    Tipo
                  </th>

                  <th>
                    Vivienda
                  </th>

                  <th>
                    Biometría
                  </th>

                  <th>
                    Estado
                  </th>

                </tr>

              </thead>


              <tbody>

                {people.map(
                  (person) => (

                    <tr
                      key={
                        person.id
                      }
                    >

                      <td>

                        {
                          person
                            .codigo_biometrico
                          ?? "-"
                        }

                      </td>


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
                                person.email
                                ??
                                "Sin correo"
                              }

                            </div>

                          </div>

                        </div>

                      </td>


                      <td>

                        {
                          person.tipo
                        }

                      </td>


                      <td>

                        {
                          person.viviendas
                            .length > 0
                            ?
                              person.viviendas
                                .join(", ")
                            :
                              "Sin vivienda"
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

                        <span
                          className={
                            person.activo
                            ?
                              "badge badge-success"
                            :
                              "badge badge-danger"
                          }
                        >

                          {
                            person.activo
                            ?
                              "ACTIVO"
                            :
                              "INACTIVO"
                          }

                        </span>

                      </td>

                    </tr>

                  )
                )}

              </tbody>

            </table>

          </div>

        </section>

      )}


      {/* =====================================
          MODAL NUEVA PERSONA
      ====================================== */}

      {showModal && (

        <div className="modal-backdrop">

          <div className="modal">

            <div className="modal-header">

              <div>

                <h3>
                  Nueva persona
                </h3>

                <p>
                  Registrar una persona
                  en el sistema
                </p>

              </div>


              <button
                type="button"
                className="modal-close"
                onClick={
                  closeModal
                }
              >
                ×
              </button>

            </div>


            <form
              onSubmit={
                handleSubmit
              }
            >

              <div className="modal-body">


                <div className="form-group">

                  <label>
                    Nombre completo *
                  </label>

                  <input
                    type="text"
                    required
                    minLength={3}
                    maxLength={150}
                    value={
                      form.nombre_completo
                    }
                    onChange={
                      (event) =>
                        setForm(
                          {
                            ...form,
                            nombre_completo:
                              event.target.value,
                          }
                        )
                    }
                    placeholder="Ej. Juan Pérez"
                  />

                </div>


                <div className="form-row">


                  <div className="form-group">

                    <label>
                      Tipo *
                    </label>

                    <select
                      value={
                        form.tipo
                      }
                      onChange={
                        (event) =>
                          handleTypeChange(
                            event.target.value
                          )
                      }
                    >

                      <option
                        value="RESIDENTE"
                      >
                        Residente
                      </option>

                      <option
                        value="TRABAJADOR"
                      >
                        Trabajador
                      </option>

                      <option
                        value="SEGURIDAD"
                      >
                        Seguridad
                      </option>

                    </select>

                  </div>


                  {
                    form.tipo
                    !== "SEGURIDAD"
                    && (

                      <div className="form-group">

                        <label>
                          Vivienda *
                        </label>

                        <select
                          required
                          value={
                            form.vivienda_id
                          }
                          onChange={
                            (event) =>
                              setForm(
                                {
                                  ...form,
                                  vivienda_id:
                                    event
                                      .target
                                      .value,
                                }
                              )
                          }
                        >

                          <option value="">
                            Seleccione...
                          </option>


                          {
                            houses.map(
                              (house) => (

                                <option
                                  key={
                                    house.id
                                  }
                                  value={
                                    house.id
                                  }
                                >

                                  {
                                    house.codigo
                                  }

                                </option>

                              )
                            )
                          }

                        </select>

                      </div>

                    )
                  }

                </div>


                <div className="form-group">

                  <label>
                    Correo electrónico
                  </label>

                  <input
                    type="email"
                    value={
                      form.email
                    }
                    onChange={
                      (event) =>
                        setForm(
                          {
                            ...form,
                            email:
                              event.target.value,
                          }
                        )
                    }
                    placeholder="correo@ejemplo.com"
                  />

                </div>


                <div className="form-group">

                  <label>
                    Teléfono
                  </label>

                  <input
                    type="text"
                    maxLength={30}
                    value={
                      form.telefono
                    }
                    onChange={
                      (event) =>
                        setForm(
                          {
                            ...form,
                            telefono:
                              event.target.value,
                          }
                        )
                    }
                    placeholder="Ej. 5555-5555"
                  />

                </div>


                {
                  form.tipo
                  === "RESIDENTE"
                  && (

                    <label className="checkbox-row">

                      <input
                        type="checkbox"
                        checked={
                          form
                            .es_responsable_notificacion
                        }
                        onChange={
                          (event) =>
                            setForm(
                              {
                                ...form,
                                es_responsable_notificacion:
                                  event
                                    .target
                                    .checked,
                              }
                            )
                        }
                      />

                      <div>

                        <strong>
                          Responsable de notificaciones
                        </strong>

                        <span>
                          Recibirá avisos relacionados
                          con ingresos a esta vivienda.
                        </span>

                      </div>

                    </label>

                  )
                }


                <div className="form-info">

                  <strong>
                    Biometría pendiente
                  </strong>

                  <p>
                    Después de crear la persona
                    deberá realizarse el enrolamiento
                    facial para habilitar el
                    reconocimiento.
                  </p>

                </div>

              </div>


              <div className="modal-footer">

                <button
                  type="button"
                  className="secondary-button"
                  onClick={
                    closeModal
                  }
                  disabled={
                    saving
                  }
                >
                  Cancelar
                </button>


                <button
                  type="submit"
                  className="primary-button"
                  disabled={
                    saving
                  }
                >

                  {
                    saving
                    ?
                      "Guardando..."
                    :
                      "Crear persona"
                  }

                </button>

              </div>

            </form>

          </div>

        </div>

      )}

    </>
  );

}


export default PersonasPage;