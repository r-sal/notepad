import { useEffect } from "react";
import { useFolderStore } from "../stores/folderStore";
import { useNoteStore } from "../stores/noteStore";
import { useKeyboardShortcuts } from "../hooks/useKeyboardShortcuts";
import NoteEditor from "./NoteEditor";
import NoteList from "./NoteList";
import Sidebar from "./Sidebar";

export default function Layout() {
  const fetchNotes = useNoteStore((s) => s.fetchNotes);
  const fetchFolders = useFolderStore((s) => s.fetchFolders);
  useKeyboardShortcuts();

  useEffect(() => {
    fetchNotes();
    fetchFolders();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="app-layout">
      <Sidebar />
      <NoteList />
      <NoteEditor />
    </div>
  );
}
