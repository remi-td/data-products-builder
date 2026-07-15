import { useQuery } from "@tanstack/react-query";
import { api } from "./api";

export type Health = { status: string; database: string };

export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: () => api<Health>("/api/health"),
    staleTime: 30_000,
  });
}

// Add additional hooks here, one per backend endpoint.
