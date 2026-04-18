import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import api from "@/api/client"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { FileText, MessageSquare, Trash2, Clock, FolderOpen, Sparkles } from "lucide-react"

export default function Dashboard() {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [deletingId, setDeletingId] = useState(null)
  const navigate = useNavigate()

  const fetchDocs = async () => {
    try {
      const res = await api.get("/documents/")
      setDocuments(res.data)
    } catch (err) {
      console.error(err.response?.data || err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDocs()
  }, [])

  const handleDelete = async (docId) => {
    if (!confirm("Delete this document? This will also remove it from the vector store.")) return
    try {
      setDeletingId(docId)
      await api.delete(`/documents/${docId}`)
      setDocuments((prev) => prev.filter((d) => d.id !== docId))
    } catch (err) {
      console.error(err.response?.data || err.message)
      alert("Failed to delete document")
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <div className="space-y-8 animate-slide-up">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
          <p className="text-muted-foreground mt-1">
            Manage your uploaded documents
          </p>
        </div>

        <Button
          onClick={() => navigate("/upload")}
          className="gradient-bg border-0 text-white shadow-lg shadow-purple-500/25 hover:opacity-90 transition-opacity"
        >
          <FileText className="w-4 h-4 mr-2" />
          Upload New
        </Button>
      </div>

      {/* Stats bar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="border-border/50 bg-card/50">
          <CardContent className="p-5 flex items-center gap-4">
            <div className="w-10 h-10 rounded-xl gradient-bg-subtle flex items-center justify-center">
              <FolderOpen className="w-5 h-5 text-primary" />
            </div>
            <div>
              <p className="text-2xl font-bold">{documents.length}</p>
              <p className="text-xs text-muted-foreground">Total Documents</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-border/50 bg-card/50">
          <CardContent className="p-5 flex items-center gap-4">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-emerald-500" />
            </div>
            <div>
              <p className="text-2xl font-bold">AI Ready</p>
              <p className="text-xs text-muted-foreground">Gemini Powered</p>
            </div>
          </CardContent>
        </Card>

        <Card className="border-border/50 bg-card/50">
          <CardContent className="p-5 flex items-center gap-4">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center">
              <MessageSquare className="w-5 h-5 text-amber-500" />
            </div>
            <div>
              <p className="text-2xl font-bold">Q&A</p>
              <p className="text-xs text-muted-foreground">Ask Anything</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Document list */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-3 border-primary/30 border-t-primary rounded-full animate-spin" />
            <p className="text-sm text-muted-foreground">Loading documents...</p>
          </div>
        </div>
      ) : documents.length === 0 ? (
        <Card className="border-border/50 border-dashed bg-card/30">
          <CardContent className="p-12 flex flex-col items-center justify-center text-center">
            <div className="w-16 h-16 rounded-2xl gradient-bg-subtle flex items-center justify-center mb-4">
              <FileText className="w-8 h-8 text-primary" />
            </div>
            <h3 className="text-lg font-semibold mb-2">No documents yet</h3>
            <p className="text-sm text-muted-foreground mb-6 max-w-sm">
              Upload your first document to start asking AI-powered questions
            </p>
            <Button
              onClick={() => navigate("/upload")}
              className="gradient-bg border-0 text-white shadow-lg shadow-purple-500/25"
            >
              Upload Your First Document
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {documents.map((doc, i) => (
            <Card
              key={doc.id}
              className="border-border/50 bg-card/50 hover:border-primary/30 hover:bg-accent/20 transition-all duration-300 group"
              style={{ animationDelay: `${i * 50}ms` }}
            >
              <CardContent className="p-5 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-xl gradient-bg-subtle flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                    <FileText className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <p className="font-semibold text-sm">{doc.filename}</p>
                    <div className="flex items-center gap-3 mt-1">
                      <span className="text-xs text-muted-foreground flex items-center gap-1">
                        ID: {doc.id}
                      </span>
                      {doc.created_at && (
                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {new Date(doc.created_at).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-primary hover:text-primary hover:bg-primary/10"
                    onClick={() => navigate(`/ask?doc=${doc.id}`)}
                  >
                    <MessageSquare className="w-4 h-4 mr-1.5" />
                    Ask
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-muted-foreground hover:text-red-400 hover:bg-red-500/10"
                    onClick={() => handleDelete(doc.id)}
                    disabled={deletingId === doc.id}
                  >
                    {deletingId === doc.id ? (
                      <span className="w-4 h-4 border-2 border-red-400/30 border-t-red-400 rounded-full animate-spin" />
                    ) : (
                      <Trash2 className="w-4 h-4" />
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}