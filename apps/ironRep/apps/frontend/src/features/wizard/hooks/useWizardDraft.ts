
import { useState, useEffect, useCallback } from "react";
import { IntakeData } from "../steps/IntakeStep";
import { InjuryDetails } from "../steps/InjuryDetailsStep";

const DRAFT_KEY = "ironrep_wizard_draft_v1";

export interface WizardDraft {
    step: string;
    intakeData: IntakeData | null;
    injuryData: InjuryDetails | null;
    foodPrefs: { liked: string[], disliked: string[] } | null;
    timestamp: number;
}

export function useWizardDraft() {
    const [draft, setDraft] = useState<WizardDraft | null>(null);
    const [hasLoaded, setHasLoaded] = useState(false);

    // Load on mount
    useEffect(() => {
        try {
            const saved = localStorage.getItem(DRAFT_KEY);
            if (saved) {
                const parsed = JSON.parse(saved);
                // Simple expiry check (e.g. 24h)
                const age = Date.now() - parsed.timestamp;
                if (age < 24 * 60 * 60 * 1000) {
                    setDraft(parsed);
                } else {
                    localStorage.removeItem(DRAFT_KEY);
                }
            }
        } catch (e) {
            console.error("Failed to load wizard draft", e);
        } finally {
            setHasLoaded(true);
        }
    }, []);

    // Save function (debounced usage recommended in parent, but direct here for simplicity on step change)
    const saveDraft = useCallback((
        step: string,
        intakeData: IntakeData | null,
        injuryData: InjuryDetails | null,
        foodPrefs: { liked: string[], disliked: string[] } | null
    ) => {
        if (!step) return;

        const draftData: WizardDraft = {
            step,
            intakeData,
            injuryData,
            foodPrefs,
            timestamp: Date.now()
        };

        try {
            localStorage.setItem(DRAFT_KEY, JSON.stringify(draftData));
        } catch (e) {
            console.error("Failed to save wizard draft", e);
        }
    }, []);

    const clearDraft = useCallback(() => {
        try {
            localStorage.removeItem(DRAFT_KEY);
            setDraft(null);
        } catch (e) {
            console.error("Failed to clear wizard draft", e);
        }
    }, []);

    return { draft, hasLoaded, saveDraft, clearDraft };
}
