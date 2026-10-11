import {
  useEffect,
  useState,
} from "react";

import type {
  FormEvent,
} from "react";

import {
  useAuth
} from "../context/AuthContext";

import {
  apiFetch
} from "../services/api";


interface SystemUser {
  id: number;
  usuario: string;
  rol: "ADMIN" | "SEGURIDAD";
  activo: boolean;
}


interface UsersResponse {
  total: number;
  usuarios: SystemUser[];
}


type Role =
  | "ADMIN"
  | "SEGURIDAD";


const API_URL =
  "http://127.0.0.1:8000/api/usuarios";


async function fetchSystemUsers():
Promise<UsersResponse> {

  const response =
    await apiFetch(
      API_URL
    );


  const result =
    await response.json();


  if (!response.ok) {

    throw new Error(
      typeof result.detail === "string"
        ? result.detail
        : "No fue posible consultar los usuarios."
    );

  }


  return result;
}


function UsuariosPage() {

  const {
    user: currentUser,
  } = useAuth();


  const [
    users,
    setUsers
  ] = useState<SystemUser[]>([]);


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
    username,
    setUsername
  ] = useState("");


  const [
    password,
    setPassword
  ] = useState("");


  const [
    passwordConfirmation,
    setPasswordConfirmation
  ] = useState("");


  const [
    role,
    setRole
  ] = useState<Role>(
    "SEGURIDAD"
  );


  const [
    saving,
    setSaving
  ] = useState(false);


  const [
    changingUserId,
    setChangingUserId
  ] = useState<number | null>(
    null
  );


  useEffect(() => {

    let active = true;


    fetchSystemUsers()
      .then(
        (data) => {

          if (!active) {
            return;
          }


          setUsers(
            data.usuarios
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


  const loadUsers =
    async () => {

      try {

        const data =
          await fetchSystemUsers();


        setUsers(
          data.usuarios
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


  const openCreateModal =
    () => {

      setUsername("");
      setPassword("");
      setPasswordConfirmation("");
      setRole("SEGURIDAD");
      setError(null);
      setSuccess(null);

      setShowCreateModal(
        true
      );

    };


  const closeCreateModal =
    () => {

      if (!saving) {

        setShowCreateModal(
          false
        );

      }

    };


  const handleCreate =
    async (
      event: FormEvent
    ) => {

      event.preventDefault();


      if (
        password
        !== passwordConfirmation
      ) {

        setError(
          "Las contraseñas no coinciden."
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
            API_URL,
            {
              method: "POST",

              headers: {
                "Content-Type":
                  "application/json",
              },

              body:
                JSON.stringify({
                  usuario:
                    username.trim(),

                  password,

                  rol:
                    role,
                }),
            }
          );


        const result =
          await response.json();


        if (!response.ok) {

          throw new Error(
            typeof result.detail === "string"
              ? result.detail
              : "No fue posible crear el usuario."
          );

        }


        setShowCreateModal(
          false
        );


        setSuccess(
          "Usuario creado correctamente."
        );


        await loadUsers();


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


  const toggleUserStatus =
    async (
      systemUser: SystemUser
    ) => {

      const newStatus =
        !systemUser.activo;


      const confirmed =
        window.confirm(
          `¿Está seguro de ${
            newStatus
              ? "activar"
              : "inactivar"
          } al usuario ${
            systemUser.usuario
          }?`
        );


      if (!confirmed) {
        return;
      }


      try {

        setChangingUserId(
          systemUser.id
        );


        setError(
          null
        );


        const response =
          await apiFetch(
            `${API_URL}/${systemUser.id}/estado`,
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


        setSuccess(
          result.message
        );


        await loadUsers();


      } catch (err) {

        if (
          err instanceof Error
        ) {

          setError(
            err.message
          );

        }


      } finally {

        setChangingUserId(
          null
        );

      }

    };


  return (
    <>

      <header className="topbar">

        <div>

          <h2>
            Usuarios
          </h2>

          <p>
            Usuarios administrativos
            del sistema
          </p>

        </div>


        <div className="header-actions">

          <button
            type="button"
            className="refresh-button"
            onClick={
              loadUsers
            }
          >
            Actualizar
          </button>


          <button
            type="button"
            className="primary-button"
            onClick={
              openCreateModal
            }
          >
            + Nuevo usuario
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
          Cargando usuarios...
        </div>
      )}


      {!loading && (

        <section className="panel">

          <div className="panel-header">

            <div>

              <h3>
                Usuarios del sistema
              </h3>

              <p>
                Total: {users.length}
              </p>

            </div>

          </div>


          <div className="table-container">

            <table>

              <thead>

                <tr>
                  <th>ID</th>
                  <th>Usuario</th>
                  <th>Rol</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>

              </thead>


              <tbody>

                {
                  users.map(
                    (systemUser) => (

                      <tr
                        key={
                          systemUser.id
                        }
                      >

                        <td>
                          #{systemUser.id}
                        </td>


                        <td>

                          <div className="person-cell">

                            <div className="person-avatar">

                              {
                                systemUser
                                  .usuario
                                  .charAt(0)
                                  .toUpperCase()
                              }

                            </div>


                            <div>

                              <strong>
                                {systemUser.usuario}
                              </strong>


                              {
                                currentUser?.id
                                === systemUser.id
                                && (

                                  <div className="secondary-text">
                                    Sesión actual
                                  </div>

                                )
                              }

                            </div>

                          </div>

                        </td>


                        <td>

                          <span
                            className={
                              systemUser.rol
                              === "ADMIN"
                                ? "badge badge-info"
                                : "badge badge-warning"
                            }
                          >
                            {systemUser.rol}
                          </span>

                        </td>


                        <td>

                          <span
                            className={
                              systemUser.activo
                                ? "badge badge-success"
                                : "badge badge-danger"
                            }
                          >

                            {
                              systemUser.activo
                                ? "ACTIVO"
                                : "INACTIVO"
                            }

                          </span>

                        </td>


                        <td>

                          <button
                            type="button"
                            className={
                              systemUser.activo
                                ? "danger-button compact-button"
                                : "activate-button compact-button"
                            }
                            disabled={
                              changingUserId
                              === systemUser.id
                              ||
                              (
                                currentUser?.id
                                === systemUser.id
                                &&
                                systemUser.activo
                              )
                            }
                            onClick={
                              () =>
                                toggleUserStatus(
                                  systemUser
                                )
                            }
                          >

                            {
                              changingUserId
                              === systemUser.id
                                ? "Procesando..."
                                : systemUser.activo
                                  ? "Inactivar"
                                  : "Activar"
                            }

                          </button>

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
                  Nuevo usuario
                </h3>

                <p>
                  Crear una cuenta
                  para acceder al sistema
                </p>

              </div>


              <button
                type="button"
                className="modal-close"
                onClick={
                  closeCreateModal
                }
              >
                ×
              </button>

            </div>


            <form
              onSubmit={
                handleCreate
              }
            >

              <div className="modal-body">

                <div className="form-group">

                  <label>
                    Usuario *
                  </label>

                  <input
                    required
                    minLength={3}
                    maxLength={50}
                    value={
                      username
                    }
                    onChange={
                      (event) =>
                        setUsername(
                          event.target.value
                        )
                    }
                  />

                </div>


                <div className="form-group">

                  <label>
                    Rol *
                  </label>

                  <select
                    value={
                      role
                    }
                    onChange={
                      (event) => {

                        const value =
                          event.target.value;


                        if (
                          value === "ADMIN"
                          ||
                          value === "SEGURIDAD"
                        ) {

                          setRole(
                            value
                          );

                        }

                      }
                    }
                  >

                    <option value="SEGURIDAD">
                      Seguridad
                    </option>

                    <option value="ADMIN">
                      Administrador
                    </option>

                  </select>

                </div>


                <div className="form-group">

                  <label>
                    Contraseña *
                  </label>

                  <input
                    type="password"
                    required
                    minLength={8}
                    value={
                      password
                    }
                    onChange={
                      (event) =>
                        setPassword(
                          event.target.value
                        )
                    }
                  />

                </div>


                <div className="form-group">

                  <label>
                    Confirmar contraseña *
                  </label>

                  <input
                    type="password"
                    required
                    minLength={8}
                    value={
                      passwordConfirmation
                    }
                    onChange={
                      (event) =>
                        setPasswordConfirmation(
                          event.target.value
                        )
                    }
                  />

                </div>

              </div>


              <div className="modal-footer">

                <button
                  type="button"
                  className="secondary-button"
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
                    saving
                  }
                >

                  {
                    saving
                      ? "Creando..."
                      : "Crear usuario"
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


export default UsuariosPage;