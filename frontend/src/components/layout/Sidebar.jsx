import { NavLink } from "react-router-dom"
import { Button } from "@/components/ui/button"

export default function Sidebar() {
  return (
    <div className="w-60 border-r bg-background p-6 space-y-6">
      <h1 className="text-xl font-bold">DocIntel AI</h1>

      <nav className="flex flex-col space-y-2">
        <NavLink to="/dashboard">
          <Button variant="ghost" className="w-full justify-start">
            Dashboard
          </Button>
        </NavLink>

        <NavLink to="/upload">
          <Button variant="ghost" className="w-full justify-start">
            Upload
          </Button>
        </NavLink>

        <NavLink to="/ask">
          <Button variant="ghost" className="w-full justify-start">
            Ask
          </Button>
        </NavLink>
      </nav>
    </div>
  )
}