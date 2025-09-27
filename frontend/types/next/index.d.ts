declare module "next" {
  export interface NextApiRequest {}
  export interface NextApiResponse {}
  export interface Metadata {
    title?: string;
    description?: string;
    icons?: Record<string, string>;
  }
}

declare module "next/image" {
  const NextImage: (props: any) => JSX.Element;
  export default NextImage;
}

declare module "next/link" {
  const NextLink: (props: any) => JSX.Element;
  export default NextLink;
}

declare module "next/navigation" {
  export const usePathname: () => string;
}
