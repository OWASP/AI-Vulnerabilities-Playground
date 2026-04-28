import { useState, type FormEvent } from 'react';
import { Mail, Users } from 'lucide-react';

const CONTACT_EMAIL = import.meta.env.VITE_CONTACT_EMAIL;

const ContactPage = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!CONTACT_EMAIL) {
      // Keep UX predictable in strict-config mode.
      window.alert('Contact email is not configured. Set VITE_CONTACT_EMAIL.');
      return;
    }
    const subject = encodeURIComponent(`AIVP Contact from ${name || 'Anonymous'}`);
    const body = encodeURIComponent(
      `Name: ${name || 'Not provided'}\nEmail: ${email || 'Not provided'}\n\nMessage:\n${message || 'No message provided'}`
    );
    window.location.href = `mailto:${CONTACT_EMAIL}?subject=${subject}&body=${body}`;
  };

  return (
    <div className="container mx-auto px-6 py-12 max-w-4xl">
      <img
        src="/aivp-banner.png"
        alt="AI Vulnerabilities Playground banner"
        className="mx-auto mb-6 w-full max-w-2xl rounded-lg border border-cyan-800/40 shadow-md shadow-cyan-900/20"
      />
      <h1 className="text-4xl font-bold mb-8 text-center bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
        Get in Touch
      </h1>

      <div className="grid md:grid-cols-2 gap-8">
        <div className="p-6 bg-gradient-to-r from-gray-900/50 to-gray-800/50 rounded-xl border border-gray-700/50">
          <h2 className="text-xl font-semibold mb-4 flex items-center text-cyan-400">
            <Mail className="w-5 h-5 mr-2" />
            Contact Information
          </h2>
          <div className="space-y-3 text-gray-300">
            <p>Feel free to reach out for:</p>
            <ul className="text-sm space-y-1 list-disc list-inside ml-2">
              <li>Security consulting</li>
              <li>Lab suggestions</li>
              <li>Bug reports</li>
              <li>Collaboration opportunities</li>
            </ul>
          </div>
        </div>

        <div className="p-6 bg-gradient-to-r from-gray-900/50 to-gray-800/50 rounded-xl border border-gray-700/50">
          <h2 className="text-xl font-semibold mb-4 flex items-center text-purple-400">
            <Users className="w-5 h-5 mr-2" />
            Community
          </h2>
          <div className="space-y-3 text-gray-300">
            <p>Join our community:</p>
            <ul className="text-sm space-y-1 list-disc list-inside ml-2">
              <li>Discord Server</li>
              <li>GitHub Repository</li>
              <li>Twitter/X Updates</li>
              <li>Newsletter</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="mt-8 p-6 bg-gradient-to-r from-cyan-900/20 to-purple-900/20 rounded-xl border border-cyan-800/30">
        <h2 className="text-xl font-semibold mb-4 text-center">Send a Message</h2>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Your Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:border-cyan-500 focus:outline-none"
          />
          <input
            type="email"
            placeholder="Your Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:border-cyan-500 focus:outline-none"
          />
          <textarea
            placeholder="Your Message"
            rows={4}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            className="w-full px-4 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:border-cyan-500 focus:outline-none"
          />
          <button
            type="submit"
            className="w-full px-4 py-2 bg-gradient-to-r from-cyan-600 to-purple-600 text-white rounded-lg font-medium hover:from-cyan-500 hover:to-purple-500 transition-all"
          >
            Send Message
          </button>
        </form>
        <p className="mt-3 text-xs text-gray-400 text-center">
          Clicking Send Message opens your default mail client{CONTACT_EMAIL ? ` to email ${CONTACT_EMAIL}` : ''}.
        </p>
      </div>
    </div>
  );
};

export default ContactPage;
