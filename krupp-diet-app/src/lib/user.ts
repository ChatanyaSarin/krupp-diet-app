export function saveUsername(u: string) {
  if (typeof window !== "undefined" && u) localStorage.setItem("username", u);
}

export function readUsername(search?: URLSearchParams | string): string {
  let fromQS = "";
  if (search) {
    const sp = typeof search === "string" ? new URLSearchParams(search) : search;
    fromQS = sp.get("username") ?? "";
  }
  if (fromQS) return fromQS;
  if (typeof window !== "undefined") return localStorage.getItem("username") || "";
  return "";
}