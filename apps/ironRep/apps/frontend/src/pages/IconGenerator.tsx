import { AppIcon, AppIconMinimal } from "../components/AppIcon";

/**
 * Icon Generator Page
 * Visit /icon-generator in dev mode to download PWA icons
 */
export function IconGenerator() {
  const downloadSVG = (svgElement: SVGSVGElement | null, filename: string) => {
    if (!svgElement) return;

    const svgData = new XMLSerializer().serializeToString(svgElement);
    const svgBlob = new Blob([svgData], {
      type: "image/svg+xml;charset=utf-8",
    });
    const url = URL.createObjectURL(svgBlob);

    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();

    URL.revokeObjectURL(url);
  };

  const convertToPNG = async (
    svgElement: SVGSVGElement | null,
    size: number,
    filename: string
  ) => {
    if (!svgElement) return;

    const canvas = document.createElement("canvas");
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const svgData = new XMLSerializer().serializeToString(svgElement);
    const img = new Image();
    const svgBlob = new Blob([svgData], {
      type: "image/svg+xml;charset=utf-8",
    });
    const url = URL.createObjectURL(svgBlob);

    img.onload = () => {
      ctx.drawImage(img, 0, 0, size, size);
      canvas.toBlob((blob) => {
        if (!blob) return;
        const pngUrl = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = pngUrl;
        link.download = filename;
        link.click();
        URL.revokeObjectURL(pngUrl);
      }, "image/png");
      URL.revokeObjectURL(url);
    };

    img.src = url;
  };

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">PWA Icon Generator</h1>
          <p className="text-muted-foreground">
            Generate and download icons for your Progressive Web App
          </p>
        </div>

        {/* Main Icon */}
        <div className="bg-card border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Main Icon (with text)</h2>
          <div className="flex gap-6 items-start">
            <div className="bg-gray-100 p-4 rounded-lg">
              <div id="icon-512" className="w-64 h-64">
                <AppIcon size={256} />
              </div>
            </div>
            <div className="space-y-3">
              <button
                onClick={() => {
                  const svg = document.querySelector(
                    "#icon-512 svg"
                  ) as SVGSVGElement;
                  convertToPNG(svg, 512, "pwa-512x512.png");
                }}
                className="block w-full bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90"
              >
                Download 512x512 PNG
              </button>
              <button
                onClick={() => {
                  const svg = document.querySelector(
                    "#icon-512 svg"
                  ) as SVGSVGElement;
                  convertToPNG(svg, 192, "pwa-192x192.png");
                }}
                className="block w-full bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90"
              >
                Download 192x192 PNG
              </button>
              <button
                onClick={() => {
                  const svg = document.querySelector(
                    "#icon-512 svg"
                  ) as SVGSVGElement;
                  convertToPNG(svg, 180, "apple-touch-icon.png");
                }}
                className="block w-full bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90"
              >
                Download 180x180 PNG (Apple)
              </button>
              <button
                onClick={() => {
                  const svg = document.querySelector(
                    "#icon-512 svg"
                  ) as SVGSVGElement;
                  downloadSVG(svg, "icon.svg");
                }}
                className="block w-full bg-secondary text-secondary-foreground px-4 py-2 rounded-md hover:bg-secondary/80"
              >
                Download SVG
              </button>
            </div>
          </div>
        </div>

        {/* Minimal Icon */}
        <div className="bg-card border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">
            Minimal Icon (maskable)
          </h2>
          <div className="flex gap-6 items-start">
            <div className="bg-gray-100 p-4 rounded-lg">
              <div id="icon-minimal" className="w-64 h-64">
                <AppIconMinimal size={256} />
              </div>
            </div>
            <div className="space-y-3">
              <button
                onClick={() => {
                  const svg = document.querySelector(
                    "#icon-minimal svg"
                  ) as SVGSVGElement;
                  convertToPNG(svg, 512, "pwa-512x512-maskable.png");
                }}
                className="block w-full bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90"
              >
                Download 512x512 PNG (Maskable)
              </button>
            </div>
          </div>
        </div>

        {/* Instructions */}
        <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-6">
          <h3 className="font-semibold mb-2">📝 Instructions</h3>
          <ol className="list-decimal list-inside space-y-1 text-sm text-muted-foreground">
            <li>Download all PNG files using the buttons above</li>
            <li>
              Move them to{" "}
              <code className="bg-muted px-1 rounded">
                apps/frontend/public/
              </code>
            </li>
            <li>
              Install PWA plugin:{" "}
              <code className="bg-muted px-1 rounded">
                pnpm add -D vite-plugin-pwa
              </code>
            </li>
            <li>
              Build: <code className="bg-muted px-1 rounded">pnpm build</code>
            </li>
            <li>Your app is now installable! 🎉</li>
          </ol>
        </div>
      </div>
    </div>
  );
}
