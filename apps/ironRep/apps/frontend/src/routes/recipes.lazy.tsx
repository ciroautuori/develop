import { createLazyFileRoute } from '@tanstack/react-router';
import { RecipesPage } from '../features/nutrition/pages/RecipesPage';

export const Route = createLazyFileRoute('/recipes')({
    component: RecipesPage,
});
