import { useState, type KeyboardEvent } from "react";
import { useAuthStore } from "../stores/authStore";
import { useFolderStore } from "../stores/folderStore";
import { useNoteStore } from "../stores/noteStore";
import type { Folder } from "../types";

function FolderItem({
  folder,
  depth = 0,
}: {
  folder: Folder;
  depth?: number;
}) {
  const activeFolderId = useNoteStore((s) => s.activeFolderId);
  const setActiveFolderId = useNoteStore((s) => s.setActiveFolderId);
  const [expanded, setExpanded] = useState(true);
  const hasChildren = folder.children && folder.children.length > 0;

  return (
    <div>
      <button
        className={`sidebar-item${activeFolderId === folder.id ? " active" : ""}`}
        style={{ paddingLeft: 8 + depth * 16 }}
        onClick={() => setActiveFolderId(folder.id)}
      >
        <span className="icon" onClick={(e) => {
          if (hasChildren) { e.stopPropagation(); setExpanded(!expanded); }
        }}>
          {hasChildren ? (expanded ? "▼" : "▶") : "📁"}
        </span>
        <span className="label">{folder.name}</span>
      </button>
      {hasChildren && expanded && (
        <div>
          {folder.children!.map((child) => (
            <FolderItem key={child.id} folder={child} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function Sidebar() {
  const logout = useAuthStore((s) => s.logout);
  const { folders, createFolder } = useFolderStore();
  const { viewFilter, setViewFilter, activeFolderId, setActiveFolderId } = useNoteStore();
  const [showNewFolder, setShowNewFolder] = useState(false);
  const [newFolderName, setNewFolderName] = useState("");

  const handleCreateFolder = async () => {
    const name = newFolderName.trim();
    if (!name) return;
    await createFolder(name);
    setNewFolderName("");
    setShowNewFolder(false);
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === "Enter") handleCreateFolder();
    if (e.key === "Escape") { setShowNewFolder(false); setNewFolderName(""); }
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>Notepad</h2>
      </div>

      {/* Virtual folders */}
      <div className="sidebar-section">
        <button
          className={`sidebar-item${viewFilter === "all" && !activeFolderId ? " active" : ""}`}
          onClick={() => { setViewFilter("all"); setActiveFolderId(null); }}
        >
          <span className="icon">📝</span>
          <span className="label">All Notes</span>
        </button>
        <button
          className={`sidebar-item${viewFilter === "starred" ? " active" : ""}`}
          onClick={() => setViewFilter("starred")}
        >
          <span className="icon">⭐</span>
          <span className="label">Starred</span>
        </button>
        <button
          className={`sidebar-item${viewFilter === "temporary" ? " active" : ""}`}
          onClick={() => setViewFilter("temporary")}
        >
          <span className="icon">📋</span>
          <span className="label">Scratchpad</span>
        </button>
        <button
          className={`sidebar-item${viewFilter === "trash" ? " active" : ""}`}
          onClick={() => setViewFilter("trash")}
        >
          <span className="icon">🗑️</span>
          <span className="label">Trash</span>
        </button>
      </div>

      {/* Folders */}
      <div className="sidebar-section">
        <div className="sidebar-section-title" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span>Folders</span>
          <button
            className="btn-icon"
            style={{ width: 20, height: 20, fontSize: 14 }}
            onClick={() => setShowNewFolder(true)}
            title="New folder"
          >
            +
          </button>
        </div>
        {showNewFolder && (
          <div className="new-folder-input">
            <input
              value={newFolderName}
              onChange={(e) => setNewFolderName(e.target.value)}
              onKeyDown={handleKeyDown}
              onBlur={() => { if (!newFolderName.trim()) setShowNewFolder(false); }}
              placeholder="Folder name"
              autoFocus
            />
          </div>
        )}
        {folders.map((folder) => (
          <FolderItem key={folder.id} folder={folder} />
        ))}
      </div>

      {/* Footer */}
      <div className="sidebar-footer">
        <button onClick={logout}>Sign out</button>
      </div>
    </div>
  );
}
