/**
 * TokenPurchase - Token purchase page for customers
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Coins,
  Sparkles,
  Zap,
  Rocket,
  Crown,
  Building2,
  Check,
  CreditCard,
} from 'lucide-react';
import { cn } from '../../../shared/lib/utils';

interface TokenPackage {
  id: string;
  name: string;
  tokens: number;
  price: number;
  pricePerToken: number;
  icon: React.ElementType;
  popular?: boolean;
  features: string[];
}

const PACKAGES: TokenPackage[] = [
  {
    id: 'starter',
    name: 'Starter',
    tokens: 2500,
    price: 49.99,
    pricePerToken: 0.02,
    icon: Zap,
    features: ['2.500 token', 'Supporto email', 'Durata 1 mese'],
  },
  {
    id: 'growth',
    name: 'Growth',
    tokens: 5000,
    price: 99.99,
    pricePerToken: 0.02,
    icon: Rocket,
    popular: true,
    features: ['5.000 token', 'Supporto prioritario', 'Durata 2 mesi', '-15% sul prezzo'],
  },
  {
    id: 'pro',
    name: 'Pro',
    tokens: 7500,
    price: 149.99,
    pricePerToken: 0.02,
    icon: Crown,
    features: ['7.500 token', 'Supporto dedicato', 'Durata 3 mesi', '-25% sul prezzo'],
  },
  {
    id: 'agency',
    name: 'Agency',
    tokens: 15000,
    price: 249.99,
    pricePerToken: 0.017,
    icon: Building2,
    features: ['15.000 token', 'Account manager', 'Durata 6 mesi', '-35% sul prezzo'],
  },
];

export function TokenPurchase() {
  const [selectedPackage, setSelectedPackage] = useState<string>('growth');

  const handlePurchase = async (packageId: string) => {
    // Call backend to create Stripe checkout session
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/v1/billing/checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ package_id: packageId }),
      });

      if (response.ok) {
        const data = await response.json();
        // Redirect to Stripe checkout
        if (data.checkout_url) {
          window.location.href = data.checkout_url;
        }
      } else {
        console.error('Failed to create checkout session');
      }
    } catch (error) {
      console.error('Checkout error:', error);
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-4">
          <Coins className="h-4 w-4 text-primary" />
          <span className="text-sm font-medium text-primary">Token Store</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold text-foreground">Acquista Token</h1>
        <p className="text-muted-foreground mt-2 max-w-lg mx-auto">
          Scegli il pacchetto più adatto alle tue esigenze. Più token acquisti, più risparmi.
        </p>
      </motion.div>

      {/* Packages Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {PACKAGES.map((pkg, index) => {
          const Icon = pkg.icon;
          const isSelected = selectedPackage === pkg.id;

          return (
            <motion.div
              key={pkg.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              onClick={() => setSelectedPackage(pkg.id)}
              className={cn(
                'relative p-6 rounded-2xl border-2 cursor-pointer transition-all',
                isSelected
                  ? 'border-primary bg-primary/5 scale-105 shadow-lg'
                  : 'border-border bg-card hover:border-primary/50'
              )}
            >
              {/* Popular Badge */}
              {pkg.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-primary text-primary-foreground text-xs font-bold rounded-full">
                  POPOLARE
                </div>
              )}

              <div className="text-center mb-4">
                <div className={cn(
                  'w-12 h-12 mx-auto rounded-xl flex items-center justify-center mb-3',
                  isSelected ? 'bg-primary text-primary-foreground' : 'bg-muted'
                )}>
                  <Icon className="h-6 w-6" />
                </div>
                <h3 className="font-bold text-lg text-foreground">{pkg.name}</h3>
                <p className="text-3xl font-bold text-foreground mt-2">
                  €{pkg.price}
                </p>
                <p className="text-sm text-muted-foreground">
                  {pkg.tokens.toLocaleString()} token
                </p>
              </div>

              <ul className="space-y-2">
                {pkg.features.map((feature, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Check className="h-4 w-4 text-primary flex-shrink-0" />
                    {feature}
                  </li>
                ))}
              </ul>

              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handlePurchase(pkg.id);
                }}
                className={cn(
                  'w-full mt-6 py-3 rounded-xl font-medium transition-colors',
                  isSelected
                    ? 'bg-primary text-primary-foreground hover:bg-primary/90'
                    : 'bg-muted text-foreground hover:bg-muted/80'
                )}
              >
                {isSelected ? 'Acquista Ora' : 'Seleziona'}
              </button>
            </motion.div>
          );
        })}
      </div>

      {/* Payment Info */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="bg-card border border-border rounded-2xl p-6 text-center"
      >
        <CreditCard className="h-8 w-8 mx-auto text-muted-foreground mb-3" />
        <p className="text-sm text-muted-foreground">
          Pagamento sicuro con Stripe. Accettiamo carte di credito, Apple Pay e Google Pay.
        </p>
      </motion.div>
    </div>
  );
}
