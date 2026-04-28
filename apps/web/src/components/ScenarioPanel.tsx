import { useState } from 'react';
import { Brain, Target, CheckCircle, XCircle } from 'lucide-react';
import { validateAnswer } from '../services/api';

type Props = {
  labId: string;
  scenario: React.ReactNode;
  objective: string;
  secretFormat?: string;
  whatYouBreak?: React.ReactNode;
  whatYouLearn?: React.ReactNode;
  realWorldImpact?: React.ReactNode;
};

const ScenarioPanel = ({ labId, scenario, objective, secretFormat, whatYouBreak, whatYouLearn, realWorldImpact }: Props) => {
  const [answer, setAnswer] = useState('');
  const [feedback, setFeedback] = useState<{ success: boolean; message: string } | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const result = await validateAnswer(labId, answer);
      setFeedback(result);
    } catch (e) {
      setFeedback({ success: false, message: 'Error: Unable to validate answer. Check server connection.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="p-4 bg-gradient-to-r from-purple-900/20 to-cyan-900/20 rounded-lg border border-purple-800/30">
        <h3 className="text-xl font-semibold mb-3 flex items-center text-purple-400">
          <Brain className="w-5 h-5 mr-2" />
          Scenario
        </h3>
        <div className="text-gray-300 text-sm leading-relaxed space-y-2">{scenario}</div>
      </div>

      <div className="p-4 bg-gradient-to-r from-cyan-900/20 to-blue-900/20 rounded-lg border border-cyan-800/30">
        <h3 className="text-xl font-semibold mb-3 flex items-center text-cyan-400">
          <Target className="w-5 h-5 mr-2" />
          Objective
        </h3>
        <p className="text-gray-300 text-sm">{objective}</p>
        {secretFormat && (
          <code className="block mt-2 text-xs bg-black/50 p-2 rounded text-green-400">{secretFormat}</code>
        )}
      </div>

      {whatYouBreak && (
        <div className="p-4 bg-gradient-to-r from-red-900/20 to-orange-900/20 rounded-lg border border-red-800/30">
          <h3 className="text-xl font-semibold mb-3 flex items-center text-red-400">
            <XCircle className="w-5 h-5 mr-2" />
            What You're Breaking
          </h3>
          <div className="text-gray-300 text-sm leading-relaxed space-y-2">{whatYouBreak}</div>
        </div>
      )}

      {whatYouLearn && (
        <div className="p-4 bg-gradient-to-r from-blue-900/20 to-indigo-900/20 rounded-lg border border-blue-800/30">
          <h3 className="text-xl font-semibold mb-3 flex items-center text-blue-400">
            <Brain className="w-5 h-5 mr-2" />
            What You'll Learn
          </h3>
          <div className="text-gray-300 text-sm leading-relaxed space-y-2">{whatYouLearn}</div>
        </div>
      )}

      {realWorldImpact && (
        <div className="p-4 bg-gradient-to-r from-yellow-900/20 to-amber-900/20 rounded-lg border border-yellow-800/30">
          <h3 className="text-xl font-semibold mb-3 flex items-center text-yellow-400">
            <Target className="w-5 h-5 mr-2" />
            Real-World Impact
          </h3>
          <div className="text-gray-300 text-sm leading-relaxed space-y-2">{realWorldImpact}</div>
        </div>
      )}

      <div className="p-4 bg-gradient-to-r from-gray-900/50 to-gray-800/50 rounded-lg border border-gray-700">
        <h3 className="text-xl font-semibold mb-3 flex items-center text-green-400">
          <CheckCircle className="w-5 h-5 mr-2" />
          Submit Your Answer
        </h3>
        <input
          type="text"
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          placeholder="Enter the secret value..."
          className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:border-green-500 focus:outline-none transition-colors mb-3"
        />
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="w-full px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg font-medium transition-all duration-300 hover:from-green-500 hover:to-emerald-500 disabled:opacity-50"
        >
          {loading ? 'Validating...' : 'Submit Answer'}
        </button>

        {feedback && (
          <div
            className={`mt-3 p-3 rounded-lg flex items-center space-x-2 ${
              feedback.success
                ? 'bg-green-900/30 border border-green-700 text-green-400'
                : 'bg-red-900/30 border border-red-700 text-red-400'
            }`}
          >
            {feedback.success ? <CheckCircle className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
            <span>{feedback.message}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default ScenarioPanel;
