import { create } from "zustand";

interface UIState {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  selectedResumeId: string | null;
  setSelectedResumeId: (id: string | null) => void;
}

export const useStore = create<UIState>((set) => ({
  sidebarOpen: false,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  selectedResumeId: null,
  setSelectedResumeId: (id) => set({ selectedResumeId: id }),
}));
