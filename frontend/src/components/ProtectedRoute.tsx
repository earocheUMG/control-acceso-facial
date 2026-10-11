import {
  Navigate
} from "react-router-dom";

import type {
  ReactNode
} from "react";

import {
  useAuth
} from "../context/AuthContext";


interface ProtectedRouteProps {
  children: ReactNode;
}


function ProtectedRoute({
  children,
}: ProtectedRouteProps) {

  const {
    user,
    loading,
  } = useAuth();


  if (loading) {

    return (
      <div className="auth-loading">
        Cargando sesión...
      </div>
    );

  }


  if (!user) {

    return (
      <Navigate
        to="/login"
        replace
      />
    );

  }


  return (
    <>
      {children}
    </>
  );

}


export default ProtectedRoute;