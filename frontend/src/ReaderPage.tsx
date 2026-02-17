import { useState, useEffect, useCallback } from "react";

interface ReaderPageProps {
  bookId: string;
  chapterOrder: number;
  onBack: () => void;
  onNavigate: (order: number) => void;
}

interface ChapterDetail {
  id: string;
  title: string | null;
  order: number | null;
  summary: string | null;
  paragraphs: string[];
  prev_order: number | null;
  next_order: number | null;
}

export default function ReaderPage({
  bookId,
  chapterOrder,
  onBack,
  onNavigate,
}: ReaderPageProps) {
  const [chapter, setChapter] = useState<ChapterDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchChapter = useCallback(
    async (order: number) => {
      setLoading(true);
      setError("");
      setChapter(null);
      try {
        const res = await fetch(`/api/chapter/${bookId}/${order}`);
        if (!res.ok) throw new Error("Không tìm thấy chương");
        const data: ChapterDetail = await res.json();
        setChapter(data);
      } catch {
        setError("Không thể tải nội dung chương.");
      } finally {
        setLoading(false);
      }
    },
    [bookId],
  );

  useEffect(() => {
    fetchChapter(chapterOrder);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, [chapterOrder, fetchChapter]);

  /* ── Copy Protection ── */
  useEffect(() => {
    // Disable right-click context menu
    const handleContextMenu = (e: MouseEvent) => {
      e.preventDefault();
    };

    // Disable copy / cut / select-all shortcuts
    const handleKeyDown = (e: KeyboardEvent) => {
      if (
        (e.ctrlKey || e.metaKey) &&
        ["c", "x", "a", "u", "s", "p"].includes(e.key.toLowerCase())
      ) {
        e.preventDefault();
      }
      // Disable F12 / Ctrl+Shift+I (dev tools)
      if (e.key === "F12") e.preventDefault();
      if (
        (e.ctrlKey || e.metaKey) &&
        e.shiftKey &&
        e.key.toLowerCase() === "i"
      ) {
        e.preventDefault();
      }
    };

    // Disable copy event
    const handleCopy = (e: ClipboardEvent) => {
      e.preventDefault();
    };

    // Disable drag
    const handleDragStart = (e: DragEvent) => {
      e.preventDefault();
    };

    document.addEventListener("contextmenu", handleContextMenu);
    document.addEventListener("keydown", handleKeyDown);
    document.addEventListener("copy", handleCopy);
    document.addEventListener("dragstart", handleDragStart);

    return () => {
      document.removeEventListener("contextmenu", handleContextMenu);
      document.removeEventListener("keydown", handleKeyDown);
      document.removeEventListener("copy", handleCopy);
      document.removeEventListener("dragstart", handleDragStart);
    };
  }, []);

  const goTo = (order: number | null) => {
    if (order != null) onNavigate(order);
  };

  return (
    <div className="min-h-screen bg-[#050510] text-[#e0e6f0] font-[Inter,system-ui,sans-serif] select-none">
      {/* Background orbs */}
      <div className="fixed inset-0 -z-10 bg-[#050510]">
        <div className="absolute -top-[200px] -left-[100px] w-[600px] h-[600px] rounded-full bg-[radial-gradient(circle,#0066ff,#003399)] blur-[120px] opacity-10 animate-[orbFloat1_20s_ease-in-out_infinite]" />
        <div className="absolute -bottom-[150px] -right-[100px] w-[500px] h-[500px] rounded-full bg-[radial-gradient(circle,#3b82f6,#1d4ed8)] blur-[120px] opacity-10 animate-[orbFloat2_25s_ease-in-out_infinite]" />
      </div>

      {/* Sticky Header */}
      <header className="sticky top-0 z-50 bg-[#050510]/80 backdrop-blur-xl border-b border-white/[0.06]">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 h-14 flex items-center gap-3">
          <button
            onClick={onBack}
            className="flex items-center gap-1.5 text-slate-400 hover:text-slate-200 transition-colors text-sm cursor-pointer shrink-0"
          >
            <span className="text-lg">←</span>
            <span className="hidden sm:inline">Mục lục</span>
          </button>
          <div className="flex-1 min-w-0 text-center">
            <span className="text-sm font-medium text-slate-300 truncate block">
              Tiên Công Khai Vật
            </span>
          </div>
          {/* Spacer to center title */}
          <div className="w-16 shrink-0" />
        </div>
      </header>

      {/* Content */}
      <main className="max-w-3xl mx-auto px-5 sm:px-8 py-10 sm:py-14">
        {loading && (
          <div className="flex items-center justify-center gap-3 py-24 text-slate-500">
            <div className="w-5 h-5 border-2 border-blue-500/20 border-t-blue-500 rounded-full animate-spin" />
            <span>Đang tải nội dung chương...</span>
          </div>
        )}

        {error && (
          <div className="text-center py-12 px-6 text-red-400 bg-red-500/8 border border-red-500/15 rounded-2xl">
            {error}
          </div>
        )}

        {!loading && !error && chapter && (
          <article>
            {/* Chapter Title */}
            <h1 className="text-2xl sm:text-3xl font-bold text-center mb-8 sm:mb-12 leading-snug">
              <span>{`Chương ${chapter.order} - ${chapter.title}`}</span>
            </h1>

            {/* Paragraphs */}
            <div className="space-y-5 text-[1.05rem] sm:text-lg leading-[1.9] sm:leading-[2] text-slate-300/90 tracking-wide">
              {chapter.paragraphs.map((text, i) => (
                <p key={i} className="text-justify indent-8">
                  {text}
                </p>
              ))}
            </div>

            {/* Chapter Navigation */}
            <nav className="flex items-center justify-between mt-14 sm:mt-20 pt-8 border-t border-white/[0.06]">
              <button
                onClick={() => goTo(chapter.prev_order)}
                disabled={chapter.prev_order == null}
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium border border-blue-500/20 text-slate-400 hover:text-slate-200 hover:border-blue-500/40 hover:bg-blue-500/10 transition-all disabled:opacity-20 disabled:cursor-not-allowed cursor-pointer"
              >
                <span>←</span>
                <span>Chương trước</span>
              </button>

              <button
                onClick={onBack}
                className="px-4 py-2.5 rounded-xl text-sm font-medium text-slate-500 hover:text-slate-300 hover:bg-white/5 transition-all cursor-pointer"
              >
                Mục lục
              </button>

              <button
                onClick={() => goTo(chapter.next_order)}
                disabled={chapter.next_order == null}
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium border border-blue-500/20 text-slate-400 hover:text-slate-200 hover:border-blue-500/40 hover:bg-blue-500/10 transition-all disabled:opacity-20 disabled:cursor-not-allowed cursor-pointer"
              >
                <span>Chương sau</span>
                <span>→</span>
              </button>
            </nav>
          </article>
        )}
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-blue-500/10 bg-[#050510]/80 backdrop-blur-sm">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 py-6 flex items-center justify-between text-xs text-slate-600">
          <div className="flex items-center gap-2">
            <img
              src="/logo.png"
              alt="Logo"
              className="w-5 h-5 object-contain"
            />
            <span className="font-medium bg-gradient-to-r from-blue-300 to-blue-500 bg-clip-text text-transparent">
              Thiên Thư Lầu
            </span>
          </div>
          <p>© 2025 Thiên Thư Lầu</p>
        </div>
      </footer>
    </div>
  );
}
