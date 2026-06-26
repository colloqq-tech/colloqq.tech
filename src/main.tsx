import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import Landing from "./pages/Landing.tsx";
import "./styles/index.css";

const root = document.getElementById("root");
if (!root) throw new Error("Root element #root not found");

createRoot(root).render(
    <StrictMode>
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Landing />} />
            </Routes>
        </BrowserRouter>
    </StrictMode>,
);
