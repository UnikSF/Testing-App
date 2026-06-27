import { expect, test } from "@playwright/test";

// Regression guards for things that have broken before. Hits the live homelab.

const DOWNLOADS: Record<string, number> = {
  // file -> minimum plausible size in bytes (catches truncated / 0-byte / missing)
  "SensitivityFinder.apk": 100_000,
  "FinanceWatcher.apk": 100_000,
  "Mappy.apk": 1_000_000,
  "SensitivityFinder.exe": 10_000_000,
  "FinanceWatcher.exe": 10_000_000,
  "Mappy.exe": 10_000_000,
};

test.describe("downloads", () => {
  for (const [file, minSize] of Object.entries(DOWNLOADS)) {
    test(`${file} is served and not truncated`, async ({ request }) => {
      const res = await request.head(`/downloads/${file}`);
      expect(res.status(), `${file} status`).toBe(200);
      const len = Number(res.headers()["content-length"] ?? "0");
      expect(len, `${file} size`).toBeGreaterThan(minSize);
    });
  }

  test("every link on the downloads page resolves (no dangling artifact)", async ({ page, request }) => {
    await page.goto("/downloads/");
    const hrefs = await page.locator('a[href^="/downloads/"]').evaluateAll((els) =>
      els.map((e) => (e as HTMLAnchorElement).getAttribute("href")!).filter(Boolean)
    );
    expect(hrefs.length).toBeGreaterThan(0);
    for (const href of [...new Set(hrefs)]) {
      const res = await request.head(href);
      expect(res.status(), href).toBe(200);
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
