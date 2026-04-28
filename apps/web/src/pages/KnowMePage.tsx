import { User } from 'lucide-react';

const KnowMePage = () => {
  return (
    <div className="container mx-auto px-6 py-12 max-w-4xl">
      <h1 className="text-4xl font-bold mb-8 text-center bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
        About the Creator
      </h1>

      <div className="p-8 bg-gradient-to-r from-gray-900/50 to-gray-800/50 rounded-xl border border-gray-700/50">
        <div className="text-center mb-8">
          <div className="w-32 h-32 mx-auto mb-4 bg-gradient-to-r from-cyan-600 to-purple-600 rounded-full flex items-center justify-center">
            <User className="w-16 h-16 text-white" />
          </div>
        </div>

        <div className="space-y-6 text-gray-300">
          <p>
            Welcome to AIVP! I'm a security researcher passionate about AI/ML security and helping organizations
            understand the evolving threat landscape of artificial intelligence systems.
          </p>

          <p>
            This platform was born from real-world experience in testing AI systems for vulnerabilities and
            the realization that many security professionals lack hands-on experience with AI-specific attack vectors.
          </p>

          <div className="p-4 bg-black/30 rounded-lg">
            <h3 className="text-lg font-semibold mb-2 text-cyan-400">My Mission</h3>
            <p className="text-sm">
              To democratize AI security knowledge and empower defenders with practical skills to protect
              AI systems from emerging threats.
            </p>
          </div>

          <div className="p-4 bg-black/30 rounded-lg">
            <h3 className="text-lg font-semibold mb-2 text-purple-400">Background</h3>
            <ul className="text-sm space-y-1 list-disc list-inside">
              <li>Security Research & Red Teaming</li>
              <li>AI/ML Security Assessment</li>
              <li>Vulnerability Research</li>
              <li>Security Tool Development</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default KnowMePage;
