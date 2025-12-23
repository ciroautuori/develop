import { createLazyFileRoute } from "@tanstack/react-router";
import { IconGenerator } from "../pages/IconGenerator";

export const Route = createLazyFileRoute("/icon-generator")({
  component: IconGenerator,
});
