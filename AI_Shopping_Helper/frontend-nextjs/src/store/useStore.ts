import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface SearchState {
  recentSearches: string[]
  addRecentSearch: (query: string) => void
  clearRecentSearches: () => void
}

export const useSearchStore = create<SearchState>()(
  persist(
    (set) => ({
      recentSearches: [],
      addRecentSearch: (query: string) =>
        set((state) => ({
          recentSearches: [
            query,
            ...state.recentSearches.filter((s) => s !== query),
          ].slice(0, 10),
        })),
      clearRecentSearches: () => set({ recentSearches: [] }),
    }),
    {
      name: 'search-storage',
    }
  )
)

interface FavoritesState {
  favorites: string[]
  toggleFavorite: (productId: string) => void
  isFavorite: (productId: string) => boolean
  clearFavorites: () => void
}

export const useFavoritesStore = create<FavoritesState>()(
  persist(
    (set, get) => ({
      favorites: [],
      toggleFavorite: (productId: string) =>
        set((state) => ({
          favorites: state.favorites.includes(productId)
            ? state.favorites.filter((id) => id !== productId)
            : [...state.favorites, productId],
        })),
      isFavorite: (productId: string) => get().favorites.includes(productId),
      clearFavorites: () => set({ favorites: [] }),
    }),
    {
      name: 'favorites-storage',
    }
  )
)
