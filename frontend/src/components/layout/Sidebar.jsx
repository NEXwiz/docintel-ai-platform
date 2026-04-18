import { NavLink } from "react-router-dom"
import { LayoutDashboard, Upload, MessageSquare, Sparkles, LogOut } from "lucide-react"

const NAV_ITEMS = [
  { to: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/upload", icon: Upload, label: "Upload" },
  { to: "/ask", icon: MessageSquare, label: "Ask AI" },
]

export default function Sidebar({ onLogout }) {
  return (
    <div className="w-64 border-r border-border/50 bg-card/50 backdrop-blur-sm p-6 flex flex-col">
      {/* Brand */}
      <div className="flex items-center gap-3 mb-10">
        <div className="w-9 h-9 rounded-xl gradient-bg flex items-center justify-center shadow-lg shadow-purple-500/25">
          <Sparkles className="w-4 h-4 text-white" />
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-tight">DocIntel AI</h1>
          <p className="text-[10px] text-muted-foreground font-medium tracking-wider uppercase">Intelligence Platform</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex flex-col gap-1 flex-1">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                isActive
                  ? "gradient-bg text-white shadow-lg shadow-purple-500/25"
                  : "text-muted-foreground hover:text-foreground hover:bg-accent/50"
              }`
            }
          >
            <item.icon className="w-4 h-4" />
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Logout */}
      {onLogout && (
        <button
          onClick={onLogout}
          className="flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium text-muted-foreground hover:text-red-400 hover:bg-red-500/10 transition-all duration-200 mt-2"
        >
          <LogOut className="w-4 h-4" />
          Log out
        </button>
      )}

      {/* Footer */}
      <div className="mt-4 pt-4 border-t border-border/50">
        <p className="text-[10px] text-muted-foreground/50 text-center">
          v1.0 • Built with Gemini AI
        </p>
      </div>
    </div>
  )
}