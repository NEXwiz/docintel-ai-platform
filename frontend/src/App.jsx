import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { useState } from "react"

import Layout from "@/components/layout/Layout"
import Login from "@/pages/Login"
import Dashboard from "@/pages/Dashboard"
import Upload from "@/pages/Upload"
import QA from "@/pages/QA"

export default function App() {
  const [token, setToken] = useState(null)

  if (!token) {
    return <Login onLogin={setToken} />
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Navigate to="/dashboard" />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/ask" element={<QA />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}