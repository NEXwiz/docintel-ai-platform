import { useState, useEffect } from "react"
import api from "@/api/client"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"

export default function QA({initialDocumentId}) {
  const [query, setQuery] = useState("")
  const [documentId, setDocumentId] = useState("")
  const [answer, setAnswer] = useState("")
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (initialDocumentId){
        setDocumentId(String(initialDocumentId))
    }
  },[initialDocumentId])

  const handleAsk = async () => {
    if (!query || !documentId) {
      alert("Provide query and document ID")
      return
    }

    try {
      setLoading(true)
      setAnswer("")
      setSources([])

      const res = await api.post(
        `/qa/?query=${encodeURIComponent(query)}&document_id=${documentId}`
      )

      setAnswer(res.data.answer)
      setSources(res.data.sources)
    } catch (err) {
      console.error(err.response?.data || err.message)
      alert("Error fetching answer")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 flex justify-center">
      <Card className="w-[600px]">
        <CardContent className="pt-6 space-y-4">
          <h2 className="text-xl font-semibold">Ask Question</h2>

          <Input
            placeholder="Document ID"
            value={documentId}
            onChange={(e) => setDocumentId(e.target.value)}
          />

          <Input
            placeholder="Ask something..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />

          <Button onClick={handleAsk} disabled={loading}>
            {loading ? "Thinking..." : "Ask"}
          </Button>

          {answer && (
            <div className="mt-4 space-y-3">
              <div>
                <h3 className="font-semibold">Answer:</h3>
                <p className="text-sm">{answer}</p>
              </div>

              <div>
                <h3 className="font-semibold">Sources:</h3>
                <div className="space-y-2">
                  {sources.map((src, index) => (
                    <div
                      key={index}
                      className="text-xs bg-muted p-2 rounded"
                    >
                      {src}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
