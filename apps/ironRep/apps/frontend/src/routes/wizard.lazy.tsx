import { createLazyFileRoute } from "@tanstack/react-router";
import { WizardOrchestrator } from "../features/wizard/WizardOrchestrator";
import { logger } from "../lib/logger";

export const Route = createLazyFileRoute("/wizard")({
  component: WizardPage,
});

function WizardPage() {
  const handleComplete = () => {
    logger.info("Wizard orchestrator completed - navigation handled internally");
    // Navigation is handled by WizardOrchestrator
  };

  return <WizardOrchestrator onComplete={handleComplete} />;
}
