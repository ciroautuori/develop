/**
 * DOM Safety Patch for Framer Motion v2.0
 * Intercepts potentially unsafe DOM operations during early initialization
 * Prevents "TypeError: can't access property 'add', t is undefined"
 *
 * Framer-motion uses internal minified variables (t, e) that reference classList.
 * This patch ensures classList is always available.
 */

// Safe mock classList for when DOM is not ready
const createSafeClassList = (): DOMTokenList => ({
  add: () => {},
  remove: () => {},
  toggle: () => false,
  contains: () => false,
  replace: () => false,
  length: 0,
  value: '',
  item: () => null,
  forEach: () => {},
  entries: () => ({ next: () => ({ done: true, value: undefined }) } as any),
  keys: () => ({ next: () => ({ done: true, value: undefined }) } as any),
  values: () => ({ next: () => ({ done: true, value: undefined }) } as any),
  supports: () => false,
  toString: () => '',
  [Symbol.iterator]: function* () { yield* [] }
} as unknown as DOMTokenList);

if (typeof window !== 'undefined' && typeof Element !== 'undefined') {
  // Store original descriptor
  const originalClassListDescriptor = Object.getOwnPropertyDescriptor(Element.prototype, 'classList');

  if (originalClassListDescriptor && originalClassListDescriptor.get) {
    const originalGet = originalClassListDescriptor.get;

    Object.defineProperty(Element.prototype, 'classList', {
      configurable: true,
      enumerable: true,
      get() {
        try {
          // Check if element is connected to DOM
          if (!this || !this.ownerDocument) {
            return createSafeClassList();
          }

          const list = originalGet.call(this);

          // Return safe mock if classList is null/undefined
          if (!list) {
            return createSafeClassList();
          }

          return list;
        } catch {
          // Catch any errors and return safe mock
          return createSafeClassList();
        }
      }
    });
  }

  // Wrap document.createElement to ensure elements always have classList
  const originalCreateElement = document.createElement.bind(document);
  document.createElement = function(tagName: string, options?: ElementCreationOptions): HTMLElement {
    const element = originalCreateElement(tagName, options);
    // Ensure classList is available immediately
    if (!element.classList) {
      Object.defineProperty(element, 'classList', {
        value: createSafeClassList(),
        writable: true,
        configurable: true
      });
    }
    return element;
  };

  // Monkey-patch Element.animate for older browsers or detached elements
  const originalAnimate = Element.prototype.animate;
  Element.prototype.animate = function(keyframes: Keyframe[] | PropertyIndexedKeyframes | null, options?: number | KeyframeAnimationOptions) {
    try {
      if (originalAnimate && this.isConnected) {
        return originalAnimate.call(this, keyframes, options);
      }
    } catch {
      // Fall through to mock
    }

    // Return mock Animation for disconnected elements
    return {
      finished: Promise.resolve(this as unknown as Animation),
      cancel: () => {},
      finish: () => {},
      pause: () => {},
      play: () => {},
      reverse: () => {},
      commitStyles: () => {},
      persist: () => {},
      updatePlaybackRate: () => {},
      onfinish: null,
      oncancel: null,
      onremove: null,
      id: '',
      effect: null,
      timeline: null,
      startTime: 0,
      currentTime: 0,
      playbackRate: 1,
      playState: 'idle' as AnimationPlayState,
      replaceState: 'active' as AnimationReplaceState,
      pending: false,
      ready: Promise.resolve(this as unknown as Animation),
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => true,
    } as unknown as Animation;
  };
}

export {};
