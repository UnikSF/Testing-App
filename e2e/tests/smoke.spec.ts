import { expect, test } from "@playwright/test";

// Public surfaces only — SSO-gated apps (finance, feedback) redirect to login,
// so they're out of scope for a credential-less smoke suite.

test("landing shows the app portal", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle(/Fiddle's Tales/);
  await expect(page.getByText("Sensitivity Finder")).toBeVisible();
  await expect(page.getByText("Downloads", { exact: true })).toBeVisible();
});

test("downloads page serves real artifacts", async ({ page, request }) => {
  await page.goto("/downloads/");
  await expect(page.getByRole("heading", { name: /Download/i })).toBeVisible();
  for (const f of [
    "SensitivityFinder.apk",
    "SensitivityFinder.exe",
    "FinanceWatcher.apk",
    "FinanceWatcher.exe",
    "Mappy.apk",
    "Mappy.exe",
  ]) {
    const res = await request.head(`/downloads/${f}`);
    expect(res.status(), f).toBe(200);
  }
});

test("sensitivity finder calibrator loads", async ({ page }) => {
  await page.goto("/sensitivity/");
  await expect(page.locator("body")).toContainText(/sensitiv/i);
});

test("PWA manifests are served", async ({ request }) => {
  for (const p of [
    "/manifest.webmanifest",
    "/sensitivity/manifest.webmanifest",
    "/finance/manifest.webmanifest",
    "/mappy/manifest.webmanifest",
    "/moodle/manifest.webmanifest",
  ]) {
    const res = await request.get(p);
    expect(res.status(), p).toBe(200);
  }
});

test("digital asset links published for the TWA APKs", async ({ request }) => {
  const res = await request.get("/.well-known/assetlinks.json");
  expect(res.status()).toBe(200);
  const body = await res.json();
  const pkgs = body.map((e: { target: { package_name: string } }) => e.target.package_name);
  expect(pkgs).toContain("net.fiddlestale.sensitivity");
  expect(pkgs).toContain("net.fiddlestale.finance");
});

// Fixed 2026-06-27: /wiki/ had a stale DB-host IP in LocalSettings; /moodle/ was
// stuck in an adminsetuppending redirect loop. Now an active regression guard.
test("public course apps are reachable", async ({ request }) => {
  for (const p of ["/wiki/", "/moodle/"]) {
    const res = await request.get(p);
    expect(res.status(), p).toBeLessThan(400);
  }
});
