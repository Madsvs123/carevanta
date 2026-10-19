import { initials } from "../../utils/formatters";

interface AvatarProps { name: string; src?: string; size?: number; }

export function Avatar({ name, src, size = 40 }: AvatarProps) {
  if (src) return <img classNam="avatar" src={src} alt={name} width={size} height={size} />;
  return <div className="avatar avatar-fallback" style={{ width: size, height: size }}>{initials(name)}</div>;
}
