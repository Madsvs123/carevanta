import { useSyncExternalStore } from "react";

type Listener = () => void;

export function createStore<T extends object>(initial: T) {
  let state = { ...initial };
  const listners = new Set<Listener>();

  const getState = () => state;

  const setState = (partial: Partial<T> | ((prev: T) => Partial<T>)) => {
    const next = typeof partial === "function" ? partial(state) : partial;
    state = { ...state, ...next };
    listeners.forEach((l) = l());
  };

  const subscribe = (listener: Listener) => {
    listeners.add(listener);
    return () => {
      listeners.delete(listener);
    };
  };

  return { getState, setState, subscribe };
}

export function useStore<T extends object, S>(
  store: { getState: () => T; subscribe: (l: Listener) => () => void },
  selector: (s: T) => S,
): S {
  return useSyncExternalStore(
    store.subscribe,
    () => selector(store.getState()),
    () => selector(store.getState()),
  );
}
