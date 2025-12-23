/**
 * Process Section Component - Come lavoro (4 step con animazioni stagger)
 */
import { motion } from 'framer-motion';
import { useLanguage } from '../i18n';

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2
    }
  }
};

const item = {
  hidden: { opacity: 0, y: 30, scale: 0.9 },
  show: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: "easeOut" as const
    }
  }
};

const stepIcons = ['🔍', '📐', '⚡', '🚀'];

export function ProcessSection() {
  const { t } = useLanguage();

  const steps = t.process.steps.map((step, index) => ({
    number: index + 1,
    title: step.title,
    description: step.description,
    icon: stepIcons[index]
  }));

  return (
    <section className="max-w-6xl mx-auto px-6 py-32">
      <motion.h2
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6 }}
        className="text-4xl font-light mb-20 text-center text-white light:text-gray-900"
      >
        {t.process.title} <span className="text-gold">{t.process.titleHighlight}</span>
      </motion.h2>

      <motion.div
        variants={container}
        initial="hidden"
        whileInView="show"
        viewport={{ once: true, margin: "-50px" }}
        className="grid md:grid-cols-4 gap-8"
      >
        {steps.map((step) => (
          <motion.div
            key={step.number}
            variants={item}
            whileHover={{
              scale: 1.05,
              transition: { duration: 0.2 }
            }}
            className="text-center group cursor-default"
          >
            <motion.div
              whileHover={{ rotate: 360 }}
              transition={{ duration: 0.6 }}
              className="w-16 h-16 rounded-full bg-gradient-to-br from-gold/20 to-gold/5 light:from-gold/30 light:to-gold/10 flex items-center justify-center mx-auto mb-6 text-2xl font-bold text-gold border border-gold/20 group-hover:border-gold/50 group-hover:shadow-[0_0_20px_rgba(212,175,55,0.3)] transition-all"
            >
              {step.number}
            </motion.div>
            <div className="text-3xl mb-3">{step.icon}</div>
            <h3 className="text-xl font-light mb-3 group-hover:text-gold transition-colors text-white light:text-gray-900">{step.title}</h3>
            <p className="text-sm text-gray-400 light:text-gray-600 leading-relaxed">
              {step.description}
            </p>
          </motion.div>
        ))}
      </motion.div>

      {/* Timeline connector - solo desktop */}
      <div className="hidden md:block relative mt-12">
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-gold/30 to-transparent" />
      </div>
    </section>
  );
}
