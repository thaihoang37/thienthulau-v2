import { useState, useEffect, useMemo } from "react";

interface ChapterItem {
  id?: string;
  title: { raw?: string; translated?: string } | null;
  order: number | null;
}

interface HomePageProps {
  onNavigate: (page: "single" | "batch") => void;
  onChapterClick: (order: number) => void;
}

const BOOK_ID = "7d274da0-2b6e-4571-b575-ffb4227c8181";
const PER_PAGE = 20;

const DESCRIPTION = `Trong Hỏa Sơn, Cơ Quan Tiên Cung do bậc tiên hiền đại năng để lại đang khát khao người kế thừa. Người mẹ liều mình tranh đoạt, lấy được Tiên Cung Bảo Ấn, lúc lâm chung phó thác cho Ninh Chuyết. Ngã Phật Tâm Ma Ấn! Độ mình thành Phật, độ người thành Ma. Chưởng ấn giả khẽ khắc tâm ấn, điều khiển cơ quan nhẹ tựa lông hồng. Mọi người ngự trị chúng thì thần mệt ý nặng; Ninh Chuyết lại có thể một tay điều khiển vạn vật, thanh thoát như đang múa. Ninh Chuyết: "Mẹ, nhi tử nhất định không phụ sự ủy thác của Người, đoạt lấy Tiên Cung đó!"`;

