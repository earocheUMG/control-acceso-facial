import {
  useState,
} from "react";

import type {
  FormEvent,
} from "react";

import {
  Navigate,
  useNavigate,
} from "react-router-dom";

import {
  useAuth
} from "../context/AuthContext";

import Icon from "../components/Icon";


function LoginPage() {

  const navigate =
    useNavigate();


  const {
    user,
    login,
    loading,
  } = useAuth();


  const [
    usuario,
    setUsuario
  ] = useState("");


  const [
    password,
    setPassword
  ] = useState("");


  const [
    submitting,
    setSubmitting
  ] = useState(false);


  const [
    error,
    setError
  ] = useState<string | null>(
    null
  );


  // ==========================================
  // LOGIN
  // ==========================================

  const handleSubmit =
    async (
      event: FormEvent
    ) => {

      event.preventDefault();


      try {

        setSubmitting(
          true
        );


        setError(
          null
        );


        await login(
          usuario.trim(),
          password
        );


        navigate(
          "/",
          {
            replace: true
          }
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

        setSubmitting(
          false
        );

      }

    };


  // ==========================================
  // SESION EXISTENTE
  // ==========================================

  if (
    !loading
    &&
    user
  ) {

    return (
      <Navigate
        to="/"
        replace
      />
    );

  }


  // ==========================================
  // RENDER
  // ==========================================

  return (

    <div className="login-page">

      <section className="login-visual" aria-hidden="true">
        <div className="login-visual-content">
          <div className="login-security-mark">CF</div>
          <span className="login-eyebrow">Control de Acceso</span>
          <h2>Control de Acceso Facial<br />Mediante IA</h2>
          <p>
            Administración centralizada de identidades,
            viviendas y eventos de acceso.
          </p>
          <div className="login-assurance">
            <span>●</span>
            Plataforma de seguridad operativa
          </div>
        </div>
      </section>

      <div className="login-card">

        <div className="login-brand">

          <div className="login-logo">
            <Icon name="shield" size={24} />
          </div>


          <h1>
            Control Facial
          </h1>


          <p>
            Sistema de Control
            de Acceso
          </p>

        </div>


        <form
          onSubmit={
            handleSubmit
          }
        >

          <div className="form-group">

            <label>
              Usuario
            </label>

            <input
              type="text"
              required
              minLength={3}
              maxLength={50}
              autoComplete="username"
              value={
                usuario
              }
              onChange={
                (event) =>
                  setUsuario(
                    event.target.value
                  )
              }
              placeholder="Ingrese su usuario"
            />

          </div>


          <div className="form-group">

            <label>
              Contraseña
            </label>

            <input
              type="password"
              required
              minLength={8}
              autoComplete="current-password"
              value={
                password
              }
              onChange={
                (event) =>
                  setPassword(
                    event.target.value
                  )
              }
              placeholder="Ingrese su contraseña"
            />

          </div>


          {error && (

            <div className="login-error">

              {error}

            </div>

          )}


          <button
            type="submit"
            className="login-button"
            disabled={
              submitting
              ||
              loading
            }
          >

            {
              submitting
                ? "Ingresando..."
                : "Iniciar sesión"
            }

          </button>

        </form>


        <div className="login-footer">

          Sistema de Control
          de Acceso Facial

        </div>

      </div>

    </div>

  );

}


export default LoginPage;
