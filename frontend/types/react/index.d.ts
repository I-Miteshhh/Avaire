declare module "react" {
  export type ReactNode = any;
  export type FC<P = {}> = (props: P & { children?: ReactNode }) => JSX.Element | null;
  export const useMemo: <T>(factory: () => T, deps: unknown[]) => T;
  export const useCallback: <T extends (...args: any[]) => unknown>(fn: T, deps: unknown[]) => T;
  export const useEffect: (effect: () => void | (() => void), deps?: unknown[]) => void;
  export const useState: <S>(initial: S) => [S, (value: S) => void];
  export const useRef: <T>(initial: T) => { current: T };
  export const useContext: (context: unknown) => unknown;
  export const useReducer: (...args: unknown[]) => unknown;
  export const useTransition: () => [boolean, (callback: () => void) => void];
  export const useSyncExternalStore: (...args: unknown[]) => unknown;
  export interface Context<T> {
    Provider: FC<{ value: T }>;
    Consumer: FC<{ children: (value: T) => ReactNode }>;
  }
  export function createContext<T>(defaultValue: T): Context<T>;
  export function createElement(type: any, props?: any, ...children: any[]): any;
  const React: {
    createElement: typeof createElement;
    useState: typeof useState;
  };
  export default React;
}

declare global {
  namespace JSX {
    interface Element {}
    interface IntrinsicElements {
      [elemName: string]: any;
    }
  }
}

declare module "react/jsx-runtime" {
  export const jsx: (...args: any[]) => any;
  export const jsxs: (...args: any[]) => any;
  export const Fragment: unique symbol;
}
