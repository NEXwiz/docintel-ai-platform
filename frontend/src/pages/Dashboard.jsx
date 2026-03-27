import { useEffect, useState } from "react"
import api from "@/api/client"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

export default function Dashboard() {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
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

    fetchDocs()
  }, [])

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">Dashboard</h2>

      {loading ? (
        <p>Loading...</p>
      ) : documents.length === 0 ? (
        <p>No documents found</p>
      ) : (
        <div className="space-y-4">
          {documents.map((doc) => (
            <Card key={doc.id}>
              <CardContent className="p-4 flex justify-between items-center">
                <div>
                  <p className="font-medium">{doc.filename}</p>
                  <p className="text-sm text-muted-foreground">
                    ID: {doc.id}
                  </p>
                </div>

                <Button variant="outline">Ask</Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}