import { ChangeDetectionStrategy, Component, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { lucideHome, lucideMenu, lucideSettings } from '@ng-icons/lucide';

import { ZardButtonComponent } from '@/shared/components/button';
import { ZardSheetImports } from '@/shared/components/sheet';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  imports: [RouterLink, NgIcon, ZardButtonComponent, ...ZardSheetImports],
  viewProviders: [
    provideIcons({
      lucideHome,
      lucideMenu,
      lucideSettings,
    }),
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HeaderComponent {
  readonly visible = signal(false);
}
