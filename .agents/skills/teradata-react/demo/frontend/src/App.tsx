import { Routes, Route, BrowserRouter } from "react-router-dom";
import { Sidebar } from "@/components/Sidebar";
import Overview from "@/pages/Overview";
import Databases from "@/pages/Databases";
import Tables from "@/pages/Tables";
import Users from "@/pages/Users";
import Space from "@/pages/Space";
import Health from "@/pages/Health";

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-full">
        <Sidebar />
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/databases" element={<Databases />} />
          <Route path="/tables" element={<Tables />} />
          <Route path="/users" element={<Users />} />
          <Route path="/space" element={<Space />} />
          <Route path="/health" element={<Health />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
