// Minimal React type fallbacks for environments without node_modules.
declare module "react" {
  export type ReactNode = any;
  export type ReactElement = any;
  export interface FC<P = {}> {
    (props: P & { children?: ReactNode }): ReactElement | null;
  }
  export interface MutableRefObject<T> {
    current: T;
  }
  export type Dispatch<A = any> = (value: A) => void;
  export type SetStateAction<S> = S | ((prevState: S) => S);
  export type ChangeEvent<T = any> = { target: T };
  export type FormEvent<T = any> = { target: T; preventDefault(): void };

  export function createContext<T>(defaultValue: T): any;
  export function useContext<T>(context: any): T;
  export function useMemo<T>(factory: () => T, deps: any[]): T;
  export function useState<S>(initialState: S | (() => S)): [S, Dispatch<SetStateAction<S>>];
  export function useEffect(effect: () => void | (() => void), deps?: any[]): void;
  export function useRef<T>(initialValue: T): MutableRefObject<T>;
  export function useCallback<T extends (...args: any[]) => any>(fn: T, deps: any[]): T;
  export function useTransition(): [boolean, (fn: () => void) => void];
  export function useReducer<R extends (...args: any[]) => any, I>(
    reducer: R,
    initialArg: I,
    init?: (arg: I) => any
  ): [any, Dispatch<any>];
  export function forwardRef<T, P>(render: (props: P, ref: any) => ReactElement | null): any;

  export { default } from "react";
}

declare namespace React {
  type ReactNode = any;
}

declare module "react-dom" {
  const ReactDOM: any;
  export default ReactDOM;
}

declare module "react-dom/client" {
  export function createRoot(container: any): { render(children: any): void };
}

declare namespace JSX {
  interface IntrinsicElements {
    [elemName: string]: any;
  }
}
