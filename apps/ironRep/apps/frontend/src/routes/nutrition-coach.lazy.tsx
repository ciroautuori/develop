import { createLazyFileRoute } from "@tanstack/react-router";
import { ChatInterface } from "../features/chat/ChatInterface";

export const Route = createLazyFileRoute("/nutrition-coach")({
  component: NutritionCoachPage,
});

function NutritionCoachPage() {
  return <ChatInterface mode="nutrition" />;
}
