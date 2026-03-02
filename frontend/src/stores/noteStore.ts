import { create } from "zustand";
import { api } from "../services/api";
import type { Note } from "../types";

type ViewFilter = "all" | "starred" | "trash" | "temporary";

interface NoteState {
  notes: Note[];
  selectedNoteId: string | null;
  viewFilter: ViewFilter;
  activeFolderId: string | null;
  searchQuery: string;
  isLoading: boolean;

  fetchNotes: () => Promise<void>;
  selectNote: (id: string | null) => void;
  setViewFilter: (filter: ViewFilter) => void;
  setActiveFolderId: (id: string | null) => void;
  setSearchQuery: (query: string) => void;
  createNote: () => Promise<Note | null>;
  updateNote: (id: string, data: Partial<Pick<Note, "title" | "body" | "folder_id" | "is_starred" | "is_temporary">>) => Promise<void>;
  trashNote: (id: string) => Promise<void>;
  restoreNote: (id: string) => Promise<void>;
  permanentDeleteNote: (id: string) => Promise<void>;
  promoteNote: (id: string) => Promise<void>;

  selectedNote: () => Note | undefined;
}

export const useNoteStore = create<NoteState>((set, get) => ({
  notes: [],
  selectedNoteId: null,
  viewFilter: "all",
  activeFolderId: null,
  searchQuery: "",
  isLoading: false,

  selectedNote: () => {
    const { notes, selectedNoteId } = get();
    return notes.find((n) => n.id === selectedNoteId);
  },

  fetchNotes: async () => {
    const { viewFilter, activeFolderId, searchQuery } = get();
    set({ isLoading: true });

    const params = new URLSearchParams();
    if (viewFilter === "trash") params.set("trashed", "true");
    if (viewFilter === "starred") params.set("starred", "true");
    if (viewFilter === "temporary") params.set("temporary", "true");
    if (activeFolderId) params.set("folder_id", activeFolderId);
    if (searchQuery) params.set("search", searchQuery);

    const query = params.toString();
    const url = `/notes${query ? `?${query}` : ""}`;

    try {
      const data = await api.get<Note[]>(url);
      set({ notes: data, isLoading: false });
    } catch {
      set({ notes: [], isLoading: false });
    }
  },

  selectNote: (id) => set({ selectedNoteId: id }),

  setViewFilter: (filter) => {
    set({ viewFilter: filter, activeFolderId: null, searchQuery: "", selectedNoteId: null });
    get().fetchNotes();
  },

  setActiveFolderId: (id) => {
    set({ activeFolderId: id, viewFilter: "all", searchQuery: "", selectedNoteId: null });
    get().fetchNotes();
  },

  setSearchQuery: (query) => {
    set({ searchQuery: query });
    get().fetchNotes();
  },

  createNote: async () => {
    const { activeFolderId, viewFilter } = get();
    const payload: Record<string, string | boolean> = {};
    if (activeFolderId && viewFilter === "all") {
      payload.folder_id = activeFolderId;
    }
    if (viewFilter === "temporary") {
      payload.is_temporary = true;
    }
    try {
      const note = await api.post<Note>("/notes", payload);
      await get().fetchNotes();
      set({ selectedNoteId: note.id });
      return note;
    } catch {
      return null;
    }
  },

  updateNote: async (id, data) => {
    try {
      await api.put<Note>(`/notes/${id}`, data);
      await get().fetchNotes();
    } catch {
      // silently fail
    }
  },

  trashNote: async (id) => {
    try {
      await api.delete(`/notes/${id}`);
      const { selectedNoteId } = get();
      if (selectedNoteId === id) set({ selectedNoteId: null });
      await get().fetchNotes();
    } catch {
      // silently fail
    }
  },

  restoreNote: async (id) => {
    try {
      await api.post(`/notes/${id}/restore`, {});
      await get().fetchNotes();
    } catch {
      // silently fail
    }
  },

  permanentDeleteNote: async (id) => {
    try {
      await api.delete(`/notes/${id}/permanent`);
      const { selectedNoteId } = get();
      if (selectedNoteId === id) set({ selectedNoteId: null });
      await get().fetchNotes();
    } catch {
      // silently fail
    }
  },

  promoteNote: async (id) => {
    try {
      await api.post(`/notes/${id}/promote`, {});
      await get().fetchNotes();
    } catch {
      // silently fail
    }
  },
}));
