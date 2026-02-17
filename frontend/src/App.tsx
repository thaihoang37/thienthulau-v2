import { useState, useCallback } from "react";
import BatchUpload from "./BatchUpload";
import HomePage from "./HomePage";
import ReaderPage from "./ReaderPage";

interface Keyword {
  raw: string;
  translated: string;
  type: string;
}

interface SentencePair {
  raw: string;
  translated: string;
}

const typeLabels: Record<string, string> = {
  character: "👤 Nhân vật",
  location: "📍 Địa danh",
  faction: "🏛️ Thế lực",
  cultivation: "⚡ Cảnh giới",
  concept: "🌀 Thuật ngữ",
  skill: "🔥 Kỹ năng",
  artifact: "💎 Bảo vật",
  title: "👑 Danh xưng",
  other: "📝 Khác",
};

const typeColors: Record<string, string> = {
  character: "bg-blue-500/20 border-blue-500/50 text-blue-300",
  location: "bg-green-500/20 border-green-500/50 text-green-300",
  faction: "bg-purple-500/20 border-purple-500/50 text-purple-300",
  cultivation: "bg-yellow-500/20 border-yellow-500/50 text-yellow-300",
  concept: "bg-cyan-500/20 border-cyan-500/50 text-cyan-300",
  skill: "bg-orange-500/20 border-orange-500/50 text-orange-300",
  artifact: "bg-pink-500/20 border-pink-500/50 text-pink-300",
  title: "bg-amber-500/20 border-amber-500/50 text-amber-300",
  other: "bg-gray-500/20 border-gray-500/50 text-gray-300",
};

