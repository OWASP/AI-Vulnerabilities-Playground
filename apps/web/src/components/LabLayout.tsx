import { CheckCircle } from 'lucide-react';
import AnimatedBackground from './AnimatedBackground';
import { adjacentLabs, navigate, shortName, useSolved } from '../lib/labs';

type Props = {
  labNumber: string;
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  onBack: () => void;
};

const LabLayout = ({ labNumber, title, icon, children, onBack }: Props) => {
  const labId = labNumber.replace('-', '_');
  const { prev, next, nextLabel } = adjacentLabs(labId);
  const solved = useSolved().includes(labId);

  return (
    <div className="min-h-screen bg-black text-white overflow-hidden relative">
      <AnimatedBackground />

      <div className="relative z-10">
        <header className="border-b border-cyan-800/30 backdrop-blur-lg bg-black/50">
          <div className="container mx-auto px-6 py-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center space-x-4">
                <div className="relative">
                  {icon}
                  <div className="absolute inset-0 animate-ping opacity-30">{icon}</div>
                </div>
                <div>
                  <div className="flex items-center space-x-4">
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                      AIVP {labNumber}: {title}
                    </h1>
                    {solved && (
                      <span className="flex items-center text-sm text-green-400 bg-green-900/30 border border-green-700 px-3 py-1 rounded-full">
                        <CheckCircle className="w-4 h-4 mr-1" />
                        Solved
                      </span>
                    )}
                  </div>
                  <p className="text-gray-400 text-sm mt-1">AI Vulnerabilities Playground</p>
                </div>
              </div>
              <div className="flex flex-wrap items-center gap-2">
                {prev && (
                  <button
                    onClick={() => navigate(`/labs/${prev.id}`)}
                    className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors text-sm"
                  >
                    ← {shortName(prev)}
                  </button>
                )}
                <button
                  onClick={onBack}
                  className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors text-sm"
                >
                  Back to Labs
                </button>
                {next && (
                  <button
                    onClick={() => navigate(`/labs/${next.id}`)}
                    className="px-4 py-2 bg-gradient-to-r from-cyan-600 to-purple-600 text-white rounded-lg text-sm hover:from-cyan-500 hover:to-purple-500 transition-all"
                  >
                    {nextLabel}: {shortName(next)} →
                  </button>
                )}
              </div>
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
