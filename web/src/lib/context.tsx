import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import type { ReactNode } from "react";
import { accounts } from "./data";
import { readableError, request } from "./api";
import type { Account, ClaimStatus, Post, ServiceStatus } from "./types";

function storedSet(name: string): Set<string> {
  try {
    const value = JSON.parse(localStorage.getItem(name) ?? "[]");
    return new Set(
      Array.isArray(value) ? value.filter((v) => typeof v === "string") : [],
    );
  } catch {
    return new Set();
  }
}
function useStoredSet(name: string) {
  const [value, setValue] = useState(() => storedSet(name));
  const toggle = useCallback(
    (id: string) =>
      setValue((previous) => {
        const next = new Set(previous);
        next.has(id) ? next.delete(id) : next.add(id);
        localStorage.setItem(name, JSON.stringify([...next]));
        return next;
      }),
    [name],
  );
  return [value, toggle] as const;
}
interface AppState {
  user: Account;
  setUser: (account: Account) => void;
  statuses: Record<string, ClaimStatus>;
  service?: ServiceStatus;
  connectionError: string;
  refresh: () => Promise<void>;
  report: Account | null;
  setReport: (account: Account | null) => void;
  liked: Set<string>;
  saved: Set<string>;
  following: Set<string>;
  toggleLike: (id: string) => void;
  toggleSave: (id: string) => void;
  toggleFollow: (id: string) => void;
  comments: Record<string, string[]>;
  addComment: (id: string, text: string) => void;
  addedPosts: Post[];
  addPost: (post: Post) => void;
  notify: (text: string) => void;
}
const AppContext = createContext<AppState | null>(null);
export function AppProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState(accounts[0]);
  const [statuses, setStatuses] = useState<Record<string, ClaimStatus>>({});
  const [service, setService] = useState<ServiceStatus>();
  const [connectionError, setConnectionError] = useState("");
  const [report, setReport] = useState<Account | null>(null);
  const [toast, setToast] = useState<{ text: string; id: number } | null>(null);
  const [liked, toggleLike] = useStoredSet("ig-likes");
  const [saved, toggleSave] = useStoredSet("ig-saved");
  const [following, toggleFollow] = useStoredSet("ig-following");
  const [comments, setComments] = useState<Record<string, string[]>>({});
  const [addedPosts, setAddedPosts] = useState<Post[]>([]);
  const refresh = useCallback(async () => {
    try {
      const [states, status] = await Promise.all([
        request<Record<string, ClaimStatus>>("/statuses"),
        request<ServiceStatus>("/analysis/status"),
      ]);
      setStatuses(states);
      setService(status);
      setConnectionError("");
    } catch (error) {
      setConnectionError(readableError(error));
    }
  }, []);
  useEffect(() => {
    void refresh();
  }, [refresh]);
  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => setToast(null), 4200);
    return () => clearTimeout(timer);
  }, [toast]);
  const notify = useCallback(
    (text: string) => setToast({ text, id: Date.now() }),
    [],
  );
  const addComment = useCallback(
    (id: string, text: string) =>
      setComments((old) => ({ ...old, [id]: [...(old[id] ?? []), text] })),
    [],
  );
  const addPost = useCallback(
    (post: Post) => setAddedPosts((old) => [post, ...old]),
    [],
  );
  const value = useMemo(
    () => ({
      user,
      setUser,
      statuses,
      service,
      connectionError,
      refresh,
      report,
      setReport,
      liked,
      saved,
      following,
      toggleLike,
      toggleSave,
      toggleFollow,
      comments,
      addComment,
      addedPosts,
      addPost,
      notify,
    }),
    [
      user,
      statuses,
      service,
      connectionError,
      refresh,
      report,
      liked,
      saved,
      following,
      toggleLike,
      toggleSave,
      toggleFollow,
      comments,
      addComment,
      addedPosts,
      addPost,
      notify,
    ],
  );
  return (
    <AppContext.Provider value={value}>
      {children}
      {toast && (
        <div className="toast" role="status">
          {toast.text}
        </div>
      )}
    </AppContext.Provider>
  );
}
export function useApp() {
  const context = useContext(AppContext);
  if (!context) throw new Error("AppProvider required");
  return context;
}
