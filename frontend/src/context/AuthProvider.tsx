import {
  useEffect,
  useState,
} from "react";

import type {
  ReactNode,
} from "react";

import {
  AuthContext,
} from "./AuthContext";

import type {
  AuthUser,
} from "./AuthContext";


interface LoginResponse {
  access_token: string;
  token_type: string;
  usuario: string;
  rol: "ADMIN" | "SEGURIDAD";
}


interface AuthProviderProps {
  children: ReactNode;
}


function AuthProvider({
  children,
}: AuthProviderProps) {

  const [
    user,
    setUser
  ] = useState<AuthUser | null>(
    null
  );


  const [
    token,
    setToken
  ] = useState<string | null>(
    () =>
      localStorage.getItem(
        "access_token"
      )
  );


  const [
    loading,
    setLoading
  ] = useState(true);


  // ==========================================
  // CERRAR SESION
  // ==========================================

  const logout = () => {

    localStorage.removeItem(
      "access_token"
    );


    setToken(
      null
    );


    setUser(
      null
    );

  };


  // ==========================================
  // OBTENER USUARIO ACTUAL
  // ==========================================

  const loadCurrentUser =
    async (
      currentToken: string
    ) => {

      const response =
        await fetch(
          "http://127.0.0.1:8000/api/auth/me",
          {
            headers: {
              Authorization:
                `Bearer ${currentToken}`,
            },
          }
        );


      if (!response.ok) {

        throw new Error(
          "La sesión no es válida."
        );

      }


      const data:
        AuthUser =
          await response.json();


      setUser(
        data
      );

  };


  // ==========================================
  // RESTAURAR SESION
  // ==========================================

  useEffect(() => {

    const restoreSession =
      async () => {

        const storedToken =
          localStorage.getItem(
            "access_token"
          );


        if (!storedToken) {

          setLoading(
            false
          );

          return;

        }


        try {

          await loadCurrentUser(
            storedToken
          );


          setToken(
            storedToken
          );


        } catch {

          localStorage.removeItem(
            "access_token"
          );


          setToken(
            null
          );


          setUser(
            null
          );


        } finally {

          setLoading(
            false
          );

        }

      };


    restoreSession();

  }, []);


  // ==========================================
  // LOGIN
  // ==========================================

  const login =
    async (
      usuario: string,
      password: string
    ) => {

      const response =
        await fetch(
          "http://127.0.0.1:8000/api/auth/login",
          {
            method: "POST",

            headers: {
              "Content-Type":
                "application/json",
            },

            body:
              JSON.stringify({
                usuario,
                password,
              }),
          }
        );


      const result =
        await response.json();


      if (!response.ok) {

        let message =
          "No fue posible iniciar sesión.";


        if (
          typeof result.detail
          === "string"
        ) {

          message =
            result.detail;

        }


        throw new Error(
          message
        );

      }


      const loginData:
        LoginResponse =
          result;


      localStorage.setItem(
        "access_token",
        loginData.access_token
      );


      setToken(
        loginData.access_token
      );


      await loadCurrentUser(
        loginData.access_token
      );

  };


  return (

    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        logout,
      }}
    >

      {children}

    </AuthContext.Provider>

  );

}


export default AuthProvider;