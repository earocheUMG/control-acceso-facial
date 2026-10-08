import {
  Route,
  Routes
} from "react-router-dom";

import Layout from "./components/Layout";

import DashboardPage from "./pages/DashboardPage";
import PersonasPage from "./pages/PersonasPage";

import "./App.css";


function App() {
  return (
    <Routes>

      <Route
        element={
          <Layout />
        }
      >

        <Route
          path="/"
          element={
            <DashboardPage />
          }
        />

        <Route
          path="/personas"
          element={
            <PersonasPage />
          }
        />

      </Route>

    </Routes>
  );
}


export default App;