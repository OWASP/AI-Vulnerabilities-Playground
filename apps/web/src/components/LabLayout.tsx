import AnimatedBackground from './AnimatedBackground';

type Props = {
  labNumber: string;
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  onBack: () => void;
};

const LabLayout = ({ labNumber, title, icon, children, onBack }: Props) => {
  return (
    <div className="min-h-screen bg-black text-white overflow-hidden relative">
      <AnimatedBackground />

      <div className="relative z-10">
        <header className="border-b border-cyan-800/30 backdrop-blur-lg bg-black/50">
          <div className="container mx-auto px-6 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="relative">
                  {icon}
                  <div className="absolute inset-0 animate-ping opacity-30">{icon}</div>
                </div>
                <div>
                  <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                    AIVP {labNumber}: {title}
                  </h1>
                  <p className="text-gray-400 text-sm mt-1">AI Vulnerabilities Playground</p>
                </div>
              </div>
              <button
                onClick={onBack}
                className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors text-sm"
              >
                Back to Labs
              </button>
            </div>
          </div>
        </header>

        <main className="container mx-auto px-6 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">{children}</div>
        </main>
      </div>
    </div>
  );
};

export default LabLayout;
