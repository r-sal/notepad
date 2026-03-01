import { create } from "zustand";
import { api } from "../services/api";
import type { Folder } from "../types";

interface FolderState {
  folders: Folder[];
  isLoading: boolean;

  fetchFolders: () => Promise<void>;
  createFolder: (name: string, parentId?: string) => Promise<Folder | null>;
  renameFolder: (id: string, name: string) => Promise<void>;
  deleteFolder: (id: string) => Promise<void>;
}

export const useFolderStore = create<FolderState>((set, get) => ({
  folders: [],
  isLoading: false,

  fetchFolders: async () => {
    set({ isLoading: true });
    try {
      const data = await api.get<Folder[]>("/folders");
      set({ folders: data, isLoading: false });
    } catch {
      set({ folders: [], isLoading: false });
    }
  },

  createFolder: async (name, parentId) => {
    try {
      const payload: Record<string, string> = { name };
      if (parentId) payload.parent_id = parentId;
      const folder = await api.post<Folder>("/folders", payload);
      await get().fetchFolders();
      return folder;
    } catch {
      return null;
    }
  },

  renameFolder: async (id, name) => {
    try {
      await api.put(`/folders/${id}`, { name });
      await get().fetchFolders();
    } catch {
      // silently fail
    }
  },

  deleteFolder: async (id) => {
    try {
      await api.delete(`/folders/${id}`);
      await get().fetchFolders();
    } catch {
      // silently fail
    }
  },
}));
