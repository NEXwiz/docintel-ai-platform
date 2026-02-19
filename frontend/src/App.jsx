import { useState } from "react"
import Login from "@/pages/Login"
import Upload from "@/pages/Upload"
import QA from "@/pages/QA"
import Dashboard from "@/pages/Dashboard"
import { Button } from "@/components/ui/button"


export default function App() {
  const [token, setToken] = useState(null)
  const [page, setPage] = useState("dashboard")
  const [selectedDocId, setSelectedDocId] = useState(null)


  if (!token) {
    return <Login onLogin={setToken} />
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between p-4 border-b">
        <h1 className="text-xl font-bold">DocIntel AI</h1>

        <div className="space-x-2">
          <Button variant="outline" onClick={() => setPage("upload")}>
            Upload
          </Button>
          <Button variant="outline" onClick={() => setPage("dashboard")}>
            Dashboard
          </Button>
          <Button onClick={() => setToken(null)}>Logout</Button>
        </div>
      </div>

      {page === "dashboard" && (
        <Dashboard
          onAsk={(docId) => {
            setSelectedDocId(docId)
            setPage("qa")
          }}
        />
      )}

      {page === "upload" && (
        <Upload
          onUploadSuccess={() => {
            setPage("dashboard")
          }}
        />
      )}

      {page === "qa" && (
          <QA initialDocumentId={selectedDocId} />
      )}
    </div>
  )
}
