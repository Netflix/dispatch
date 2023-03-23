import { test } from '@playwright/test';

export type DispatchUserFixtures = {
    adminAccount: string;
}

type ExtendedParams = Parameters<typeof test.extend<DispatchUserFixtures>>

// Note that we pass worker fixture types as a second template parameter.
export const myAccount: ExtendedParams[0] = {
  adminAccount: async({page}, use) => {
    // Unique username.
    const username = 'admin@example.com';
    const password = 'password';

    await page.goto('/default/auth/login');
    await page.getByLabel('Email').fill(username);
    await page.getByLabel('Password').fill(password);
    await page.getByRole('button', { name: 'Login'}).click();
    await use('test');
  },
};
