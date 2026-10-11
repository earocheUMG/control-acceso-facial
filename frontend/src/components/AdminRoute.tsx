import {
  Navigate
} from "react-router-dom";

import type {
  ReactNode
} from "react";

import {
  useAuth
} from "../context/AuthContext";


interface AdminRouteProps {
  children: ReactNode;
}


function AdminRoute({
  children,
}: AdminRouteProps) {

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


  if (
    user.rol !== "ADMIN"
  ) {

    return (
      <Navigate
        to="/"
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


export default AdminRoute;