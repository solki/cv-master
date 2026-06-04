import { create } from "zustand";

interface UIState {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  selectedResumeId: string | null;
  setSelectedResumeId: (id: string | null) => void;
}

export const useStore = create<UIState>((set) => ({
  sidebarOpen: true,
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
  selectedResumeId: null,
  setSelectedResumeId: (id) => set({ selectedResumeId: id }),
}));
