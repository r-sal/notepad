import { useCallback, useEffect, useState } from "react";
import { useFolderStore } from "../stores/folderStore";
import { useNoteStore } from "../stores/noteStore";
import { useKeyboardShortcuts } from "../hooks/useKeyboardShortcuts";
import NoteEditor from "./NoteEditor";
import NoteList from "./NoteList";
import Sidebar from "./Sidebar";

const PANELS_BP = 900;

export default function Layout() {
  const fetchNotes = useNoteStore((s) => s.fetchNotes);
  const fetchFolders = useFolderStore((s) => s.fetchFolders);
  useKeyboardShortcuts();

  const [panelsCollapsed, setPanelsCollapsed] = useState(
    () => window.innerWidth <= PANELS_BP,
  );

  // Auto-collapse/expand on window resize via matchMedia
  useEffect(() => {
    const mq = window.matchMedia(`(max-width: ${PANELS_BP}px)`);
    const handler = (e: MediaQueryListEvent) => setPanelsCollapsed(e.matches);
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, []);

  useEffect(() => {
    fetchNotes();
    fetchFolders();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const togglePanels = useCallback(() => setPanelsCollapsed((v) => !v), []);

  const collapsePanels = useCallback(() => {
    if (window.innerWidth <= PANELS_BP) {
      setPanelsCollapsed(true);
    }
  }, []);

  return (
    <div className={`app-layout${panelsCollapsed ? " panels-collapsed" : ""}`}>
      <Sidebar collapsed={panelsCollapsed} onToggle={togglePanels} />
      <NoteList onNoteSelect={collapsePanels} />
      <NoteEditor />
    </div>
  );
}
