import { Routes, Route, BrowserRouter } from "react-router-dom";
import { Sidebar } from "@/components/Sidebar";
import Overview from "@/pages/Overview";
import Health from "@/pages/Health";

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-full">
        <Sidebar />
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/health" element={<Health />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
