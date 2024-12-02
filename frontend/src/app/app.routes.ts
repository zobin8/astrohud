import { ChartComponent } from './chart/component';
import { HomeComponent } from './home/component';
import { Routes } from '@angular/router';

export const routes: Routes = [
    { path: '', redirectTo: 'home', pathMatch: 'full' },
    { path: 'home', component: HomeComponent },
    { path: 'chart', component: ChartComponent },
];