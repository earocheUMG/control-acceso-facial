import {
  useEffect,
  useState,
} from "react";

import type {
  FormEvent,
} from "react";

import EnrollmentModal
  from "../components/EnrollmentModal";

import {
  apiFetch
} from "../services/api";


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


interface EnrollmentPerson {
  id: number;
  nombre_completo: string;
}


interface PersonDetailResponse {

  persona: {
    id: number;
    codigo_biometrico: string | null;
    nombre_completo: string;
    tipo: string;
    email: string | null;
    telefono: string | null;
    activo: boolean;
    fecha_inicio: string | null;
    fecha_fin: string | null;
    creado_en: string;
  };

  vivienda: {
    id: number;
    codigo: string;
    direccion: string | null;
    relacion: string;
    es_responsable_notificacion: boolean;
  } | null;

  biometria: {
    modelo: string;
    template_path: string;
    cantidad_muestras: number;
    activo: boolean;
    creado_en: string;
  } | null;
}


const initialForm: PersonForm = {
  nombre_completo: "",
  tipo: "RESIDENTE",
  email: "",
  telefono: "",
  vivienda_id: "",
  es_responsable_notificacion: false,
};


async function fetchPeople():
Promise<PeopleResponse> {

  const response =
    await apiFetch(
      "http://127.0.0.1:8000/api/personas"
    );


  const result =
    await response.json();


  if (!response.ok) {

    throw new Error(
      typeof result.detail === "string"
        ? result.detail
        : "No fue posible consultar las personas."
    );

  }


  return result;
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


async function fetchPersonDetail(
  personId: number
): Promise<PersonDetailResponse> {

  const response =
    await apiFetch(
      `http://127.0.0.1:8000/api/personas/${personId}/detalle`
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


function formatDate(
  value: string | null
) {

  if (!value) {
    return "-";
  }


  return new Intl.DateTimeFormat(
    "es-GT",
    {
      dateStyle: "medium",
      timeStyle: "short",
    }
  ).format(
    new Date(value)
  );

}


function PersonasPage() {

  const [
    people,
    setPeople
  ] = useState<Person[]>([]);


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
    success,
    setSuccess
  ] = useState<string | null>(
    null
  );


  const [
    showCreateModal,
    setShowCreateModal
  ] = useState(false);


  const [
    saving,
    setSaving
  ] = useState(false);


  const [
    form,
    setForm
  ] = useState<PersonForm>(
    initialForm
  );


  const [
    enrollmentPerson,
    setEnrollmentPerson
  ] = useState<EnrollmentPerson | null>(
    null
  );


  const [
    personDetail,
    setPersonDetail
  ] = useState<PersonDetailResponse | null>(
    null
  );


  const [
    detailLoading,
    setDetailLoading
  ] = useState(false);


  const [
    editMode,
    setEditMode
  ] = useState(false);


  const [
    editForm,
    setEditForm
  ] = useState<PersonForm>(
    initialForm
  );


  const [
    savingEdit,
    setSavingEdit
  ] = useState(false);


  const [
    changingStatus,
    setChangingStatus
  ] = useState(false);


  useEffect(() => {

    let active = true;


    Promise.all([
      fetchPeople(),
      fetchHouses(),
    ])
      .then(
        ([
          peopleData,
          housesData,
        ]) => {

          if (!active) {
            return;
          }


          setPeople(
            peopleData.personas
          );


          setHouses(
            housesData.viviendas
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


  const refreshPeople =
    async () => {

      const data =
        await fetchPeople();


      setPeople(
        data.personas
      );

  };


  const refreshAll =
    async () => {

      try {

        const [
          peopleData,
          housesData,
        ] =
          await Promise.all([
            fetchPeople(),
            fetchHouses(),
          ]);


        setPeople(
          peopleData.personas
        );


        setHouses(
          housesData.viviendas
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


  const handleTypeChange =
    (
      tipo: string
    ) => {

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


  const handleSubmit =
    async (
      event: FormEvent
    ) => {

      event.preventDefault();


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


        setError(
          null
        );


        const response =
          await apiFetch(
            "http://127.0.0.1:8000/api/personas",
            {
              method: "POST",

              headers: {
                "Content-Type":
                  "application/json",
              },

              body:
                JSON.stringify({
                  nombre_completo:
                    form
                      .nombre_completo
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
                }),
            }
          );


        const result =
          await response.json();


        if (!response.ok) {

          throw new Error(
            typeof result.detail === "string"
              ? result.detail
              : "No fue posible crear la persona."
          );

        }


        setShowCreateModal(
          false
        );


        setSuccess(
          "Persona creada correctamente. "
          + "La biometría está pendiente de enrolamiento."
        );


        await refreshPeople();


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


  const openPersonDetail =
    async (
      personId: number,
      openEditing = false
    ) => {

      try {

        setDetailLoading(
          true
        );


        const data =
          await fetchPersonDetail(
            personId
          );


        setPersonDetail(
          data
        );


        setEditForm({
          nombre_completo:
            data.persona.nombre_completo,

          tipo:
            data.persona.tipo,

          email:
            data.persona.email
            ?? "",

          telefono:
            data.persona.telefono
            ?? "",

          vivienda_id:
            data.vivienda
              ? String(
                  data.vivienda.id
                )
              : "",

          es_responsable_notificacion:
            data.vivienda
              ?.es_responsable_notificacion
            ?? false,
        });


        setEditMode(
          openEditing
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


      } finally {

        setDetailLoading(
          false
        );

      }

    };


  const handleEditTypeChange =
    (
      tipo: string
    ) => {

      setEditForm(
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


  const savePersonEdit =
    async (
      event: FormEvent
    ) => {

      event.preventDefault();


      if (!personDetail) {
        return;
      }


      try {

        setSavingEdit(
          true
        );


        const response =
          await apiFetch(
            `http://127.0.0.1:8000/api/personas/${personDetail.persona.id}`,
            {
              method: "PUT",

              headers: {
                "Content-Type":
                  "application/json",
              },

              body:
                JSON.stringify({
                  nombre_completo:
                    editForm
                      .nombre_completo
                      .trim(),

                  tipo:
                    editForm.tipo,

                  email:
                    editForm.email.trim()
                    || null,

                  telefono:
                    editForm.telefono.trim()
                    || null,

                  vivienda_id:
                    editForm.tipo
                    === "SEGURIDAD"
                      ? null
                      : Number(
                          editForm.vivienda_id
                        ),

                  es_responsable_notificacion:
                    editForm.tipo
                    === "RESIDENTE"
                      ? editForm
                          .es_responsable_notificacion
                      : false,
                }),
            }
          );


        const result =
          await response.json();


        if (!response.ok) {

          throw new Error(
            typeof result.detail === "string"
              ? result.detail
              : "No fue posible actualizar la persona."
          );

        }


        setPersonDetail(
          result.detalle
        );


        setEditMode(
          false
        );


        setSuccess(
          "Persona actualizada correctamente."
        );


        await refreshPeople();


      } catch (err) {

        if (
          err instanceof Error
        ) {

          setError(
            err.message
          );

        }


      } finally {

        setSavingEdit(
          false
        );

      }

    };


  const togglePersonStatus =
    async () => {

      if (!personDetail) {
        return;
      }


      const newStatus =
        !personDetail.persona.activo;


      if (
        !window.confirm(
          `¿Está seguro de ${
            newStatus
              ? "activar"
              : "inactivar"
          } a ${personDetail.persona.nombre_completo}?`
        )
      ) {

        return;

      }


      try {

        setChangingStatus(
          true
        );


        const response =
          await apiFetch(
            `http://127.0.0.1:8000/api/personas/${personDetail.persona.id}/estado`,
            {
              method: "PATCH",

              headers: {
                "Content-Type":
                  "application/json",
              },

              body:
                JSON.stringify({
                  activo:
                    newStatus,
                }),
            }
          );


        const result =
          await response.json();


        if (!response.ok) {

          throw new Error(
            typeof result.detail === "string"
              ? result.detail
              : "No fue posible cambiar el estado."
          );

        }


        const updated =
          await fetchPersonDetail(
            personDetail.persona.id
          );


        setPersonDetail(
          updated
        );


        setSuccess(
          result.message
        );


        await refreshPeople();


      } catch (err) {

        if (
          err instanceof Error
        ) {

          setError(
            err.message
          );

        }


      } finally {

        setChangingStatus(
          false
        );

      }

    };


  const handleEnrollmentCompleted =
    async (
      biometricCode: string
    ) => {

      setEnrollmentPerson(
        null
      );


      setSuccess(
        "Enrolamiento biométrico completado. "
        + `Código asignado: ${biometricCode}`
      );


      await refreshPeople();

    };


  return (
    <>

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
            type="button"
            className="refresh-button"
            onClick={
              refreshAll
            }
          >
            Actualizar
          </button>


          <button
            type="button"
            className="primary-button"
            onClick={
              () => {

                setForm(
                  initialForm
                );

                setError(
                  null
                );

                setSuccess(
                  null
                );

                setShowCreateModal(
                  true
                );

              }
            }
          >
            + Nueva persona
          </button>

        </div>

      </header>


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
                  <th>Código</th>
                  <th>Persona</th>
                  <th>Tipo</th>
                  <th>Vivienda</th>
                  <th>Biometría</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>

              </thead>


              <tbody>

                {
                  people.map(
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
                                  ?? "Sin correo"
                                }

                              </div>

                            </div>

                          </div>

                        </td>


                        <td>
                          {person.tipo}
                        </td>


                        <td>

                          {
                            person.viviendas.length
                            > 0
                              ? person.viviendas
                                  .join(", ")
                              : "Sin vivienda"
                          }

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

                          <span
                            className={
                              person.activo
                                ? "badge badge-success"
                                : "badge badge-danger"
                            }
                          >

                            {
                              person.activo
                                ? "ACTIVO"
                                : "INACTIVO"
                            }

                          </span>

                        </td>


                        <td>

                          <div className="person-actions">

                            <button
                              type="button"
                              className="action-button"
                              onClick={
                                () =>
                                  openPersonDetail(
                                    person.id
                                  )
                              }
                            >
                              Ver detalle
                            </button>


                            <button
                              type="button"
                              className="action-button"
                              onClick={
                                () =>
                                  openPersonDetail(
                                    person.id,
                                    true
                                  )
                              }
                            >
                              Editar
                            </button>


                            {
                              !person
                                .biometria_configurada
                              &&
                              person.activo
                              && (

                                <button
                                  type="button"
                                  className="enroll-button"
                                  onClick={
                                    () =>
                                      setEnrollmentPerson({
                                        id:
                                          person.id,

                                        nombre_completo:
                                          person
                                            .nombre_completo,
                                      })
                                  }
                                >
                                  Enrolar
                                </button>

                              )
                            }

                          </div>

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


      {showCreateModal && (

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
                  () =>
                    setShowCreateModal(
                      false
                    )
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
                    required
                    value={
                      form.nombre_completo
                    }
                    onChange={
                      (event) =>
                        setForm({
                          ...form,
                          nombre_completo:
                            event.target.value,
                        })
                    }
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

                      <option value="RESIDENTE">
                        Residente
                      </option>

                      <option value="TRABAJADOR">
                        Trabajador
                      </option>

                      <option value="SEGURIDAD">
                        Seguridad
                      </option>

                    </select>

                  </div>


                  {
                    form.tipo !== "SEGURIDAD"
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
                              setForm({
                                ...form,

                                vivienda_id:
                                  event.target.value,
                              })
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

                                  {house.codigo}

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
                    Correo
                  </label>

                  <input
                    type="email"
                    value={
                      form.email
                    }
                    onChange={
                      (event) =>
                        setForm({
                          ...form,

                          email:
                            event.target.value,
                        })
                    }
                  />

                </div>


                <div className="form-group">

                  <label>
                    Teléfono
                  </label>

                  <input
                    value={
                      form.telefono
                    }
                    onChange={
                      (event) =>
                        setForm({
                          ...form,

                          telefono:
                            event.target.value,
                        })
                    }
                  />

                </div>


                {
                  form.tipo === "RESIDENTE"
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
                            setForm({
                              ...form,

                              es_responsable_notificacion:
                                event.target.checked,
                            })
                        }
                      />

                      <div>

                        <strong>
                          Responsable de notificaciones
                        </strong>

                      </div>

                    </label>

                  )
                }

              </div>


              <div className="modal-footer">

                <button
                  type="button"
                  className="secondary-button"
                  onClick={
                    () =>
                      setShowCreateModal(
                        false
                      )
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
                      ? "Guardando..."
                      : "Crear persona"
                  }

                </button>

              </div>

            </form>

          </div>

        </div>

      )}


      {
        personDetail
        && (

          <div className="modal-backdrop">

            <div className="modal person-detail-modal">

              <div className="modal-header">

                <div>

                  <h3>

                    {
                      editMode
                        ? "Editar persona"
                        : "Detalle de persona"
                    }

                  </h3>

                  <p>
                    {
                      personDetail
                        .persona
                        .nombre_completo
                    }
                  </p>

                </div>


                <button
                  type="button"
                  className="modal-close"
                  onClick={
                    () =>
                      setPersonDetail(
                        null
                      )
                  }
                >
                  ×
                </button>

              </div>


              {
                editMode
                  ? (

                    <form
                      onSubmit={
                        savePersonEdit
                      }
                    >

                      <div className="modal-body">

                        <div className="form-group">

                          <label>
                            Nombre completo
                          </label>

                          <input
                            required
                            value={
                              editForm
                                .nombre_completo
                            }
                            onChange={
                              (event) =>
                                setEditForm({
                                  ...editForm,

                                  nombre_completo:
                                    event.target.value,
                                })
                            }
                          />

                        </div>


                        <div className="form-row">

                          <div className="form-group">

                            <label>
                              Tipo
                            </label>

                            <select
                              value={
                                editForm.tipo
                              }
                              onChange={
                                (event) =>
                                  handleEditTypeChange(
                                    event.target.value
                                  )
                              }
                            >

                              <option value="RESIDENTE">
                                Residente
                              </option>

                              <option value="TRABAJADOR">
                                Trabajador
                              </option>

                              <option value="SEGURIDAD">
                                Seguridad
                              </option>

                            </select>

                          </div>


                          {
                            editForm.tipo
                            !== "SEGURIDAD"
                            && (

                              <div className="form-group">

                                <label>
                                  Vivienda
                                </label>

                                <select
                                  value={
                                    editForm
                                      .vivienda_id
                                  }
                                  onChange={
                                    (event) =>
                                      setEditForm({
                                        ...editForm,

                                        vivienda_id:
                                          event.target.value,
                                      })
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

                                          {house.codigo}

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
                            Correo
                          </label>

                          <input
                            type="email"
                            value={
                              editForm.email
                            }
                            onChange={
                              (event) =>
                                setEditForm({
                                  ...editForm,

                                  email:
                                    event.target.value,
                                })
                            }
                          />

                        </div>


                        <div className="form-group">

                          <label>
                            Teléfono
                          </label>

                          <input
                            value={
                              editForm.telefono
                            }
                            onChange={
                              (event) =>
                                setEditForm({
                                  ...editForm,

                                  telefono:
                                    event.target.value,
                                })
                            }
                          />

                        </div>


                        {
                          editForm.tipo
                          === "RESIDENTE"
                          && (

                            <label className="checkbox-row">

                              <input
                                type="checkbox"
                                checked={
                                  editForm
                                    .es_responsable_notificacion
                                }
                                onChange={
                                  (event) =>
                                    setEditForm({
                                      ...editForm,

                                      es_responsable_notificacion:
                                        event.target.checked,
                                    })
                                }
                              />

                              <strong>
                                Responsable de notificaciones
                              </strong>

                            </label>

                          )
                        }

                      </div>


                      <div className="modal-footer">

                        <button
                          type="button"
                          className="secondary-button"
                          onClick={
                            () =>
                              setEditMode(
                                false
                              )
                          }
                        >
                          Cancelar
                        </button>


                        <button
                          type="submit"
                          className="primary-button"
                          disabled={
                            savingEdit
                          }
                        >

                          {
                            savingEdit
                              ? "Guardando..."
                              : "Guardar cambios"
                          }

                        </button>

                      </div>

                    </form>

                  )
                  : (

                    <>

                      <div className="modal-body">

                        <div className="detail-grid">

                          <div className="detail-item">

                            <span>
                              Código biométrico
                            </span>

                            <strong>

                              {
                                personDetail
                                  .persona
                                  .codigo_biometrico
                                ?? "Pendiente"
                              }

                            </strong>

                          </div>


                          <div className="detail-item">

                            <span>
                              Tipo
                            </span>

                            <strong>
                              {
                                personDetail
                                  .persona.tipo
                              }
                            </strong>

                          </div>


                          <div className="detail-item">

                            <span>
                              Correo
                            </span>

                            <strong>
                              {
                                personDetail
                                  .persona.email
                                ?? "Sin correo"
                              }
                            </strong>

                          </div>


                          <div className="detail-item">

                            <span>
                              Teléfono
                            </span>

                            <strong>
                              {
                                personDetail
                                  .persona.telefono
                                ?? "Sin teléfono"
                              }
                            </strong>

                          </div>


                          <div className="detail-item">

                            <span>
                              Vivienda
                            </span>

                            <strong>
                              {
                                personDetail
                                  .vivienda?.codigo
                                ?? "Sin vivienda"
                              }
                            </strong>

                          </div>


                          <div className="detail-item">

                            <span>
                              Estado
                            </span>

                            <strong>

                              {
                                personDetail
                                  .persona.activo
                                  ? "ACTIVO"
                                  : "INACTIVO"
                              }

                            </strong>

                          </div>


                          <div className="detail-item">

                            <span>
                              Registrado
                            </span>

                            <strong>

                              {
                                formatDate(
                                  personDetail
                                    .persona
                                    .creado_en
                                )
                              }

                            </strong>

                          </div>


                          <div className="detail-item">

                            <span>
                              Biometría
                            </span>

                            <strong>

                              {
                                personDetail.biometria
                                  ? `${personDetail.biometria.modelo} / ${personDetail.biometria.cantidad_muestras} muestras`
                                  : "Pendiente"
                              }

                            </strong>

                          </div>

                        </div>

                      </div>


                      <div className="modal-footer person-detail-footer">

                        <button
                          type="button"
                          className={
                            personDetail
                              .persona.activo
                              ? "danger-button"
                              : "activate-button"
                          }
                          onClick={
                            togglePersonStatus
                          }
                          disabled={
                            changingStatus
                          }
                        >

                          {
                            changingStatus
                              ? "Procesando..."
                              : personDetail
                                  .persona.activo
                                ? "Inactivar"
                                : "Activar"
                          }

                        </button>


                        <div className="detail-footer-right">

                          <button
                            type="button"
                            className="secondary-button"
                            onClick={
                              () =>
                                setPersonDetail(
                                  null
                                )
                            }
                          >
                            Cerrar
                          </button>


                          <button
                            type="button"
                            className="primary-button"
                            onClick={
                              () =>
                                setEditMode(
                                  true
                                )
                            }
                          >
                            Editar persona
                          </button>

                        </div>

                      </div>

                    </>

                  )
              }

            </div>

          </div>

        )
      }


      {detailLoading && (

        <div className="floating-loading">
          Cargando detalle...
        </div>

      )}


      {
        enrollmentPerson
        && (

          <EnrollmentModal
            person={
              enrollmentPerson
            }
            onClose={
              () =>
                setEnrollmentPerson(
                  null
                )
            }
            onCompleted={
              handleEnrollmentCompleted
            }
          />

        )
      }

    </>
  );

}


export default PersonasPage;