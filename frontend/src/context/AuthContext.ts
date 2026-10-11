import {
  createContext,
  useContext,
} from "react";


export interface AuthUser {
  id: number;
  usuario: string;
  rol: "ADMIN" | "SEGURIDAD";
  activo: boolean;
}


export interface AuthContextType {
  user: AuthUser | null;
  token: string | null;
  loading: boolean;

  login: (
    usuario: string,
    password: string
  ) => Promise<void>;

  logout: () => void;
}


export const AuthContext =
  createContext<AuthContextType | null>(
    null
  );


export function useAuth() {

  const context =
    useContext(
      AuthContext
    );


  if (!context) {

    throw new Error(
      "useAuth debe utilizarse "
      + "dentro de AuthProvider."
    );

  }


  return context;
}