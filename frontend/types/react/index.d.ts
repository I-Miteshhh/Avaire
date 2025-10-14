declare module "react" {
  export type ReactNode = any;
  
  export interface FunctionComponent<P = {}> {
    (props: P & { children?: ReactNode }): JSX.Element | null;
    displayName?: string;
    defaultProps?: Partial<P>;
  }
  
  export type FC<P = {}> = FunctionComponent<P>;
  
  export type SetStateAction<S> = S | ((prevState: S) => S);
  export type Dispatch<A> = (value: A) => void;
  export type Ref<T> = ((instance: T | null) => void) | { current: T | null } | null;
  export type ForwardedRef<T> = ((instance: T | null) => void) | { readonly current: T | null } | null;
  
  export const useMemo: <T>(factory: () => T, deps: unknown[]) => T;
  export const useCallback: <T extends (...args: any[]) => unknown>(fn: T, deps: unknown[]) => T;
  export const useEffect: (effect: () => void | (() => void), deps?: unknown[]) => void;
  export const useState: <S>(initial: S | (() => S)) => [S, Dispatch<SetStateAction<S>>];
  export const useRef: <T>(initial: T) => { current: T };
  export const useContext: (context: unknown) => unknown;
  export const useReducer: (...args: unknown[]) => unknown;
  export const useTransition: () => [boolean, (callback: () => void) => void];
  export const useSyncExternalStore: (...args: unknown[]) => unknown;
  
  // forwardRef
  export function forwardRef<T, P = {}>(
    render: (props: P, ref: ForwardedRef<T>) => ReactNode | null
  ): FC<P & { ref?: Ref<T> }>;
  
  // HTML Attributes
  export interface HTMLAttributes<T = HTMLElement> {
    className?: string;
    children?: ReactNode;
    onClick?: (event: any) => void;
    onChange?: (event: any) => void;
    onSubmit?: (event: any) => void;
    style?: any;
    id?: string;
    title?: string;
    role?: string;
    [key: string]: any;
  }
  
  export interface ButtonHTMLAttributes<T = HTMLButtonElement> extends HTMLAttributes<T> {
    type?: "button" | "submit" | "reset";
    disabled?: boolean;
    value?: string | number;
    name?: string;
    form?: string;
  }
  
  export interface InputHTMLAttributes<T = HTMLInputElement> extends HTMLAttributes<T> {
    type?: string;
    value?: string | number;
    defaultValue?: string | number;
    placeholder?: string;
    disabled?: boolean;
    readOnly?: boolean;
    required?: boolean;
    name?: string;
    min?: string | number;
    max?: string | number;
    step?: string | number;
    checked?: boolean;
    defaultChecked?: boolean;
  }
  
  export interface SelectHTMLAttributes<T = HTMLSelectElement> extends HTMLAttributes<T> {
    value?: string | number;
    defaultValue?: string | number;
    disabled?: boolean;
    required?: boolean;
    name?: string;
    multiple?: boolean;
  }
  
  export interface TextareaHTMLAttributes<T = HTMLTextAreaElement> extends HTMLAttributes<T> {
    value?: string;
    defaultValue?: string;
    placeholder?: string;
    disabled?: boolean;
    readOnly?: boolean;
    required?: boolean;
    name?: string;
    rows?: number;
    cols?: number;
  }
  
  // Suspense component
  export interface SuspenseProps {
    children?: ReactNode;
    fallback?: ReactNode;
  }
  export const Suspense: FC<SuspenseProps>;
  
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
