import { useEffect, useRef } from "react";
import { useNoteStore } from "../stores/noteStore";

function stripHtml(html: string): string {
  const tmp = document.createElement("div");
  tmp.innerHTML = html;
  return tmp.textContent || tmp.innerText || "";
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const dayMs = 86400000;

  if (diff < dayMs) {
    return date.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
  }
  if (diff < 7 * dayMs) {
    return date.toLocaleDateString([], { weekday: "short" });
  }
  return date.toLocaleDateString([], { month: "short", day: "numeric" });
}

export default function NoteList({
  onNoteSelect,
}: {
  onNoteSelect: () => void;
}) {
  const {
    notes,
    selectedNoteId,
    selectNote,
    viewFilter,
    activeFolderId,
    searchQuery,
    setSearchQuery,
    createNote,
    isLoading,
  } = useNoteStore();
  const searchRef = useRef<HTMLInputElement>(null);
  const searchTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const handleSearchChange = (value: string) => {
    if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);
    searchTimeoutRef.current = setTimeout(() => {
      setSearchQuery(value);
    }, 300);
  };

  const handleNoteClick = (id: string) => {
    selectNote(id);
    onNoteSelect();
  };

  // Select first note when notes change and nothing selected
  useEffect(() => {
    const first = notes[0];
    if (notes.length > 0 && !selectedNoteId && first) {
      selectNote(first.id);
    }
  }, [notes, selectedNoteId, selectNote]);

  let title = "All Notes";
  if (viewFilter === "starred") title = "Starred";
  if (viewFilter === "temporary") title = "Scratchpad";
  if (viewFilter === "trash") title = "Trash";
  if (activeFolderId) title = "Folder";

  return (
    <div className="notelist">
      <div className="notelist-header">
        <h3>{title}</h3>
        <div style={{ display: "flex", gap: 4, alignItems: "center" }}>
          {viewFilter !== "trash" && (
            <button className="btn-icon" onClick={createNote} title="New note">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                <path d="M12 5v14M5 12h14" />
              </svg>
            </button>
          )}
        </div>
      </div>

      <div className="notelist-search">
        <input
          ref={searchRef}
          type="text"
          placeholder="Search notes..."
          defaultValue={searchQuery}
          onChange={(e) => handleSearchChange(e.target.value)}
        />
      </div>

      <div className="notelist-items">
        {isLoading && notes.length === 0 && (
          <div className="notelist-empty">Loading...</div>
        )}
        {!isLoading && notes.length === 0 && (
          <div className="notelist-empty">
            {searchQuery ? "No matching notes" : "No notes yet"}
          </div>
        )}
        {notes.map((note) => (
          <div
            key={note.id}
            className={`note-item${selectedNoteId === note.id ? " active" : ""}`}
            onClick={() => handleNoteClick(note.id)}
          >
            <div className="note-item-title">
              {note.is_starred && "⭐ "}
              {note.is_temporary && "📋 "}
              {note.title || "Untitled"}
            </div>
            <div className="note-item-preview">
              {stripHtml(note.body).slice(0, 80) || "No content"}
            </div>
            <div className="note-item-date">{formatDate(note.updated_at)}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
