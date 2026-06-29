import { expect, test } from "@playwright/test";

// Regression guards for things that have broken before. Hits the live homelab.

// Artifacts are hosted on GitHub Releases (the NAS home-uplink can't serve 74 MB
// reliably to external users). url -> minimum plausible size in bytes.
const DOWNLOADS: Record<string, number> = {
  "https://github.com/UnikSF/SensitivityFinder/releases/download/v1.0.0/SensitivityFinder.apk": 100_000,
  "https://github.com/UnikSF/FinanceWatcher/releases/download/v1.0.0/FinanceWatcher.apk": 100_000,
  "https://github.com/UnikSF/Mappy/releases/download/v1.0.0/Mappy.apk": 1_000_000,
  // Windows apps ship zipped — a bare unsigned .exe gets hard-blocked by browsers.
  "https://github.com/UnikSF/SensitivityFinder/releases/download/v1.0.0/SensitivityFinder.zip": 10_000_000,
  "https://github.com/UnikSF/FinanceWatcher/releases/download/v1.0.0/FinanceWatcher.zip": 10_000_000,
  "https://github.com/UnikSF/Mappy/releases/download/v1.0.0/Mappy.zip": 10_000_000,
};

test.describe("downloads", () => {
  for (const [url, minSize] of Object.entries(DOWNLOADS)) {
    const file = url.split("/").pop()!;
    test(`${file} is served and not truncated`, async ({ request }) => {
      // request follows GitHub's redirect to its CDN; Range avoids pulling 74 MB.
      const res = await request.get(url, { headers: { Range: "bytes=0-0" } });
      expect([200, 206], `${file} status`).toContain(res.status());
      const len = Number(
        res.headers()["content-range"]?.split("/")[1] ?? res.headers()["content-length"] ?? "0"
      );
      expect(len, `${file} size`).toBeGreaterThan(minSize);
    });
  }

  test("every download link on the page resolves (no dangling artifact)", async ({ page, request }) => {
    await page.goto("/downloads/");
    // The page renders from projects.json; artifacts now live on GitHub Releases.
    await page.waitForSelector('a.dl[href^="https://github.com"]', { timeout: 15_000 });
    const hrefs = await page.locator('a.dl[href^="https://github.com"]').evaluateAll((els) =>
      els.map((e) => (e as HTMLAnchorElement).getAttribute("href")!).filter(Boolean)
    );
    expect(hrefs.length).toBeGreaterThan(0);
    for (const href of [...new Set(hrefs)]) {
      const res = await request.get(href, { headers: { Range: "bytes=0-0" } });
      expect([200, 206], href).toContain(res.status());
    }
  });
});

// Regression: the Optimize button fetched an absolute /api/solve and 404'd under
// the /mappy proxy. It must reach the app at /mappy/api/solve and return a route.
test("mappy optimize endpoint works under the /mappy mount", async ({ request }) => {
  const res = await request.post("/mappy/api/solve", {
    data: {
      vehicles: [
        { lat: 48.85, lon: 2.35, label: "A" },
        { lat: 48.86, lon: 2.34, label: "B" },
      ],
      zones: 1,
    },
  });
  expect(res.status()).toBe(200);
  const body = await res.json();
  expect(Array.isArray(body.zones)).toBe(true);
  expect(body.zones.length).toBeGreaterThan(0);
});

// Regression: UGOS must redirect off the shared proxy to its own host:port
// (serving the vendor OS under /desktop 404'd its apps).
test("UGOS /app redirects straight to the UGOS host", async ({ request }) => {
  const res = await request.get("/app", { maxRedirects: 0 });
  expect(res.status()).toBeGreaterThanOrEqual(300);
  expect(res.status()).toBeLessThan(400);
  expect(res.headers()["location"] ?? "").toMatch(/:9999\/desktop\//);
});
