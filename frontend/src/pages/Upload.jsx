import { useState, useRef } from "react"
import { useNavigate } from "react-router-dom"
import api from "@/api/client"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Upload as UploadIcon, FileText, CheckCircle2, AlertCircle, X, CloudUpload } from "lucide-react"

const ACCEPTED_TYPES = [".pdf", ".docx", ".txt"]

export default function Upload() {
  const [file, setFile] = useState(null)
  const [uploadInfo, setUploadInfo] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef(null)
  const navigate = useNavigate()

  const handleFile = (f) => {
    setError("")
    setUploadInfo(null)

    const ext = f.name.substring(f.name.lastIndexOf(".")).toLowerCase()
    if (!ACCEPTED_TYPES.includes(ext)) {
      setError(`Unsupported file type. Please upload: ${ACCEPTED_TYPES.join(", ")}`)
      return
    }
    setFile(f)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragActive(false)
    if (e.dataTransfer.files?.[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file first")
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
    } catch (err) {
      console.error(err.response?.data || err.message)
      setError(err.response?.data?.detail || "Upload failed. Please try again.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8 animate-slide-up">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Upload Document</h2>
        <p className="text-muted-foreground mt-1">
          Upload a PDF, DOCX, or TXT file to start asking questions
        </p>
      </div>

      <div className="max-w-xl">
        {/* Drop zone */}
        <Card
          className={`border-2 border-dashed transition-all duration-300 cursor-pointer ${
            dragActive
              ? "border-primary bg-primary/5"
              : file
              ? "border-emerald-500/50 bg-emerald-500/5"
              : "border-border/50 bg-card/30 hover:border-primary/30 hover:bg-accent/10"
          }`}
          onDragOver={(e) => { e.preventDefault(); setDragActive(true) }}
          onDragLeave={() => setDragActive(false)}
          onDrop={handleDrop}
          onClick={() => !file && fileInputRef.current?.click()}
        >
          <CardContent className="p-10 flex flex-col items-center justify-center text-center">
            {file ? (
              <>
                <div className="w-14 h-14 rounded-2xl bg-emerald-500/10 flex items-center justify-center mb-4">
                  <FileText className="w-7 h-7 text-emerald-500" />
                </div>
                <p className="font-semibold text-sm mb-1">{file.name}</p>
                <p className="text-xs text-muted-foreground mb-4">
                  {(file.size / 1024).toFixed(1)} KB
                </p>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-muted-foreground hover:text-red-400"
                  onClick={(e) => {
                    e.stopPropagation()
                    setFile(null)
                    setUploadInfo(null)
                  }}
                >
                  <X className="w-4 h-4 mr-1" />
                  Remove
                </Button>
              </>
            ) : (
              <>
                <div className="w-14 h-14 rounded-2xl gradient-bg-subtle flex items-center justify-center mb-4">
                  <CloudUpload className="w-7 h-7 text-primary" />
                </div>
                <p className="font-semibold text-sm mb-1">
                  {dragActive ? "Drop your file here" : "Drag & drop your file here"}
                </p>
                <p className="text-xs text-muted-foreground mb-4">
                  or click to browse • PDF, DOCX, TXT
                </p>
              </>
            )}
          </CardContent>
        </Card>

        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.txt"
          className="hidden"
          onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
        />

        {/* Upload button */}
        {file && !uploadInfo && (
          <Button
            onClick={handleUpload}
            disabled={loading}
            className="w-full mt-4 h-11 gradient-bg border-0 text-white font-semibold shadow-lg shadow-purple-500/25 hover:opacity-90 transition-opacity"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Processing document...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <UploadIcon className="w-4 h-4" />
                Upload & Process
              </span>
            )}
          </Button>
        )}

        {/* Success */}
        {uploadInfo && (
          <Card className="mt-4 border-emerald-500/30 bg-emerald-500/5 animate-slide-up">
            <CardContent className="p-5 space-y-4">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                <span className="font-semibold text-sm text-emerald-400">Upload successful!</span>
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="p-3 rounded-lg bg-card/50">
                  <p className="text-xs text-muted-foreground">Document ID</p>
                  <p className="font-bold text-lg">{uploadInfo.document_id}</p>
                </div>
                <div className="p-3 rounded-lg bg-card/50">
                  <p className="text-xs text-muted-foreground">Chunks Stored</p>
                  <p className="font-bold text-lg">{uploadInfo.chunks_stored}</p>
                </div>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-primary hover:bg-primary/10"
                  onClick={() => navigate(`/ask?doc=${uploadInfo.document_id}`)}
                >
                  Ask Questions →
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-muted-foreground"
                  onClick={() => {
                    setFile(null)
                    setUploadInfo(null)
                  }}
                >
                  Upload Another
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Error */}
        {error && (
          <div className="mt-4 p-4 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center gap-3 animate-fade-in">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}
      </div>
    </div>
  )
}
