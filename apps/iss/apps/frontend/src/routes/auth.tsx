import { createFileRoute, Outlet } from '@tanstack/react-router';

export const Route = createFileRoute('/auth')({
  component: AuthLayout,
});

function AuthLayout() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-iss-bordeaux-50 via-white to-iss-gold-50">
      {/* Background Pattern */}
      <div 
        className="absolute inset-0 opacity-50"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23c41e3a' fill-opacity='0.03'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
        }}
      />
      
      <div className="relative flex min-h-screen">
        {/* Left Side - Branding */}
        <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-iss-bordeaux-900 via-iss-bordeaux-800 to-iss-bordeaux-700 items-center justify-center p-12">
          <div className="text-white text-center max-w-md">
            <div className="mb-8">
              <h1 className="text-4xl font-bold mb-4">
                Benvenuto in ISS
              </h1>
              <p className="text-xl text-iss-bordeaux-100 leading-relaxed">
                La piattaforma che democratizza l'accesso ai finanziamenti per 
                <strong className="text-iss-gold-300"> 500+ APS campane</strong>
              </p>
            </div>
            
            <div className="space-y-4 text-left">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-iss-gold-500 rounded-full flex items-center justify-center">
                  <span className="text-iss-bordeaux-900 font-bold text-sm">✓</span>
                </div>
                <span className="text-iss-bordeaux-100">100% Gratuito per sempre</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-iss-gold-500 rounded-full flex items-center justify-center">
                  <span className="text-iss-bordeaux-900 font-bold text-sm">✓</span>
                </div>
                <span className="text-iss-bordeaux-100">Accessibilità WCAG 2.1 AA</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-iss-gold-500 rounded-full flex items-center justify-center">
                  <span className="text-iss-bordeaux-900 font-bold text-sm">✓</span>
                </div>
                <span className="text-iss-bordeaux-100">Supporto dedicato APS</span>
              </div>
            </div>
          </div>
        </div>
        
        {/* Right Side - Auth Forms */}
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="w-full max-w-md">
            <Outlet />
          </div>
        </div>
      </div>
    </div>
  );
}
