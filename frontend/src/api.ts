import axios from "axios";

const BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export const api = axios.create({
  baseURL: BASE,
  headers: { "Content-Type": "application/json" },
  timeout: 30000,
});

export async function postQuery(payload: any) {
  const res = await api.post("/api/analysis/query/", payload);
  return res.data;
}

export async function uploadFile(file: File) {
  const fd = new FormData();
  fd.append("file", file);
  const res = await api.post("/api/analysis/upload/", fd, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}
