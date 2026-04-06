import { Routes } from '@angular/router';
import { SidepanelComponent } from './modules/sidepanel/sidepanel.component';

export const routes: Routes = [
  {
    path: '',
    component: SidepanelComponent, // Default view for Teams Sidepanel
    title: 'LUMI AI Assistant'
  },
  {
    path: 'sidepanel',
    component: SidepanelComponent
  },
  {
    path: '**',
    redirectTo: ''
  }
];