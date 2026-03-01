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

export default function NoteList() {
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

  // Select first note when notes change and nothing selected
  useEffect(() => {
    const first = notes[0];
    if (notes.length > 0 && !selectedNoteId && first) {
      selectNote(first.id);
    }
  }, [notes, selectedNoteId, selectNote]);

  let title = "All Notes";
  if (viewFilter === "starred") title = "Starred";
  if (viewFilter === "trash") title = "Trash";
  if (activeFolderId) title = "Folder";

  return (
    <div className="notelist">
      <div className="notelist-header">
        <h3>{title}</h3>
        {viewFilter !== "trash" && (
          <button className="btn-icon" onClick={createNote} title="New note">
            ✏️
          </button>
        )}
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
            onClick={() => selectNote(note.id)}
          >
            <div className="note-item-title">
              {note.is_starred && "⭐ "}
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
