# UI Test Plan — Playwright E2E Tests

This document defines the end-to-end test cases to be implemented with Playwright. Each test simulates real user interactions in the browser against the running application.

---

## 1. Authentication

### 1.1 Registration
| # | Test Case | Steps | Expected Result |
|---|-----------|-------|-----------------|
| 1 | Successful registration | Fill email + password + confirm, click "Create account" | Redirected to main app, three-panel layout visible |
| 2 | Password mismatch | Fill mismatched password and confirm, submit | Error: "Passwords do not match" |
| 3 | Short password | Enter password with fewer than 8 characters, submit | Error: "Password must be at least 8 characters" |
| 4 | Duplicate email | Register with an already-used email | Error: "Registration failed. Email may already be in use." |
| 5 | Invalid email format | Enter "notanemail", submit | Browser validation prevents submission |
| 6 | Navigate to login | Click "Sign in" link | Navigated to /login |

### 1.2 Login
| # | Test Case | Steps | Expected Result |
|---|-----------|-------|-----------------|
| 7 | Successful login | Enter valid credentials, click "Sign in" | Redirected to main app |
| 8 | Wrong password | Enter valid email with wrong password | Error: "Invalid email or password" |
| 9 | Nonexistent user | Enter unregistered email | Error: "Invalid email or password" |
| 10 | Navigate to register | Click "Create one" link | Navigated to /register |

### 1.3 Session
| # | Test Case | Steps | Expected Result |
|---|-----------|-------|-----------------|
| 11 | Persist session on reload | Log in, reload page | Still authenticated, main app loads |
| 12 | Sign out | Click "Sign out" in sidebar | Redirected to /login, localStorage cleared |
| 13 | Protected route redirect | Navigate to / without auth | Redirected to /login |
| 14 | Public route redirect | Navigate to /login while authenticated | Redirected to / |

---

## 2. Notes — CRUD

### 2.1 Create
| # | Test Case | Steps | Expected Result |
|---|-----------|-------|-----------------|
| 15 | Create note via button | Click ✏️ button in note list header | New "Untitled" note appears at top of list, selected in editor |
| 16 | Create note via keyboard | Press Cmd+N | New "Untitled" note created and selected |
| 17 | Default values | Create note, inspect editor | Title: "Untitled", body: empty with "Start writing..." placeholder |

### 2.2 Edit
| # | Test Case | Steps | Expected Result |
|---|-----------|-------|-----------------|
| 18 | Edit title | Click title input, clear and type new title, wait 1s | Note list updates with new title |
| 19 | Edit body | Click editor area, type text, wait 1s | Note list preview updates with new body text |
| 20 | Auto-save persists | Edit title, reload page | Edited title persists after reload |
| 21 | Rich text — bold | Select text, click B toolbar button | Text appears bold |
| 22 | Rich text — italic | Select text, click I toolbar button | Text appears italic |
| 23 | Rich text — heading | Place cursor, click H1 button, type text | Text renders as heading |
| 24 | Rich text — bullet list | Click bullet list button, type items | Bullet list renders |
| 25 | Rich text — code block | Click </> button, type code | Code block renders with monospace font |

### 2.3 Read / Select
| # | Test Case | Steps | Expected Result |
|---|-----------|-------|-----------------|
| 26 | Select note from list | Click a note in the note list | Editor loads that note's title and body |
| 27 | Switch between notes | Click note A, then click note B | Editor content changes to note B |
| 28 | Auto-select first note | Create two notes, reload page | First note in list is auto-selected |

---

## 3. Notes — Star

| # | Test Case | Steps | Expected Result |
|---|-----------|-------|-----------------|
| 29 | Star a note | Click ☆ button in editor | Icon changes to ⭐, star emoji appears in note list |
| 30 | Unstar a note | Click ⭐ button on a starred note | Icon reverts to ☆, star removed from list |
| 31 | Star via keyboard | Press Cmd+Shift+S | Star toggles on selected note |
| 32 | Starred view shows only starred | Star one note, click "Starred" in sidebar | Only starred notes visible in list |
| 33 | Starred view excludes unstarred | Have starred and unstarred notes, open Starred view | Unstarred notes not shown |

---

## 4. Notes — Trash & Restore

### 4.1 Soft Delete
| # | Test Case | Steps | Expected Result |
|---|-----------|-------|-----------------|
| 34 | Trash via button | Click 🗑️ in editor | Note removed from All Notes, editor shows empty state |
| 35 | Trash via keyboard | Select note, press Cmd+Backspace (not in editor) | Note moved to trash |
| 36 | Trashed note appears in Trash | Trash a note, click "Trash" in sidebar | Trashed note visible in trash list |
| 37 | Trashed note hidden from All Notes | Trash a note, go to All Notes | Trashed note not visible |
| 38 | No create button in Trash | Navigate to Trash view | ✏️ button is not present |

### 4.2 Trash Bar
| # | Test Case | Steps | Expected Result |
|---|-----------|-------|-----------------|
| 39 | Trash bar visible | Click a trashed note in Trash view | Orange bar with "This note is in the trash.", Restore and Delete forever buttons |
| 40 | No star/trash actions on trashed note | View trashed note | Star and trash buttons are hidden |

