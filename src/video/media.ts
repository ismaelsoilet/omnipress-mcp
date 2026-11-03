import { staticFile } from "remotion";

/**
 * Resolve a public-dir-relative media path without ever passing an absolute
 * path to staticFile(). Media staging (omnipress media.json) is responsible for
 * turning absolute channel paths into relative targets.
 */
export const resolveMediaSrc = (src?: string): string => {
  if (!src) {
    return "";
  }
  if (
    src.startsWith("http://") ||
    src.startsWith("https://") ||
    src.startsWith("data:") ||
    src.startsWith("blob:")
  ) {
    return src;
  }
  return staticFile(src);
};
