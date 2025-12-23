import { Dumbbell } from "lucide-react";

/**
 * PWA Icon Component
 * Generates app icon using Lucide React icons
 */
export function AppIcon({ size = 512 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 512 512"
      xmlns="http://www.w3.org/2000/svg"
    >
      {/* Background */}
      <rect width="512" height="512" fill="#000000" />

      {/* Icon Container */}
      <g transform="translate(256, 200)">
        <Dumbbell
          size={200}
          color="#FFFFFF"
          strokeWidth={2.5}
          style={{ transform: "translate(-100px, -100px)" }}
        />
      </g>

      {/* App Name */}
      <text
        x="256"
        y="400"
        fontFamily="system-ui, -apple-system, sans-serif"
        fontSize="56"
        fontWeight="700"
        fill="#FFFFFF"
        textAnchor="middle"
      >
        IronRep
      </text>

      {/* Tagline */}
      <text
        x="256"
        y="450"
        fontFamily="system-ui, -apple-system, sans-serif"
        fontSize="24"
        fontWeight="400"
        fill="#AAAAAA"
        textAnchor="middle"
      >
        Medical Coach
      </text>
    </svg>
  );
}

/**
 * Alternative: Minimal Icon (for maskable)
 */
export function AppIconMinimal({ size = 512 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 512 512"
      xmlns="http://www.w3.org/2000/svg"
    >
      <rect width="512" height="512" fill="#000000" />
      <g transform="translate(256, 256)">
        <Dumbbell
          size={280}
          color="#FFFFFF"
          strokeWidth={3}
          style={{ transform: "translate(-140px, -140px)" }}
        />
      </g>
    </svg>
  );
}
