/**
 * useScrollReveal Hook
 * Intersection Observer per scroll reveal animations
 */

import { useEffect } from 'react';

export function useScrollReveal() {
  useEffect(() => {
    const observerOptions = {
      threshold: 0.15,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !entry.target.classList.contains('active')) {
          entry.target.classList.add('active');
        }
      });
    }, observerOptions);

    // Attiva TUTTE le sezioni immediatamente per evitare schermo nero
    const elements = document.querySelectorAll('.reveal');
    elements.forEach(el => {
      el.classList.add('active');
      observer.observe(el);
    });

    return () => {
      observer.disconnect();
    };
  }, []);
}
