import { GeneratorComponent } from './charts/generator/component';
import { HomeComponent } from './home/component';
import { Routes } from '@angular/router';

export const routes: Routes = [
    { path: '', redirectTo: 'home', pathMatch: 'full' },
    { path: 'home', component: HomeComponent },
    { path: 'charts/generator', component: GeneratorComponent },
];