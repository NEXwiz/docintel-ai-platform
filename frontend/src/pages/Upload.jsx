import { useState } from "react"
import api from "@/api/client"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

export default function Upload({ onUploadSuccess }) {
  const [file, setFile] = useState(null)
  const [uploadInfo, setUploadInfo] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file")
      return
    }

    try {
      setLoading(true)
      setError("")
      setUploadInfo(null)

      const formData = new FormData()
      formData.append("file", file)

      const res = await api.post("/documents/upload", formData)

      setUploadInfo(res.data)

      if (onUploadSuccess) {
        onUploadSuccess(res.data.document_id)
      }

    } catch (err) {
      console.error(err.response?.data || err.message)
      setError("Upload failed")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 flex justify-center">
      <Card className="w-[400px]">
        <CardContent className="pt-6 space-y-4">
          <h2 className="text-xl font-semibold">Upload Document</h2>

          <input
            type="file"
            onChange={(e) => setFile(e.target.files[0])}
            className="block w-full text-sm"
          />

          <Button onClick={handleUpload} disabled={loading}>
            {loading ? "Uploading..." : "Upload"}
          </Button>

          {uploadInfo && (
            <div className="text-sm space-y-1 text-green-600">
              <p>Document ID: {uploadInfo.document_id}</p>
              <p>Chunks stored: {uploadInfo.chunks_stored}</p>
            </div>
          )}

          {error && (
            <p className="text-sm text-red-500">{error}</p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
