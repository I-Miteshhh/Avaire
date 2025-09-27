declare module "next" {
  export type Metadata = Record<string, any>;
}

declare module "next/link" {
  const Link: any;
  export default Link;
}

declare module "next/navigation" {
  export function usePathname(): string;
  export function useRouter(): any;
}

declare module "next/image" {
  const NextImage: any;
  export default NextImage;
}

declare module "next/dynamic" {
  const dynamic: any;
  export default dynamic;
}