### 4.3 Restore
| # | Test Case | Steps | Expected Result |
|---|-----------|-------|-----------------|
| 41 | Restore note | Click "Restore" on trash bar | Note removed from Trash, reappears in All Notes |
| 42 | Restored note is accessible | Restore a note, go to All Notes, click it | Note content is intact |

### 4.4 Permanent Delete
| # | Test Case | Steps | Expected Result |
|---|-----------|-------|-----------------|
| 43 | Delete forever | Click "Delete forever" on trash bar | Note removed from Trash, gone permanently |
| 44 | Permanent delete is irreversible | Delete forever, check All Notes and Trash | Note does not appear anywhere |

---

## 5. Folders

### 5.1 Create
| # | Test Case | Steps | Expected Result |
|---|-----------|-------|-----------------|
| 45 | Create folder | Click "+" next to FOLDERS, type name, press Enter | Folder appears in sidebar |
| 46 | Cancel folder creation | Click "+", press Escape | Input disappears, no folder created |
| 47 | Empty name rejected | Click "+", press Enter without typing | No folder created |

### 5.2 Navigate
| # | Test Case | Steps | Expected Result |
|---|-----------|-------|-----------------|
| 48 | Click folder filters notes | Create folder, add a note to it, click folder | Only that folder's notes shown, header shows "Folder" |
| 49 | Empty folder | Click a folder with no notes | "No notes yet" message displayed |
| 50 | Create note inside folder | Select a folder, click ✏️ | New note is created with that folder_id |
| 51 | Back to All Notes | Click folder, then click "All Notes" | All non-trashed notes visible again |

### 5.3 Folder Tree
| # | Test Case | Steps | Expected Result |
|---|-----------|-------|-----------------|
| 52 | Nested folders display | Create parent folder, create child inside it (via API) | Tree shows parent with indented child |
| 53 | Expand/collapse | Click arrow on parent folder with children | Children toggle visibility |

---

## 6. Search

| # | Test Case | Steps | Expected Result |
|---|-----------|-------|-----------------|
| 54 | Search by title | Type a word from a note's title into search | Only matching notes shown |
| 55 | Search by body | Type a word from a note's body into search | Only matching notes shown |
| 56 | No results | Type a term that matches nothing | "No matching notes" message |
| 57 | Clear search | Search for something, clear the input | All notes shown again |
| 58 | Search is debounced | Type quickly, observe network | Only one API call after typing stops |
| 59 | Focus search via keyboard | Press Cmd+Shift+F | Search input is focused and selected |

---

## 7. Keyboard Shortcuts

| # | Test Case | Steps | Expected Result |
|---|-----------|-------|-----------------|
| 60 | Cmd+N creates note | Press Cmd+N | New note created and selected |
| 61 | Cmd+Shift+F focuses search | Press Cmd+Shift+F | Search input focused |
| 62 | Cmd+Backspace trashes note | Select note (not in editor), press Cmd+Backspace | Note moved to trash |
| 63 | Cmd+Shift+S toggles star | Press Cmd+Shift+S | Star toggles on selected note |
| 64 | Arrow Up/Down navigates list | Press ArrowDown, then ArrowUp | Selected note changes in list |
| 65 | Escape blurs editor | Focus search, press Escape | Search input loses focus |
| 66 | Shortcuts disabled while editing | Focus title input, press Cmd+Backspace | Note is NOT trashed (shortcut suppressed) |

---

## 8. Layout & Responsiveness

| # | Test Case | Steps | Expected Result |
|---|-----------|-------|-----------------|
| 67 | Three-panel layout | Log in | Sidebar (220px), Note List (300px), Editor (flex) all visible |
| 68 | Sidebar virtual folders | Inspect sidebar | "All Notes", "Starred", "Trash" with icons visible |
| 69 | Empty state — no notes | New user with no notes | "No notes yet" in list, "Select a note or create a new one" in editor |
| 70 | Empty state — no selection | Deselect all notes | "Select a note or create a new one" in editor |

---

## 9. User Isolation

| # | Test Case | Steps | Expected Result |
|---|-----------|-------|-----------------|
| 71 | Notes isolated between users | Create note as User A, log out, log in as User B | User B does not see User A's notes |
| 72 | Folders isolated between users | Create folder as User A, log in as User B | User B does not see User A's folders |
| 73 | Search isolated | User A creates note "Secret", User B searches "Secret" | No results for User B |

---

## Test Infrastructure Notes

- **Framework**: Playwright with TypeScript
- **Base URL**: `http://localhost:5173`
- **API proxy**: Vite proxies `/api` to backend at `http://backend:8000`
- **Test database**: Use a dedicated test database or reset state between test suites
- **Auth helpers**: Create reusable `login()` and `register()` page object methods
- **Suggested structure**:
  ```
  tests/
    e2e/
      auth.spec.ts          (tests 1-14)
      notes-crud.spec.ts    (tests 15-28)
      notes-star.spec.ts    (tests 29-33)
      notes-trash.spec.ts   (tests 34-44)
      folders.spec.ts       (tests 45-53)
      search.spec.ts        (tests 54-59)
      shortcuts.spec.ts     (tests 60-66)
      layout.spec.ts        (tests 67-70)
      isolation.spec.ts     (tests 71-73)
    fixtures/
      auth.ts               (login/register helpers)
      notes.ts              (create note helper)
      folders.ts            (create folder helper)
  ```
