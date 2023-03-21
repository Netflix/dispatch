import { Page } from '@playwright/test';

/**
 * Set the cookies as well as the localStorage items for each origin
 * to the context of the current page.
 *
 * This function causes an extra `page.goto` at the end. The `pageOptions`
 * param is for that navigation.
 *
 * @param page The page in question
 * @param param1 An object containing `cookies` and `origins`
 * @param pageOptions page options for the navigation
 */
export async function setStorageState(
  page: Page,
  { cookies, origins }: { cookies: Cookie[]; origins: Origin[] },
  pageOptions?: PageOptions,
) {
  const initialUrl = page.url();

  // 1. Set all origins which include the localStorage
  for (const { origin, localStorage } of origins) {
    // 1.1 Navigate to the origin
    await page.goto(origin);

    // 1.2 Loop through the items in localStorage and assign them
    for (const { name, value } of localStorage) {
      await page.evaluate(async (args: string) => {
        const [name, value] = args.split(',');
        window.localStorage.setItem(name, value);
        console.log(JSON.stringify(window.localStorage));
      }, `${name},${value}`);
    }
  }

  // 2. Set cookies
  await page.context().addCookies(cookies.map((cookie) => ({ ...cookie, sameSite: <SameSite>cookie.sameSite })));

  // 3. Navigate back to the initial url
  await page.goto(initialUrl, pageOptions);
}

// =========================== Types =========================== //

interface PageOptions {
  referer?: string | undefined;
  timeout?: number | undefined;
  waitUntil?: 'load' | 'domcontentloaded' | 'networkidle' | 'commit' | undefined;
}

interface Cookie {
  name: string;
  value: string;
  domain: string;
  path: string;
  expires: number;
  httpOnly: boolean;
  secure: boolean;
  sameSite?: string;
}

enum SameSite {
  Lax = 'Lax',
  None = 'None',
  Strict = 'Strict',
}

interface Origin {
  origin: string;
  localStorage: LocalStorage[];
}

interface LocalStorage {
  name: string;
  value: string;
}
