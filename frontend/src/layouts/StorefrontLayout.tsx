import { Outlet } from "react-router";

export function StorefrontLayout() {
  return (
    <div className="min-h-screen flex flex-col bg-background">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:px-4 focus:py-2 bg-primary text-white rounded z-50"
      >
        Skip to main content
      </a>
      <header className="bg-white border-b border-border">
        <div className="max-w-7xl mx-auto px-4 h-14 flex items-center">
          <a
            href="/"
            className="font-semibold text-text-primary text-lg min-h-[44px] inline-flex items-center"
          >
            persocart
          </a>
          <nav className="ml-auto">
            <a
              href="/admin"
              className="text-sm text-text-secondary hover:text-text-primary px-3 py-2 min-h-[44px] inline-flex items-center"
            >
              Admin
            </a>
          </nav>
        </div>
      </header>
      <main id="main" className="flex-1 max-w-7xl mx-auto w-full px-4 py-6">
        <Outlet />
      </main>
      <footer className="border-t border-border py-4 px-4 text-center text-sm text-text-secondary">
        <p>
          This store uses only essential cookies (session &amp; CSRF) required
          for secure operation. No personal shopper data is collected.
        </p>
      </footer>
    </div>
  );
}
