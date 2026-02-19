import { useState } from "react"
import api, { setAuthToken } from "@/api/client"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"

export default function Login({ onLogin }) {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)

  const handleLogin = async () => {
    try {
      setLoading(true)

      const res = await api.post("/auth/login", {
        email: email,
        password: password,
      })

      const token = res.data.access_token

      // Set token in axios default headers
      setAuthToken(token)

      // Inform parent component
      onLogin(token)

    } catch (err) {
      console.error("Login error:", err.response?.data || err.message)
      alert("Invalid email or password")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted">
      <Card className="w-[350px]">
        <CardContent className="pt-6 space-y-4">
          <h2 className="text-xl font-semibold text-center">Login</h2>

          <Input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <Input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <Button 
            className="w-full"
            onClick={handleLogin}
            disabled={loading}
          >
            {loading ? "Logging in..." : "Login"}
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