export default function HomePage({ onChapterClick }: HomePageProps) {
  const [chapters, setChapters] = useState<ChapterItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    async function fetchChapters() {
      try {
        const res = await fetch(`/api/chapter/list/${BOOK_ID}`);
        if (!res.ok) throw new Error("Failed to fetch chapters");
        const data = await res.json();
        setChapters(data);
      } catch (err) {
        console.error(err);
        setError("Không thể tải danh sách chương.");
      } finally {
        setLoading(false);
      }
    }
    fetchChapters();
  }, []);

  // Sort by order descending
  const sortedChapters = useMemo(
    () => [...chapters].sort((a, b) => (b.order ?? 0) - (a.order ?? 0)),
    [chapters],
  );

  const totalPages = Math.max(1, Math.ceil(sortedChapters.length / PER_PAGE));
  const paginatedChapters = sortedChapters.slice(
    (currentPage - 1) * PER_PAGE,
    currentPage * PER_PAGE,
  );

  // Generate page numbers to show (max 7 visible)
  const pageNumbers = useMemo(() => {
    const pages: (number | "...")[] = [];
    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      pages.push(1);
      if (currentPage > 3) pages.push("...");
      const start = Math.max(2, currentPage - 1);
      const end = Math.min(totalPages - 1, currentPage + 1);
      for (let i = start; i <= end; i++) pages.push(i);
      if (currentPage < totalPages - 2) pages.push("...");
      pages.push(totalPages);
    }
    return pages;
  }, [currentPage, totalPages]);

  const goToPage = (page: number) => {
    setCurrentPage(page);
    document.getElementById("chapters")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="min-h-screen bg-[#050510] text-[#e0e6f0] overflow-hidden font-[Inter,system-ui,sans-serif]">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-[#050510]/80 backdrop-blur-xl border-b border-white/[0.06]">
        <div className="max-w-[1100px] mx-auto px-4 sm:px-6 lg:px-8 h-20 sm:h-24 flex items-center gap-3">
          <img
            src="/logo.png"
            alt="Thiên Thư Lầu"
            className="w-18 h-18 sm:w-22 sm:h-22 object-contain"
          />
          <div className="flex flex-col">
            <span className="text-lg sm:text-xl font-bold tracking-wide bg-gradient-to-r from-cyan-300 via-blue-300 to-indigo-400 bg-clip-text text-transparent leading-tight">
              Thiên Thư Lâu
            </span>
          </div>
        </div>
      </header>

      {/* Background orbs */}
      <div className="fixed inset-0 -z-10 bg-[#050510]">
        <div className="absolute -top-[200px] -left-[100px] w-[600px] h-[600px] rounded-full bg-[radial-gradient(circle,#0066ff,#003399)] blur-[120px] opacity-15 animate-[orbFloat1_20s_ease-in-out_infinite]" />
        <div className="absolute -bottom-[150px] -right-[100px] w-[500px] h-[500px] rounded-full bg-[radial-gradient(circle,#00b4d8,#0077b6)] blur-[120px] opacity-15 animate-[orbFloat2_25s_ease-in-out_infinite]" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[350px] h-[350px] rounded-full bg-[radial-gradient(circle,#0ea5e9,#0284c7)] blur-[120px] opacity-10" />
      </div>

      {/* Hero Section — Book Info */}
      <section
        id="about"
        className="relative z-10 max-w-[1100px] mx-auto px-4 sm:px-6 lg:px-8 pt-10 sm:pt-14 pb-12"
      >
        <div className="flex flex-col sm:flex-row ga  p-8 sm:gap-10 items-center sm:items-start">
          {/* Cover Image */}
          <div className="shrink-0">
            <div className="relative group">
              <div className="absolute -inset-3 bg-gradient-to-br from-cyan-500/20 via-blue-500/15 to-indigo-500/20 rounded-2xl blur-2xl group-hover:blur-xl transition-all duration-500 opacity-50 group-hover:opacity-75" />
              <div className="relative p-0.5 bg-gradient-to-br from-cyan-500/40 via-blue-500/25 to-indigo-500/40 rounded-xl shadow-2xl shadow-blue-500/20">
                <img
                  src="/cover.jpg"
                  alt="Tiên Công Khai Vật"
                  className="w-44 sm:w-52 rounded-xl object-cover aspect-[3/4]"
                />
              </div>
            </div>
          </div>

          {/* Text content */}
          <div className="flex-1 min-w-0 space-y-4 text-center sm:text-left">
            <div className="inline-block px-3 py-1.5 bg-gradient-to-r from-cyan-500/15 to-indigo-500/15 border border-cyan-500/30 rounded-full">
              <span className="text-xs font-semibold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                Tiên Hiệp · Cơ Quan Thuật
              </span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-extrabold leading-tight tracking-tight">
              <span className="bg-gradient-to-r from-white via-blue-200 to-cyan-300 bg-clip-text text-transparent">
                Tiên Công Khai Vật
              </span>
            </h2>
            <p className="flex items-center gap-2 text-slate-400 justify-center sm:justify-start">
              <span>✍️</span> Tác giả:{" "}
              <span className="text-blue-300 font-medium">Cổ Chân Nhân</span>
            </p>
            <p className="text-sm text-slate-400 leading-relaxed">
              {DESCRIPTION}
            </p>

            {/* Stats */}
            <div className="flex items-center gap-6 pt-2 justify-center sm:justify-start">
              <div className="flex flex-col items-center sm:items-start">
                <span className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                  {chapters.length}
                </span>
                <span className="text-[0.7rem] text-slate-500 uppercase tracking-wider">
                  Chương đã dịch
                </span>
              </div>
              <div className="w-px h-8 bg-gradient-to-b from-transparent via-blue-500/30 to-transparent" />
              <div className="flex flex-col items-center sm:items-start">
                <span className="text-lg font-bold bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
                  Đang ra
                </span>
                <span className="text-[0.7rem] text-slate-500 uppercase tracking-wider">
                  Trạng thái
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Chapter List Section */}
      <section
        id="chapters"
        className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16"
      >
        <div className="text-center mb-10">
          <h2 className="text-3xl font-bold mb-2">
            <span className="bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
              📖 Danh Sách Chương
            </span>
          </h2>
          <p className="text-slate-500 text-sm">{chapters.length} chương</p>
        </div>

        {loading && (
          <div className="flex items-center justify-center gap-3 py-12 text-slate-500">
            <div className="w-5 h-5 border-2 border-blue-500/20 border-t-blue-500 rounded-full animate-spin" />
            <span>Đang tải danh sách chương...</span>
          </div>
        )}

        {error && (
          <div className="text-center py-8 px-6 text-red-400 bg-red-500/8 border border-red-500/15 rounded-2xl">
            {error}
          </div>
        )}

        {!loading && !error && chapters.length === 0 && (
          <div className="text-center py-12 text-slate-500">
            Chưa có chương nào được dịch.
          </div>
        )}

        {!loading && !error && paginatedChapters.length > 0 && (
          <>
            <div className="flex flex-col gap-2">
              {paginatedChapters.map((ch, idx) => {
                const titleText =
                  ch.title?.translated ||
                  ch.title?.raw ||
                  `Chương ${ch.order ?? idx + 1}`;
                return (
                  <div
                    key={ch.order ?? idx}
                    onClick={() => ch.order != null && onChapterClick(ch.order)}
                    className="flex items-center gap-4 px-5 py-4 rounded-xl bg-[#0a0f1e]/50 border border-blue-500/8 hover:border-blue-500/25 hover:bg-[#0f1528]/60 cursor-pointer transition-all duration-300 group hover:translate-x-1 hover:shadow-lg hover:shadow-blue-500/5"
                  >
                    <div className="flex items-center justify-center p-2 rounded-lg bg-gradient-to-br from-cyan-500/15 to-blue-500/15 border border-blue-500/20 text-blue-400 text-sm font-bold shrink-0">
                      Chương {ch.order ?? idx + 1}
                    </div>
                    <div className="flex-1 min-w-0">
                      <span className="text-slate-300 text-[0.95rem] block truncate group-hover:text-slate-100 transition-colors">
                        {titleText}
                      </span>
                    </div>
                    <span className="text-slate-600 group-hover:text-blue-400 transition-all group-hover:translate-x-1 shrink-0">
                      →
                    </span>
                  </div>
                );
              })}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 mt-8">
                <button
                  onClick={() => goToPage(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="px-3 py-2 rounded-lg text-sm font-medium border border-blue-500/20 text-slate-400 hover:text-slate-200 hover:border-blue-500/40 hover:bg-blue-500/10 transition-all disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer"
                >
                  ‹
                </button>
                {pageNumbers.map((p, i) =>
                  p === "..." ? (
                    <span key={`dots-${i}`} className="px-2 text-slate-600">
                      …
                    </span>
                  ) : (
                    <button
                      key={p}
                      onClick={() => goToPage(p)}
                      className={`w-9 h-9 rounded-lg text-sm font-medium transition-all cursor-pointer ${
                        currentPage === p
                          ? "bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-lg shadow-blue-500/30"
                          : "border border-blue-500/20 text-slate-400 hover:text-slate-200 hover:border-blue-500/40 hover:bg-blue-500/10"
                      }`}
                    >
                      {p}
                    </button>
                  ),
                )}
                <button
                  onClick={() => goToPage(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="px-3 py-2 rounded-lg text-sm font-medium border border-blue-500/20 text-slate-400 hover:text-slate-200 hover:border-blue-500/40 hover:bg-blue-500/10 transition-all disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer"
                >
                  ›
                </button>
              </div>
            )}
          </>
        )}
      </section>

      {/* Footer */}
      {/* <footer className="relative z-10 border-t border-blue-500/10 bg-[#050510]/80 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col sm:flex-row items-center justify-between text-sm text-slate-600">
          <div className="flex items-center gap-2">
            <img
              src="/logo.png"
              alt="Logo"
              className="w-6 h-6 object-contain"
            />
            <span className="font-medium bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
              Thiên Thư Lầu
            </span>
            <span className="text-slate-600">— Dịch truyện AI</span>
          </div>
          <p className="mt-3 sm:mt-0">© 2025 Thiên Thư Lầu</p>
        </div>
      </footer> */}
    </div>
  );
}
