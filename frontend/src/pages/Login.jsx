import { useState } from "react"
import api, { setAuthToken } from "@/api/client"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { FileText, Brain, Search, Shield, ArrowRight, Sparkles, Zap, Lock } from "lucide-react"

const FEATURES = [
  {
    icon: FileText,
    title: "Smart Upload",
    desc: "Upload PDFs, DOCX, and TXT files. We extract and chunk the text automatically.",
  },
  {
    icon: Brain,
    title: "AI-Powered Q&A",
    desc: "Ask natural-language questions and get precise answers backed by your documents.",
  },
  {
    icon: Search,
    title: "Semantic Search",
    desc: "Find relevant passages across all your documents using vector similarity search.",
  },
  {
    icon: Shield,
    title: "Secure & Private",
    desc: "Your documents are scoped to your account. No one else can access them.",
  },
]

export default function Login({ onLogin }) {
  const [isSignUp, setIsSignUp] = useState(false)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  const resetForm = () => {
    setEmail("")
    setPassword("")
    setConfirmPassword("")
    setError("")
    setSuccess("")
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError("")
    setSuccess("")

    if (!email || !password) {
      setError("Please fill in all fields")
      return
    }

    if (isSignUp && password !== confirmPassword) {
      setError("Passwords do not match")
      return
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters")
      return
    }

    try {
      setLoading(true)

      if (isSignUp) {
        await api.post("/auth/register", { email, password })
        setSuccess("Account created! You can now log in.")
        setIsSignUp(false)
        setPassword("")
        setConfirmPassword("")
      } else {
        const res = await api.post("/auth/login", { email, password })
        const token = res.data.access_token
        setAuthToken(token)
        onLogin(token)
      }
    } catch (err) {
      const data = err.response?.data
      let msg = ""
      if (typeof data?.detail === "string") {
        msg = data.detail
      } else if (Array.isArray(data?.detail)) {
        msg = data.detail.map((e) => e.msg || e.message || JSON.stringify(e)).join("; ")
      } else if (err.response?.status) {
        msg = `Server error (${err.response.status}). Please try again.`
      } else {
        msg = "Network error. Check your connection."
      }
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col lg:flex-row dark bg-background text-foreground">
      {/* Left — Hero / Info Panel */}
      <div className="relative flex-1 flex flex-col justify-center px-8 py-12 lg:px-16 overflow-hidden">
        {/* Animated background orbs */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -left-40 w-96 h-96 rounded-full gradient-bg opacity-20 blur-3xl animate-float" />
          <div className="absolute -bottom-40 -right-40 w-[500px] h-[500px] rounded-full bg-purple-500/10 blur-3xl animate-float-delayed" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-72 h-72 rounded-full bg-violet-400/5 blur-2xl animate-glow" />
        </div>

        <div className="relative z-10 max-w-xl mx-auto lg:mx-0">
          {/* Logo */}
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-xl gradient-bg flex items-center justify-center shadow-lg shadow-purple-500/25">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight">DocIntel AI</span>
          </div>

          {/* Headline */}
          <h1 className="text-4xl lg:text-5xl font-extrabold leading-tight mb-4 tracking-tight">
            Your documents,{" "}
            <span className="gradient-text">supercharged</span>{" "}
            with AI
          </h1>

          <p className="text-lg text-muted-foreground mb-10 leading-relaxed max-w-md">
            Upload any document and instantly ask questions, search for information, and get AI-powered answers — all in one place.
          </p>

          {/* Feature grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {FEATURES.map((f) => (
              <div
                key={f.title}
                className="group p-4 rounded-xl border border-border/50 bg-card/30 backdrop-blur-sm hover:border-primary/30 hover:bg-accent/30 transition-all duration-300"
              >
                <div className="w-9 h-9 rounded-lg gradient-bg-subtle flex items-center justify-center mb-3 group-hover:scale-110 transition-transform duration-300">
                  <f.icon className="w-4 h-4 text-primary" />
                </div>
                <h3 className="font-semibold text-sm mb-1">{f.title}</h3>
                <p className="text-xs text-muted-foreground leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>

          {/* Bottom tagline */}
          <div className="mt-10 flex items-center gap-2 text-xs text-muted-foreground">
            <Zap className="w-3.5 h-3.5 text-primary" />
            <span>Powered by Gemini AI & Qdrant Vector Search</span>
          </div>
        </div>
      </div>

      {/* Right — Auth Form */}
      <div className="flex-1 flex items-center justify-center px-8 py-12 lg:px-16">
        <div className="w-full max-w-md animate-slide-up">
          <Card className="glass-card border-0 shadow-2xl shadow-black/20">
            <CardContent className="p-8 space-y-6">
              {/* Form Header */}
              <div className="text-center space-y-2">
                <h2 className="text-2xl font-bold tracking-tight">
                  {isSignUp ? "Create your account" : "Welcome back"}
                </h2>
                <p className="text-sm text-muted-foreground">
                  {isSignUp
                    ? "Start analyzing your documents with AI"
                    : "Sign in to continue to DocIntel AI"}
                </p>
              </div>

              {/* Error / Success messages */}
              {error && (
                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm animate-fade-in">
                  {error}
                </div>
              )}
              {success && (
                <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm animate-fade-in">
                  {success}
                </div>
              )}

              {/* Form */}
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-muted-foreground">Email</label>
                  <Input
                    id="auth-email"
                    type="email"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="h-11 bg-secondary/50 border-border/50 focus:border-primary/50 transition-colors"
                  />
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-muted-foreground">Password</label>
                  <Input
                    id="auth-password"
                    type="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="h-11 bg-secondary/50 border-border/50 focus:border-primary/50 transition-colors"
                  />
                </div>

                {isSignUp && (
                  <div className="space-y-2 animate-fade-in">
                    <label className="text-sm font-medium text-muted-foreground">Confirm Password</label>
                    <Input
                      id="auth-confirm-password"
                      type="password"
                      placeholder="••••••••"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className="h-11 bg-secondary/50 border-border/50 focus:border-primary/50 transition-colors"
                    />
                  </div>
                )}

                <Button
                  type="submit"
                  className="w-full h-11 gradient-bg border-0 text-white font-semibold hover:opacity-90 transition-opacity shadow-lg shadow-purple-500/25"
                  disabled={loading}
                >
                  {loading ? (
                    <span className="flex items-center gap-2">
                      <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      {isSignUp ? "Creating account..." : "Signing in..."}
                    </span>
                  ) : (
                    <span className="flex items-center gap-2">
                      {isSignUp ? "Create Account" : "Sign In"}
                      <ArrowRight className="w-4 h-4" />
                    </span>
                  )}
                </Button>
              </form>

              {/* Toggle Login / Sign Up */}
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-border/50" />
                </div>
                <div className="relative flex justify-center text-xs">
                  <span className="bg-card px-3 text-muted-foreground">or</span>
                </div>
              </div>

              <Button
                type="button"
                variant="ghost"
                className="w-full text-sm text-muted-foreground hover:text-foreground"
                onClick={() => {
                  setIsSignUp(!isSignUp)
                  resetForm()
                }}
              >
                {isSignUp
                  ? "Already have an account? Sign in"
                  : "Don't have an account? Sign up"}
              </Button>

              {/* Security note */}
              <div className="flex items-center justify-center gap-1.5 text-[11px] text-muted-foreground/60">
                <Lock className="w-3 h-3" />
                <span>Secured with JWT authentication</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
