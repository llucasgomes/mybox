import { Component } from '@angular/core';
import { IonApp, IonRouterOutlet } from '@ionic/angular';

import { ZardSonnerComponent } from './shared/components/sonner';

@Component({
  selector: 'app-root',
  templateUrl: 'app.component.html',
  imports: [IonApp, IonRouterOutlet, ZardSonnerComponent],
})
export class AppComponent {
  constructor() {}
}
