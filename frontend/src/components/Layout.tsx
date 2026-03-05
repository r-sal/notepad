import { useCallback, useEffect, useState } from "react";
import { useFolderStore } from "../stores/folderStore";
import { useNoteStore } from "../stores/noteStore";
import { useKeyboardShortcuts } from "../hooks/useKeyboardShortcuts";
import NoteEditor from "./NoteEditor";
import NoteList from "./NoteList";
import Sidebar from "./Sidebar";

const SIDEBAR_BP = 900;
const NOTELIST_BP = 700;

export default function Layout() {
  const fetchNotes = useNoteStore((s) => s.fetchNotes);
  const fetchFolders = useFolderStore((s) => s.fetchFolders);
  useKeyboardShortcuts();

  const [sidebarCollapsed, setSidebarCollapsed] = useState(
    () => window.innerWidth <= SIDEBAR_BP,
  );
  const [notelistCollapsed, setNotelistCollapsed] = useState(
    () => window.innerWidth <= NOTELIST_BP,
  );

  // Auto-collapse/expand on window resize via matchMedia
  useEffect(() => {
    const sidebarMq = window.matchMedia(`(max-width: ${SIDEBAR_BP}px)`);
    const notelistMq = window.matchMedia(`(max-width: ${NOTELIST_BP}px)`);

    const handleSidebar = (e: MediaQueryListEvent) => setSidebarCollapsed(e.matches);
    const handleNotelist = (e: MediaQueryListEvent) => setNotelistCollapsed(e.matches);

    sidebarMq.addEventListener("change", handleSidebar);
    notelistMq.addEventListener("change", handleNotelist);

    return () => {
      sidebarMq.removeEventListener("change", handleSidebar);
      notelistMq.removeEventListener("change", handleNotelist);
    };
  }, []);

  useEffect(() => {
    fetchNotes();
    fetchFolders();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const toggleSidebar = useCallback(() => setSidebarCollapsed((v) => !v), []);
  const toggleNotelist = useCallback(() => setNotelistCollapsed((v) => !v), []);

  const collapseNotelist = useCallback(() => {
    if (window.innerWidth <= NOTELIST_BP) {
      setNotelistCollapsed(true);
    }
  }, []);

  const classes = [
    "app-layout",
    sidebarCollapsed ? "sidebar-collapsed" : "",
    notelistCollapsed ? "notelist-collapsed" : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={classes}>
      <Sidebar collapsed={sidebarCollapsed} onToggle={toggleSidebar} />
      <NoteList collapsed={notelistCollapsed} onToggle={toggleNotelist} onNoteSelect={collapseNotelist} />
      <NoteEditor />
    </div>
  );
}
