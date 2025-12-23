/**
 * Portfolio List - ENTERPRISE CON CRUD COMPLETO
 * @deprecated Use PortfolioHub instead
 * Design IDENTICO alla Landing con supporto Light/Dark
 */
import { Link } from 'react-router-dom';
import { Plus, Edit, Briefcase, Package } from 'lucide-react';
import { useProjects, useServices } from '../hooks/usePortfolio';
import { useTheme } from '../../../shared/contexts/ThemeContext';
import { SPACING } from '../../../shared/config/constants';
import { cn } from '../../../shared/lib/utils';

export function PortfolioList() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  // Theme classes
  const textPrimary = isDark ? 'text-white' : 'text-gray-900';
  const textSecondary = isDark ? 'text-gray-400' : 'text-gray-600';
  const textTertiary = isDark ? 'text-gray-500' : 'text-gray-500';
  const cardBg = isDark ? 'bg-white/5 border-white/10' : 'bg-gray-100 border-gray-200';
  const itemBg = isDark ? 'bg-white/5 hover:bg-white/10 border-white/10' : 'bg-white hover:bg-gray-50 border-gray-200';
  const buttonBg = isDark ? 'bg-white/10 hover:bg-white/20 text-white' : 'bg-gray-200 hover:bg-gray-300 text-gray-900';
  const badgeBg = isDark ? 'bg-white/10 text-gray-400' : 'bg-gray-200 text-gray-600';
  const greenBadge = isDark ? 'bg-gold/20 text-gold' : 'bg-gold/10 text-gold';

  const { data: projects, isLoading: loadingProjects } = useProjects(1, {});
  const { data: services, isLoading: loadingServices } = useServices(1, {});

  const displayProjects = projects;
  const displayServices = services;

  return (
    <div className={cn(SPACING.padding.full, SPACING.lg)}>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className={`text-2xl sm:text-3xl lg:text-4xl font-bold ${textPrimary}`}>Portfolio</h1>
          <p className={`text-sm sm:text-base ${textSecondary} mt-1 sm:mt-2`}>Gestisci progetti e servizi in modo enterprise</p>
        </div>
      </div>

      {/* Projects Section */}
      <div className={`${cardBg} border rounded-2xl sm:rounded-3xl p-4 sm:p-6 lg:p-8`}>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div className="flex items-center gap-2 sm:gap-3">
            <Briefcase className="h-5 w-5 sm:h-6 sm:w-6 text-gold" />
            <h2 className={`text-xl sm:text-2xl font-semibold ${textPrimary}`}>Progetti ({displayProjects?.total || 0})</h2>
          </div>
          <Link to="/admin/portfolio/project/new" className="w-full sm:w-auto">
            <button className="w-full sm:w-auto px-4 sm:px-6 py-2.5 sm:py-3 bg-gold text-black rounded-lg hover:bg-gold-light transition flex items-center justify-center gap-2 font-medium text-sm sm:text-base">
              <Plus className="h-4 w-4 sm:h-5 sm:w-5" />
              Nuovo Progetto
            </button>
          </Link>
        </div>

        {loadingProjects ? (
          <div className={`text-center py-12 ${textTertiary}`}>Caricamento...</div>
        ) : displayProjects?.items && displayProjects.items.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
            {displayProjects.items.map((project: any) => (
              <Link
                key={project.id}
                to={`/admin/portfolio/project/${project.id}`}
                className={`group p-4 sm:p-6 ${itemBg} rounded-lg sm:rounded-xl transition border hover:border-gold/50`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className={`${textPrimary} font-semibold group-hover:text-gold transition`}>{project.title}</h3>
                    <p className={`text-sm ${textSecondary} mt-1`}>{project.category} • {project.year}</p>
                  </div>
                  <Edit className="h-4 w-4 text-gray-500 group-hover:text-gold transition" />
                </div>
                <p className={`text-sm ${textTertiary} line-clamp-2`}>{project.description}</p>
                <div className="flex items-center gap-2 mt-3 flex-wrap">
                  {project.is_public && (
                    <span className={`px-2 py-1 ${greenBadge} text-xs rounded`}>Pubblico</span>
                  )}
                  {project.is_featured && (
                    <span className="px-2 py-1 bg-gold/20 text-gold text-xs rounded">In evidenza</span>
                  )}
                  <span className={`px-2 py-1 ${badgeBg} text-xs rounded`}>{project.status}</span>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 sm:py-12">
            <p className={`text-sm sm:text-base ${textTertiary} mb-4`}>Nessun progetto presente</p>
            <Link to="/admin/portfolio/project/new" className="inline-block w-full sm:w-auto">
              <button className={`w-full sm:w-auto px-6 py-2 ${buttonBg} rounded-lg transition text-sm sm:text-base`}>
                Crea il primo progetto
              </button>
            </Link>
          </div>
        )}
      </div>

      {/* Services Section */}
      <div className={`${cardBg} border rounded-2xl sm:rounded-3xl p-4 sm:p-6 lg:p-8`}>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div className="flex items-center gap-2 sm:gap-3">
            <Package className="h-5 w-5 sm:h-6 sm:w-6 text-gold" />
            <h2 className={`text-xl sm:text-2xl font-semibold ${textPrimary}`}>Servizi ({displayServices?.total || 0})</h2>
          </div>
          <Link to="/admin/portfolio/service/new" className="w-full sm:w-auto">
            <button className="w-full sm:w-auto px-4 sm:px-6 py-2.5 sm:py-3 bg-gold text-black rounded-lg hover:bg-gold-light transition flex items-center justify-center gap-2 font-medium text-sm sm:text-base">
              <Plus className="h-4 w-4 sm:h-5 sm:w-5" />
              Nuovo Servizio
            </button>
          </Link>
        </div>

        {loadingServices ? (
          <div className={`text-center py-12 ${textTertiary}`}>Caricamento...</div>
        ) : displayServices?.items && displayServices.items.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
            {displayServices.items.map((service: any) => (
              <Link
                key={service.id}
                to={`/admin/portfolio/service/${service.id}`}
                className={`group p-4 sm:p-6 ${itemBg} rounded-lg sm:rounded-xl transition border hover:border-gold/50`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-3xl">{service.icon}</span>
                      <h3 className={`${textPrimary} font-semibold group-hover:text-gold transition`}>{service.title}</h3>
                    </div>
                    <p className={`text-sm ${textSecondary}`}>{service.category}</p>
                  </div>
                  <Edit className="h-4 w-4 text-gray-500 group-hover:text-gold transition" />
                </div>
                <p className={`text-sm ${textTertiary} line-clamp-2`}>{service.description}</p>
                <div className="flex items-center gap-2 mt-3 flex-wrap">
                  {service.is_active && (
                    <span className={`px-2 py-1 ${greenBadge} text-xs rounded`}>Attivo</span>
                  )}
                  {service.is_featured && (
                    <span className="px-2 py-1 bg-gold/20 text-gold text-xs rounded">In evidenza</span>
                  )}
                  {service.value_indicator && (
                    <span className={`px-2 py-1 ${badgeBg} text-xs rounded`}>{service.value_indicator}</span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 sm:py-12">
            <p className={`text-sm sm:text-base ${textTertiary} mb-4`}>Nessun servizio presente</p>
            <Link to="/admin/portfolio/service/new" className="inline-block w-full sm:w-auto">
              <button className={`w-full sm:w-auto px-6 py-2 ${buttonBg} rounded-lg transition text-sm sm:text-base`}>
                Crea il primo servizio
              </button>
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
