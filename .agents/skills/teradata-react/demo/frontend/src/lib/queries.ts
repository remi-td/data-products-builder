import { useQuery } from "@tanstack/react-query";
import { api } from "./api";

export type Health = { status: string; database: string };
export type Overview = {
  database_count: number;
  table_count: number;
  user_count: number;
  total_perm_bytes: number;
};
export type DatabaseRow = {
  databasename: string;
  ownername: string | null;
  permspace: number;
  spoolspace: number;
  tempspace: number;
};
export type TableRow = {
  databasename: string;
  tablename: string;
  tablekind: string;
  createtimestamp: string | null;
};
export type UserRow = {
  username: string;
  createtimestamp: string | null;
  lastaltertimestamp: string | null;
  ownername: string | null;
};
export type SpaceByDatabase = {
  databasename: string;
  currentperm: number;
  maxperm: number;
};

export const useHealth = () =>
  useQuery({ queryKey: ["health"], queryFn: () => api<Health>("/api/health"), staleTime: 30_000 });

export const useOverview = () =>
  useQuery({ queryKey: ["overview"], queryFn: () => api<Overview>("/api/overview") });

export const useDatabases = (limit = 200) =>
  useQuery({
    queryKey: ["databases", limit],
    queryFn: () => api<DatabaseRow[]>(`/api/databases?limit=${limit}`),
  });

export const useTablesByDatabase = (database: string, limit = 500) =>
  useQuery({
    queryKey: ["tables", database, limit],
    queryFn: () =>
      api<TableRow[]>(`/api/tables?database=${encodeURIComponent(database)}&limit=${limit}`),
    enabled: database.length > 0,
  });

export const useUsers = (limit = 200) =>
  useQuery({
    queryKey: ["users", limit],
    queryFn: () => api<UserRow[]>(`/api/users?limit=${limit}`),
  });

export const useSpaceByDatabase = (limit = 20) =>
  useQuery({
    queryKey: ["space", "by-database", limit],
    queryFn: () => api<SpaceByDatabase[]>(`/api/space/by-database?limit=${limit}`),
  });
