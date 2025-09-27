declare module "react-dom" {
  export const createPortal: (...args: any[]) => any;
}

declare module "react-dom/client" {
  export function createRoot(container: HTMLElement): {
    render(children: any): void;
  };
}
