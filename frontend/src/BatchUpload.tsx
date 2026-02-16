import { useState, useCallback, useRef } from "react";

interface FileStatus {
  name: string;
  status: "pending" | "extracting" | "translating" | "done" | "failed";
  error?: string;
}

const DEFAULT_BOOK_ID = "7d274da0-2b6e-4571-b575-ffb4227c8181";

const statusConfig: Record<string, { icon: string; label: string; color: string }> = {
  pending: { icon: "⏳", label: "Chờ xử lý", color: "text-zinc-500" },
  extracting: { icon: "🔍", label: "Đang trích xuất...", color: "text-cyan-400" },
  translating: { icon: "✍️", label: "Đang dịch...", color: "text-yellow-400" },
  done: { icon: "✅", label: "Hoàn thành", color: "text-green-400" },
  failed: { icon: "❌", label: "Lỗi", color: "text-red-400" },
};

export default function BatchUpload({ onBack }: { onBack: () => void }) {
  const [files, setFiles] = useState<FileStatus[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const abortRef = useRef(false);
  const batchFilesRef = useRef<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const folderInputRef = useRef<HTMLInputElement>(null);

  const addFiles = useCallback((newFiles: File[]) => {
    const txtFiles = newFiles
      .filter((f) => f.name.endsWith(".txt"))
      .sort((a, b) => a.name.localeCompare(b.name));

    if (txtFiles.length === 0) return;

    // Read file contents and store
    const fileEntries: FileStatus[] = txtFiles.map((f) => ({
      name: f.name,
      status: "pending" as const,
    }));

    setFiles((prev) => [...prev, ...fileEntries]);

    // Store actual File objects for processing
    batchFilesRef.current = [...batchFilesRef.current, ...txtFiles];
  }, []);

  const processAllFiles = useCallback(async () => {
    const fileObjects = batchFilesRef.current;
    if (fileObjects.length === 0) return;

    setIsProcessing(true);
    abortRef.current = false;

    for (let i = 0; i < fileObjects.length; i++) {
      if (abortRef.current) break;

      const file = fileObjects[i];

      // Skip already processed files
      setFiles((prev) => {
        if (prev[i]?.status === "done") return prev;
        return prev;
      });

      // Read file content
      const text = await new Promise<string>((resolve) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target?.result as string);
        reader.readAsText(file);
      });

      // Step 1: Extract glossary
      setFiles((prev) =>
        prev.map((f, idx) => (idx === i ? { ...f, status: "extracting" } : f))
      );

      let chapterId: string | null = null;

      try {
        const extractRes = await fetch("/api/glossary/extract", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text, book_id: DEFAULT_BOOK_ID }),
        });

        if (extractRes.ok) {
          const data = await extractRes.json();
          chapterId = data.chapter_id || null;
        } else {
          throw new Error(`Extract failed: ${extractRes.status}`);
        }
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : String(err);
        setFiles((prev) =>
          prev.map((f, idx) =>
            idx === i ? { ...f, status: "failed", error: message } : f
          )
        );
        continue;
      }

      if (abortRef.current) break;

      // Step 2: Translate
      setFiles((prev) =>
        prev.map((f, idx) => (idx === i ? { ...f, status: "translating" } : f))
      );

      try {
        const translateRes = await fetch("/api/chapter/translate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text,
            book_id: DEFAULT_BOOK_ID,
            chapter_id: chapterId,
          }),
        });

        if (!translateRes.ok) {
          throw new Error(`Translate failed: ${translateRes.status}`);
        }

        setFiles((prev) =>
          prev.map((f, idx) => (idx === i ? { ...f, status: "done" } : f))
        );
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : String(err);
        setFiles((prev) =>
          prev.map((f, idx) =>
            idx === i ? { ...f, status: "failed", error: message } : f
          )
        );
      }
    }

    setIsProcessing(false);
  }, []);

  const handleStop = useCallback(() => {
    abortRef.current = true;
  }, []);

  const handleClear = useCallback(() => {
    setFiles([]);
    batchFilesRef.current = [];
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      const droppedFiles = Array.from(e.dataTransfer.files);
      addFiles(droppedFiles);
    },
    [addFiles]
  );

  // Stats
  const totalFiles = files.length;
  const doneCount = files.filter((f) => f.status === "done").length;
  const failedCount = files.filter((f) => f.status === "failed").length;
  const processingFile = files.find(
    (f) => f.status === "extracting" || f.status === "translating"
  );
  const failedFiles = files.filter((f) => f.status === "failed");
  const progress = totalFiles > 0 ? Math.round((doneCount / totalFiles) * 100) : 0;

  return (
    <main className="min-h-screen p-6 md:p-10">
      {/* Header */}
      <div className="text-center mb-8 fade-in">
        <h1 className="text-4xl md:text-5xl font-bold gradient-text mb-3">
          📦 Batch Upload
        </h1>
        <p className="text-[var(--text-muted)] text-lg">
          Upload nhiều file .txt để xử lý hàng loạt
        </p>
        <button
          onClick={onBack}
          className="mt-4 px-4 py-2 rounded-xl bg-[var(--surface)] border border-[var(--border)] 
                     hover:border-[var(--primary)] transition-all cursor-pointer text-sm"
        >
          ← Quay lại trang đơn
        </button>
      </div>

      {/* Upload Zone */}
      {!isProcessing && (
        <div className="max-w-3xl mx-auto mb-8 fade-in">
          <div
            className={`upload-zone ${isDragOver ? "dragover" : ""}`}
            onDrop={handleDrop}
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragOver(true);
            }}
            onDragLeave={(e) => {
              e.preventDefault();
              setIsDragOver(false);
            }}
          >
            <div className="text-6xl mb-4">📁</div>
            <h3 className="text-xl font-semibold mb-2">
              Kéo thả nhiều file .txt vào đây
            </h3>
            <p className="text-[var(--text-muted)] mb-4">hoặc</p>
            <div className="flex gap-3 justify-center flex-wrap">
              <label className="btn-primary cursor-pointer inline-block">
                Chọn Files
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".txt"
                  multiple
                  onChange={(e) => {
                    if (e.target.files) addFiles(Array.from(e.target.files));
                  }}
                  className="hidden"
                />
              </label>
              <label className="btn-primary cursor-pointer inline-block">
                Chọn Folder
                <input
                  ref={folderInputRef}
                  type="file"
                  // @ts-ignore
                  webkitdirectory=""
                  directory=""
                  onChange={(e) => {
                    if (e.target.files) addFiles(Array.from(e.target.files));
                  }}
                  className="hidden"
                />
              </label>
            </div>
          </div>
        </div>
      )}

      {/* Controls */}
      {files.length > 0 && (
        <div className="max-w-3xl mx-auto mb-6 fade-in">
          <div className="glass rounded-xl p-4">
            {/* Progress bar */}
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <span className="text-sm font-medium">
                  {isProcessing ? (
                    <>
                      {processingFile && (
                        <span className="text-[var(--text-muted)]">
                          Đang xử lý: <span className="text-[var(--text)]">{processingFile.name}</span>
                        </span>
                      )}
                    </>
                  ) : (
                    <span className="text-[var(--text-muted)]">
                      {doneCount === totalFiles && totalFiles > 0
                        ? "✅ Hoàn thành tất cả!"
                        : `${totalFiles} file đã chọn`}
                    </span>
                  )}
                </span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <span className="text-green-400">{doneCount} ✓</span>
                {failedCount > 0 && (
                  <span className="text-red-400">{failedCount} ✗</span>
                )}
                <span className="text-[var(--text-muted)]">
                  {doneCount + failedCount}/{totalFiles}
                </span>
              </div>
            </div>

            {/* Progress bar visual */}
            <div className="w-full h-2 bg-[var(--surface)] rounded-full overflow-hidden mb-4">
              <div
                className="h-full rounded-full transition-all duration-500 ease-out"
                style={{
                  width: `${progress}%`,
                  background: "linear-gradient(90deg, var(--primary), #06b6d4)",
                }}
              />
            </div>

            {/* Action buttons */}
            <div className="flex gap-3 justify-center">
              {!isProcessing ? (
                <>
                  <button onClick={processAllFiles} className="btn-primary">
                    🚀 Bắt đầu xử lý ({files.filter(f => f.status === 'pending').length} file)
                  </button>
                  <button
                    onClick={handleClear}
                    className="px-4 py-3 rounded-xl bg-[var(--surface)] border border-[var(--border)] 
                               hover:border-[var(--primary)] transition-all cursor-pointer"
                  >
                    ✕ Xóa tất cả
                  </button>
                </>
              ) : (
                <button
                  onClick={handleStop}
                  className="px-4 py-3 rounded-xl bg-red-500/20 border border-red-500/50 
                             hover:bg-red-500/30 transition-all cursor-pointer text-red-400"
                >
                  ⏹ Dừng
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* File List */}
      {files.length > 0 && (
        <div className="max-w-3xl mx-auto mb-6 fade-in">
          <div className="glass rounded-xl p-4">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <span>📋</span>
              <span>Danh sách file ({files.length})</span>
            </h3>
            <div className="space-y-1 max-h-[400px] overflow-y-auto pr-2">
              {files.map((file, idx) => {
                const config = statusConfig[file.status];
                return (
                  <div
                    key={idx}
                    className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-all ${
                      file.status === "extracting" || file.status === "translating"
                        ? "bg-[var(--primary)]/10 border border-[var(--primary)]/30"
                        : file.status === "failed"
                        ? "bg-red-500/5"
                        : file.status === "done"
                        ? "bg-green-500/5"
                        : "bg-transparent"
                    }`}
                  >
                    <span className="text-lg">{config.icon}</span>
                    <span className="flex-1 text-sm truncate font-mono">
                      {file.name}
                    </span>
                    <span className={`text-xs font-medium ${config.color}`}>
                      {config.label}
                    </span>
                    {(file.status === "extracting" || file.status === "translating") && (
                      <div className="loading-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Failed Files */}
      {failedFiles.length > 0 && (
        <div className="max-w-3xl mx-auto mb-6 fade-in">
          <div className="glass rounded-xl p-4 border border-red-500/30">
            <h3 className="text-lg font-semibold mb-3 flex items-center gap-2 text-red-400">
              <span>⚠️</span>
              <span>File lỗi ({failedFiles.length})</span>
            </h3>
            <div className="space-y-2">
              {failedFiles.map((file, idx) => (
                <div
                  key={idx}
                  className="flex items-start gap-3 px-3 py-2 rounded-lg bg-red-500/10"
                >
                  <span className="text-lg">❌</span>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-mono truncate">{file.name}</div>
                    {file.error && (
                      <div className="text-xs text-red-400/70 mt-0.5">
                        {file.error}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
