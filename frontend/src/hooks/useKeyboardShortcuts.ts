import { useEffect } from "react";
import { useNoteStore } from "../stores/noteStore";

/**
 * Global keyboard shortcuts:
 *
 * Cmd/Ctrl + N          → New note
 * Cmd/Ctrl + Shift + F  → Focus search
 * Cmd/Ctrl + Backspace  → Trash selected note
 * Cmd/Ctrl + Shift + S  → Toggle star on selected note
 * Cmd/Ctrl + Shift + P  → Promote temporary note to regular note
 * ArrowUp / ArrowDown   → Navigate note list (when not in editor)
 */
export function useKeyboardShortcuts() {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const mod = e.metaKey || e.ctrlKey;
      const target = e.target as HTMLElement;
      const tagName = target.tagName.toLowerCase();
      const isEditing =
        tagName === "input" || tagName === "textarea" || target.isContentEditable;

      // Cmd+N — new note
      if (mod && e.key === "n") {
        e.preventDefault();
        useNoteStore.getState().createNote();
        return;
      }

      // Cmd+Shift+F — focus search
      if (mod && e.shiftKey && e.key.toLowerCase() === "f") {
        e.preventDefault();
        const searchInput = document.querySelector<HTMLInputElement>(
          ".notelist-search input",
        );
        searchInput?.focus();
        searchInput?.select();
        return;
      }

      // Cmd+Backspace — trash selected note
      if (mod && e.key === "Backspace" && !isEditing) {
        e.preventDefault();
        const { selectedNoteId, notes } = useNoteStore.getState();
        const note = notes.find((n) => n.id === selectedNoteId);
        if (note && !note.is_trashed) {
          useNoteStore.getState().trashNote(note.id);
        }
        return;
      }

      // Cmd+Shift+S — toggle star
      if (mod && e.shiftKey && e.key.toLowerCase() === "s") {
        e.preventDefault();
        const { selectedNoteId, notes } = useNoteStore.getState();
        const note = notes.find((n) => n.id === selectedNoteId);
        if (note && !note.is_trashed) {
          useNoteStore.getState().updateNote(note.id, { is_starred: !note.is_starred });
        }
        return;
      }

      // Cmd+Shift+P — promote temporary note to regular note
      if (mod && e.shiftKey && e.key.toLowerCase() === "p") {
        e.preventDefault();
        const { selectedNoteId, notes } = useNoteStore.getState();
        const note = notes.find((n) => n.id === selectedNoteId);
        if (note && note.is_temporary && !note.is_trashed) {
          useNoteStore.getState().promoteNote(note.id);
        }
        return;
      }

      // Arrow keys — navigate note list (only when not editing text)
      if ((e.key === "ArrowUp" || e.key === "ArrowDown") && !isEditing) {
        e.preventDefault();
        const { notes, selectedNoteId } = useNoteStore.getState();
        if (notes.length === 0) return;
        const currentIdx = notes.findIndex((n) => n.id === selectedNoteId);
        let nextIdx: number;
        if (e.key === "ArrowUp") {
          nextIdx = currentIdx <= 0 ? notes.length - 1 : currentIdx - 1;
        } else {
          nextIdx = currentIdx >= notes.length - 1 ? 0 : currentIdx + 1;
        }
        const next = notes[nextIdx];
        if (next) {
          useNoteStore.getState().selectNote(next.id);
        }
        return;
      }

      // Escape — blur active element (deselect search/editor)
      if (e.key === "Escape" && isEditing) {
        (target as HTMLElement).blur();
        return;
      }
    };

    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);
}
