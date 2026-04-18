import { Outlet } from "react-router-dom"
import Sidebar from "./Sidebar"

export default function Layout({ onLogout }) {
  return (
    <div className="flex min-h-screen dark bg-background text-foreground">
      <Sidebar onLogout={onLogout} />
      <main className="flex-1 p-8 overflow-y-auto">
        <div className="max-w-5xl mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  )
}