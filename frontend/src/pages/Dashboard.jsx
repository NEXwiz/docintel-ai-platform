import { useEffect, useState } from "react"
import api from "@/api/client"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

export default function Dashboard({ onAsk }) {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)

  const fetchDocuments = async () => {
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
    fetchDocuments()
  }, [])

  const handleDelete = async (id) => {
    try {
      await api.delete(`/documents/${id}`)
      setDocuments(documents.filter((doc) => doc.id !== id))
    } catch (err) {
      console.error(err.response?.data || err.message)
      alert("Delete failed")
    }
  }

  if (loading) return <div className="p-6">Loading...</div>

  return (
    <div className="p-6 space-y-4">
      <h2 className="text-xl font-semibold">My Documents</h2>

      {documents.length === 0 && (
        <p className="text-sm text-muted-foreground">
          No documents uploaded yet.
        </p>
      )}

      {documents.map((doc) => (
        <Card key={doc.id}>
          <CardContent className="flex justify-between items-center p-4">
            <div>
              <p className="font-medium">{doc.filename}</p>
              <p className="text-xs text-muted-foreground">
                ID: {doc.id}
              </p>
            </div>

            <div className="space-x-2">
              <Button
                variant="outline"
                onClick={() => onAsk(doc.id)}
              >
                Ask
              </Button>

              <Button
                variant="destructive"
                onClick={() => handleDelete(doc.id)}
              >
                Delete
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
