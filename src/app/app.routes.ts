import type { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: 'home',
    loadComponent: () => import('./feature/home/home.page').then((m) => m.HomePage),
  },
  {
    path: 'config',
    loadComponent: () => import('./feature/config/config.page').then((m) => m.ConfigPage),
  },
  {
    path: '',
    redirectTo: 'home',
    pathMatch: 'full',
  },
];
