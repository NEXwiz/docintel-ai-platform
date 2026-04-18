import { useState, useEffect } from "react"
import { useSearchParams } from "react-router-dom"
import api from "@/api/client"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Send, Bot, User, BookOpen, Sparkles } from "lucide-react"

export default function QA() {
  const [searchParams] = useSearchParams()
  const [query, setQuery] = useState("")
  const [documentId, setDocumentId] = useState("")
  const [conversation, setConversation] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const doc = searchParams.get("doc")
    if (doc) setDocumentId(doc)
  }, [searchParams])

  const handleAsk = async (e) => {
    e?.preventDefault()
    if (!query.trim() || !documentId) return

    const userMessage = query.trim()
    setQuery("")
    setConversation((prev) => [...prev, { role: "user", content: userMessage }])

    try {
      setLoading(true)
      const res = await api.post(
        `/qa/?query=${encodeURIComponent(userMessage)}&document_id=${documentId}`
      )

      setConversation((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.data.answer,
          sources: res.data.sources,
        },
      ])
    } catch (err) {
      console.error(err.response?.data || err.message)
      setConversation((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Sorry, I encountered an error processing your question. Please try again.",
          isError: true,
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="h-[calc(100vh-6rem)] flex flex-col animate-slide-up">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Ask AI</h2>
          <p className="text-muted-foreground mt-1">
            Ask questions about your documents
          </p>
        </div>

        <div className="flex items-center gap-2">
          <label className="text-sm text-muted-foreground">Doc ID:</label>
          <Input
            id="qa-doc-id"
            value={documentId}
            onChange={(e) => setDocumentId(e.target.value)}
            placeholder="e.g. 1"
            className="w-24 h-9 bg-secondary/50 border-border/50 text-center"
          />
        </div>
      </div>

      {/* Chat area */}
      <Card className="flex-1 flex flex-col border-border/50 bg-card/30 overflow-hidden">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {conversation.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center">
              <div className="w-16 h-16 rounded-2xl gradient-bg-subtle flex items-center justify-center mb-4">
                <Sparkles className="w-8 h-8 text-primary" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Ready to answer</h3>
              <p className="text-sm text-muted-foreground max-w-sm">
                {documentId
                  ? `Document #${documentId} selected. Ask any question about it.`
                  : "Enter a Document ID and start asking questions about your uploaded documents."}
              </p>
            </div>
          ) : (
            conversation.map((msg, i) => (
              <div
                key={i}
                className={`flex gap-3 animate-fade-in ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                {msg.role === "assistant" && (
                  <div className="w-8 h-8 rounded-lg gradient-bg flex items-center justify-center flex-shrink-0 shadow-md shadow-purple-500/20">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                )}

                <div
                  className={`max-w-[75%] space-y-3 ${
                    msg.role === "user" ? "order-first" : ""
                  }`}
                >
                  <div
                    className={`p-4 rounded-2xl text-sm leading-relaxed ${
                      msg.role === "user"
                        ? "gradient-bg text-white rounded-br-md shadow-lg shadow-purple-500/20"
                        : msg.isError
                        ? "bg-red-500/10 border border-red-500/20 text-red-400 rounded-bl-md"
                        : "bg-card border border-border/50 rounded-bl-md"
                    }`}
                  >
                    {msg.content}
                  </div>

                  {/* Sources */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="space-y-1.5">
                      <p className="text-[10px] uppercase tracking-wider text-muted-foreground font-medium flex items-center gap-1">
                        <BookOpen className="w-3 h-3" />
                        Sources
                      </p>
                      {msg.sources.map((src, j) => (
                        <div
                          key={j}
                          className="text-xs p-3 rounded-xl bg-accent/30 border border-border/30 text-muted-foreground leading-relaxed"
                        >
                          {src}
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {msg.role === "user" && (
                  <div className="w-8 h-8 rounded-lg bg-secondary flex items-center justify-center flex-shrink-0">
                    <User className="w-4 h-4 text-muted-foreground" />
                  </div>
                )}
              </div>
            ))
          )}

          {/* Loading indicator */}
          {loading && (
            <div className="flex gap-3 animate-fade-in">
              <div className="w-8 h-8 rounded-lg gradient-bg flex items-center justify-center flex-shrink-0 shadow-md shadow-purple-500/20">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className="p-4 rounded-2xl rounded-bl-md bg-card border border-border/50">
                <div className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "0ms" }} />
                  <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "150ms" }} />
                  <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input bar */}
        <div className="p-4 border-t border-border/50 bg-card/50 backdrop-blur-sm">
          <form onSubmit={handleAsk} className="flex gap-3">
            <Input
              id="qa-input"
              placeholder={documentId ? "Ask a question about your document..." : "Enter a Document ID first..."}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={!documentId || loading}
              className="flex-1 h-11 bg-secondary/50 border-border/50 focus:border-primary/50"
            />
            <Button
              type="submit"
              disabled={!query.trim() || !documentId || loading}
              className="h-11 px-5 gradient-bg border-0 text-white shadow-lg shadow-purple-500/25 hover:opacity-90 transition-opacity disabled:opacity-40"
            >
              <Send className="w-4 h-4" />
            </Button>
          </form>
        </div>
      </Card>
    </div>
  )
}
