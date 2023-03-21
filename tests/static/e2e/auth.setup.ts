// auth.setup.ts
import { test as setup } from '@playwright/test';
import { setStorageState } from './helpers'
import * as adminState from '.auth/admin.json';
import * as userState from '.auth/user.json'

const adminFile = '.auth/admin.json';

setup('authenticate as admin', async ({ page }) => {
  // Perform authentication steps. Replace these actions with your own.
  await page.goto("http://127.0.0.1:8080/default/auth/login");
  await page.getByLabel('Email').fill('admin@example.com');
  await page.getByLabel('Password').fill('password');
  await page.getByRole('button', { name: 'Login' }).click();
  // End of authentication steps.

  await setStorageState(page, { cookies: adminState.cookies, origins: adminState.origins });
  await page.context().storageState({ path: adminFile });
});

const userFile = './playwright/.auth/user.json';

setup('authenticate as user', async ({ page }) => {
  // Perform authentication steps. Replace these actions with your own.
  await page.goto("http://127.0.0.1:8080/default/auth/login");
  await page.getByLabel('Email').fill('user@example.com');
  await page.getByLabel('Password').fill('password');
  await page.getByRole('button', { name: 'Login' }).click();
  // End of authentication steps.

  await page.context().storageState({ path: userFile });
});