export default function App() {
  const [page, setPage] = useState<"home" | "single" | "batch" | "reader">(
    "home",
  );
  const [rawText, setRawText] = useState<string>("");
  const [sentences, setSentences] = useState<SentencePair[]>([]);
  const [keywords, setKeywords] = useState<Keyword[]>([]);
  const [isExtractingKeywords, setIsExtractingKeywords] =
    useState<boolean>(false);
  const [isTranslating, setIsTranslating] = useState<boolean>(false);
  const [fileName, setFileName] = useState<string>("");
  const [isDragOver, setIsDragOver] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const [currentStep, setCurrentStep] = useState<
    "idle" | "extracting" | "translating" | "done"
  >("idle");
  const [readerChapterOrder, setReaderChapterOrder] = useState<number>(1);

  const DEFAULT_BOOK_ID = "7d274da0-2b6e-4571-b575-ffb4227c8181";

  const processText = useCallback(async (text: string) => {
    // Extract glossary
    setCurrentStep("extracting");
    setIsExtractingKeywords(true);
    let extractedGlossary: Keyword[] = [];
    let chapterId: string | null = null;
    try {
      const keywordsResponse = await fetch("/api/glossary/extract", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, book_id: DEFAULT_BOOK_ID }),
      });

      if (keywordsResponse.ok) {
        const keywordsData = await keywordsResponse.json();
        extractedGlossary = keywordsData.glossaries || [];
        chapterId = keywordsData.chapter_id || null;
        setKeywords(extractedGlossary);
      }
    } catch (err) {
      console.error("Error extracting keywords:", err);
    } finally {
      setIsExtractingKeywords(false);
    }

    // Translate
    setCurrentStep("translating");
    setIsTranslating(true);
    try {
      const response = await fetch("/api/chapter/translate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text,
          book_id: DEFAULT_BOOK_ID,
          chapter_id: chapterId,
        }),
      });

      if (!response.ok) {
        throw new Error("Translation failed");
      }

      const data = await response.json();
      setSentences(data.sentences || []);
      setCurrentStep("done");
    } catch (err) {
      setError("Lỗi khi dịch văn bản. Vui lòng thử lại.");
      console.error(err);
      setCurrentStep("idle");
    } finally {
      setIsTranslating(false);
    }
  }, []);

  const handleFileUpload = useCallback(
    async (file: File) => {
      if (!file.name.endsWith(".txt")) {
        setError("Vui lòng chọn file .txt");
        return;
      }

      setError("");
      setFileName(file.name);

      const reader = new FileReader();
      reader.onload = async (e) => {
        const text = e.target?.result as string;
        setRawText(text);
        setSentences([]);
        setKeywords([]);
        await processText(text);
      };

      reader.readAsText(file);
    },
    [processText],
  );

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragOver(false);

      const file = e.dataTransfer.files[0];
      if (file) {
        handleFileUpload(file);
      }
    },
    [handleFileUpload],
  );

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        handleFileUpload(file);
      }
    },
    [handleFileUpload],
  );

  const handleRetranslate = async () => {
    if (!rawText) return;
    setError("");
    setKeywords([]);
    await processText(rawText);
  };

  const handleClear = () => {
    setRawText("");
    setSentences([]);
    setKeywords([]);
    setFileName("");
    setError("");
    setCurrentStep("idle");
  };

  const isLoading = isExtractingKeywords || isTranslating;

  // Group keywords by type
  const groupedKeywords = keywords.reduce(
    (acc, kw) => {
      const type = kw.type || "other";
      if (!acc[type]) acc[type] = [];
      acc[type].push(kw);
      return acc;
    },
    {} as Record<string, Keyword[]>,
  );

  if (page === "home") {
    return (
      <HomePage
        onNavigate={(p) => setPage(p)}
        onChapterClick={(order) => {
          setReaderChapterOrder(order);
          setPage("reader");
        }}
      />
    );
  }

  if (page === "reader") {
    return (
      <ReaderPage
        bookId={DEFAULT_BOOK_ID}
        chapterOrder={readerChapterOrder}
        onBack={() => setPage("home")}
        onNavigate={(order) => setReaderChapterOrder(order)}
      />
    );
  }

  if (page === "batch") {
    return <BatchUpload onBack={() => setPage("home")} />;
  }

  return (
    <main className="min-h-screen p-6 md:p-10">
      {/* Header */}
      <div className="text-center mb-8 fade-in">
        <h1 className="text-4xl md:text-5xl font-bold gradient-text mb-3">
          📚 Dịch Truyện AI
        </h1>
        <p className="text-[var(--text-muted)] text-lg">
          Upload file .txt và để AI dịch truyện cho bạn
        </p>
        <div className="flex gap-3 mt-4">
          <button
            onClick={() => setPage("home")}
            className="px-4 py-2 rounded-xl bg-[var(--surface)] border border-[var(--border)] 
                       hover:border-[var(--primary)] transition-all cursor-pointer text-sm"
          >
            🏠 Trang chủ
          </button>
          <button
            onClick={() => setPage("batch")}
            className="px-4 py-2 rounded-xl bg-[var(--surface)] border border-[var(--border)] 
                       hover:border-[var(--primary)] transition-all cursor-pointer text-sm"
          >
            📦 Batch Upload →
          </button>
        </div>
      </div>

      {/* Upload Zone */}
      {!rawText && (
        <div
          className={`upload-zone max-w-2xl mx-auto mb-8 fade-in ${
            isDragOver ? "dragover" : ""
          }`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
        >
          <div className="text-6xl mb-4">📄</div>
          <h3 className="text-xl font-semibold mb-2">
            Kéo thả file .txt vào đây
          </h3>
          <p className="text-[var(--text-muted)] mb-4">hoặc</p>
          <label className="btn-primary cursor-pointer inline-block">
            Chọn File
            <input
              type="file"
              accept=".txt"
              onChange={handleInputChange}
              className="hidden"
            />
          </label>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="max-w-2xl mx-auto mb-6 p-4 bg-red-500/20 border border-red-500/50 rounded-xl text-red-400 text-center fade-in">
          {error}
        </div>
      )}

      {/* File Info & Actions */}
      {rawText && (
        <div className="flex flex-wrap items-center justify-center gap-4 mb-6 fade-in">
          <div className="glass px-4 py-2 rounded-xl flex items-center gap-2">
            <span>📄</span>
            <span className="text-[var(--text-muted)]">{fileName}</span>
          </div>

          {/* Progress Indicator */}
          {isLoading && (
            <div className="glass px-4 py-2 rounded-xl flex items-center gap-2">
              <div className="loading-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <span className="text-[var(--text-muted)]">
                {currentStep === "extracting"
                  ? "Đang trích xuất từ khóa..."
                  : "Đang dịch..."}
              </span>
            </div>
          )}

          <button
            onClick={handleRetranslate}
            disabled={isLoading}
            className="btn-primary"
          >
            {isLoading ? "Đang xử lý..." : "🔄 Dịch lại"}
          </button>
          <button
            onClick={handleClear}
            className="px-4 py-3 rounded-xl bg-[var(--surface)] border border-[var(--border)] 
                       hover:border-[var(--primary)] transition-all cursor-pointer"
          >
            ✕ Xóa
          </button>
        </div>
      )}

      {/* Keywords Panel */}
      {rawText && keywords.length > 0 && (
        <div className="mb-6 fade-in">
          <div className="glass rounded-xl p-4">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <span>🔑</span>
              <span>Từ khóa & Thuật ngữ ({keywords.length})</span>
            </h3>
            <div className="space-y-4">
              {Object.entries(groupedKeywords).map(([type, kws]) => (
                <div key={type}>
                  <h4 className="text-sm font-medium text-[var(--text-muted)] mb-2">
                    {typeLabels[type] || type}
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {kws.map((kw, idx) => (
                      <div
                        key={idx}
                        className={`px-3 py-1.5 rounded-lg border text-sm ${typeColors[type] || typeColors.other}`}
                      >
                        <span className="opacity-70">{kw.raw}</span>
                        <span className="mx-1.5">→</span>
                        <span className="font-medium">{kw.translated}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Translation Panels */}
      {rawText && (
        <div className="fade-in">
          <div className="glass rounded-xl p-6">
            <div className="flex items-center gap-4 mb-6">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <span>📖</span>
                <span>Bản gốc</span>
              </h2>
              <div className="h-px flex-1 bg-[var(--border)]"></div>
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <span>✨</span>
                <span>Bản dịch</span>
              </h2>
            </div>

            {isTranslating ? (
              <div className="flex flex-col items-center justify-center py-20 gap-4">
                <div className="loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <p className="text-[var(--text-muted)]">Đang dịch văn bản...</p>
              </div>
            ) : sentences.length > 0 ? (
              <div className="space-y-4">
                {sentences.map((sentence, index) => (
                  <div
                    key={index}
                    className="grid grid-cols-1 lg:grid-cols-2 gap-4 p-4 rounded-lg bg-[var(--surface)] border border-[var(--border)] hover:border-[var(--primary)] transition-all"
                  >
                    {/* Raw sentence */}
                    <div className="flex gap-3">
                      <div className="shrink-0 w-8 h-8 rounded-full bg-purple-500/20 text-purple-300 flex items-center justify-center text-sm font-semibold">
                        {index + 1}
                      </div>
                      <div className="flex-1 text-[var(--text-muted)] leading-relaxed">
                        {sentence.raw}
                      </div>
                    </div>

                    {/* Translated sentence */}
                    <div className="flex gap-3">
                      <div className="shrink-0 w-8 h-8 rounded-full bg-green-500/20 text-green-300 flex items-center justify-center text-sm font-semibold">
                        {index + 1}
                      </div>
                      <div className="flex-1 leading-relaxed">
                        {sentence.translated}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center justify-center py-20 text-[var(--text-muted)]">
                Bản dịch sẽ hiển thị ở đây
              </div>
            )}
          </div>
        </div>
      )}
    </main>
  );
}
