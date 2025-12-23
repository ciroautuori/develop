/**
 * Buy Me a Coffee Button Component
 * Premium, brand-consistent button for StudioCentos
 */

import { Coffee } from 'lucide-react';
import { cn } from '../../lib/utils';

interface BuyMeCoffeeButtonProps {
    variant?: 'full' | 'compact';
    className?: string;
}

const BMAC_URL = 'https://buymeacoffee.com/ciroautuori';

export function BuyMeCoffeeButton({ variant = 'full', className }: BuyMeCoffeeButtonProps) {
    if (variant === 'compact') {
        return (
            <a
                href={BMAC_URL}
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Buy Me a Coffee"
                className={cn(
                    'inline-flex items-center justify-center w-9 h-9 rounded-full',
                    'bg-gradient-to-br from-amber-500/20 to-amber-600/10',
                    'border border-amber-500/30 hover:border-amber-400/60',
                    'text-amber-400 hover:text-amber-300',
                    'transition-all duration-300 hover:scale-110 hover:shadow-[0_0_20px_rgba(245,158,11,0.3)]',
                    className
                )}
            >
                <Coffee className="w-4 h-4" />
            </a>
        );
    }

    return (
        <a
            href={BMAC_URL}
            target="_blank"
            rel="noopener noreferrer"
            className={cn(
                'group inline-flex items-center gap-2 px-5 py-2.5 rounded-full',
                'bg-gradient-to-r from-amber-500/10 via-amber-400/5 to-amber-500/10',
                'border border-amber-500/30 hover:border-amber-400/60',
                'text-amber-400 hover:text-amber-300 font-medium text-sm',
                'transition-all duration-300 hover:shadow-[0_0_25px_rgba(245,158,11,0.25)]',
                'backdrop-blur-sm',
                className
            )}
        >
            <Coffee className="w-4 h-4 group-hover:animate-pulse" />
            <span>Buy me a Coffee</span>
        </a>
    );
}
