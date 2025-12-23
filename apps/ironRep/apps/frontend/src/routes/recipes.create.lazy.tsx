import { createLazyFileRoute } from '@tanstack/react-router';
import { RecipeCreator } from '../features/nutrition/pages/RecipeCreator';

export const Route = createLazyFileRoute('/recipes/create')({
    component: RecipeCreator,
});
