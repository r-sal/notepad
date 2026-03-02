import { useCallback, useEffect, useRef, useState } from "react";
import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Link from "@tiptap/extension-link";
import CodeBlock from "@tiptap/extension-code-block";
import Placeholder from "@tiptap/extension-placeholder";
import { useNoteStore } from "../stores/noteStore";

function Toolbar({ editor }: { editor: ReturnType<typeof useEditor> }) {
  if (!editor) return null;

  return (
    <div className="editor-toolbar">
      <button
        onClick={() => editor.chain().focus().toggleBold().run()}
        className={editor.isActive("bold") ? "is-active" : ""}
        title="Bold"
      >
        <strong>B</strong>
      </button>
      <button
        onClick={() => editor.chain().focus().toggleItalic().run()}
        className={editor.isActive("italic") ? "is-active" : ""}
        title="Italic"
      >
        <em>I</em>
      </button>
      <button
        onClick={() => editor.chain().focus().toggleStrike().run()}
        className={editor.isActive("strike") ? "is-active" : ""}
        title="Strikethrough"
      >
        <s>S</s>
      </button>
      <button
        onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
        className={editor.isActive("heading", { level: 1 }) ? "is-active" : ""}
        title="Heading 1"
      >
        H1
      </button>
      <button
        onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
        className={editor.isActive("heading", { level: 2 }) ? "is-active" : ""}
        title="Heading 2"
      >
        H2
      </button>
      <button
        onClick={() => editor.chain().focus().toggleBulletList().run()}
        className={editor.isActive("bulletList") ? "is-active" : ""}
        title="Bullet list"
      >
        •&mdash;
      </button>
      <button
        onClick={() => editor.chain().focus().toggleOrderedList().run()}
        className={editor.isActive("orderedList") ? "is-active" : ""}
        title="Ordered list"
      >
        1.
      </button>
      <button
        onClick={() => editor.chain().focus().toggleBlockquote().run()}
        className={editor.isActive("blockquote") ? "is-active" : ""}
        title="Quote"
      >
        &ldquo;
      </button>
      <button
        onClick={() => editor.chain().focus().toggleCodeBlock().run()}
        className={editor.isActive("codeBlock") ? "is-active" : ""}
        title="Code block"
      >
        {"</>"}
      </button>
    </div>
  );
}

export default function NoteEditor() {
  const { notes, selectedNoteId, updateNote, trashNote, restoreNote, permanentDeleteNote, promoteNote } =
    useNoteStore();
  const note = notes.find((n) => n.id === selectedNoteId);
  const [title, setTitle] = useState("");
  const saveTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const isUpdatingRef = useRef(false);

  const debouncedSave = useCallback(
    (field: "title" | "body", value: string) => {
      if (!selectedNoteId) return;
      if (saveTimeoutRef.current) clearTimeout(saveTimeoutRef.current);
      saveTimeoutRef.current = setTimeout(() => {
        isUpdatingRef.current = true;
        updateNote(selectedNoteId, { [field]: value }).then(() => {
          isUpdatingRef.current = false;
        });
      }, 500);
    },
    [selectedNoteId, updateNote],
  );

  const editor = useEditor({
    extensions: [
      StarterKit.configure({ codeBlock: false }),
      CodeBlock,
      Link.configure({ openOnClick: true }),
      Placeholder.configure({ placeholder: "Start writing..." }),
    ],
    content: "",
    onUpdate: ({ editor: ed }) => {
      debouncedSave("body", ed.getHTML());
    },
  });

  // Sync editor content when switching notes
  useEffect(() => {
    if (!note) return;
    setTitle(note.title);
    if (editor && !isUpdatingRef.current) {
      const currentContent = editor.getHTML();
      if (currentContent !== note.body) {
        editor.commands.setContent(note.body || "", false);
      }
    }
  }, [note?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  if (!note) {
    return (
      <div className="editor-pane">
        <div className="editor-empty">Select a note or create a new one</div>
      </div>
    );
  }

  const handleTitleChange = (value: string) => {
    setTitle(value);
    debouncedSave("title", value);
  };

  const handleStar = () => {
    updateNote(note.id, { is_starred: !note.is_starred });
  };

  return (
    <div className="editor-pane">
      {note.is_trashed && (
        <div className="trash-bar">
          <span>This note is in the trash.</span>
          <button className="btn-restore" onClick={() => restoreNote(note.id)}>
            Restore
          </button>
          <button
            className="btn-delete-forever"
            onClick={() => permanentDeleteNote(note.id)}
          >
            Delete forever
          </button>
        </div>
      )}

      {note.is_temporary && !note.is_trashed && (
        <div className="temp-bar">
          <span>This is a scratchpad note.</span>
          <button className="btn-promote" onClick={() => promoteNote(note.id)}>
            Promote to Note
          </button>
        </div>
      )}

      <Toolbar editor={editor} />

      <div className="editor-toolbar" style={{ borderBottom: "none", paddingBottom: 0 }}>
        <div className="spacer" />
        <div className="note-actions">
          {!note.is_trashed && (
            <>
              {note.is_temporary && (
                <button onClick={() => promoteNote(note.id)} title="Promote to regular note">
                  📤
                </button>
              )}
              <button onClick={handleStar} title={note.is_starred ? "Unstar" : "Star"}>
                {note.is_starred ? "⭐" : "☆"}
              </button>
              <button onClick={() => trashNote(note.id)} title="Move to trash">
                🗑️
              </button>
            </>
          )}
        </div>
      </div>

      <div className="editor-title">
        <input
          value={title}
          onChange={(e) => handleTitleChange(e.target.value)}
          placeholder="Untitled"
          disabled={note.is_trashed}
        />
      </div>

      <div className="editor-content">
        <EditorContent editor={editor} />
      </div>
    </div>
  );
}
