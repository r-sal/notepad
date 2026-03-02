export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface Note {
  id: string;
  title: string;
  body: string;
  folder_id: string | null;
  user_id: string;
  is_starred: boolean;
  is_trashed: boolean;
  is_temporary: boolean;
  trashed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Folder {
  id: string;
  name: string;
  parent_id: string | null;
  user_id: string;
  sort_order: number;
  created_at: string;
  updated_at: string;
  children?: Folder[];
}
