/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        neon: {
          cyan: '#00ffff',
          magenta: '#ff00ff',
          lime: '#39ff14',
          blue: '#0066ff',
          purple: '#bf00ff',
          pink: '#ff0066',
          green: '#00ff88',
          red: '#ff3366',
        },
        dark: {
          bg: '#0a0a1a',
          card: '#12122a',
          cardHover: '#1a1a3a',
          border: '#2a2a4a',
        },
      },
      boxShadow: {
        'neon-cyan': '0 0 10px #00ffff, 0 0 20px #00ffff, 0 0 40px #00ffff',
        'neon-magenta': '0 0 10px #ff00ff, 0 0 20px #ff00ff, 0 0 40px #ff00ff',
        'neon-lime': '0 0 10px #39ff14, 0 0 20px #39ff14, 0 0 40px #39ff14',
        'neon-blue': '0 0 10px #0066ff, 0 0 20px #0066ff',
        'neon-green': '0 0 10px #00ff88, 0 0 20px #00ff88',
        'neon-red': '0 0 10px #ff3366, 0 0 20px #ff3366',
        'card': '0 4px 20px rgba(0, 255, 255, 0.1)',
        'card-hover': '0 8px 30px rgba(0, 255, 255, 0.2)',
      },
      animation: {
        'pulse-neon': 'pulse-neon 2s ease-in-out infinite',
        'glow': 'glow 1.5s ease-in-out infinite alternate',
      },
      keyframes: {
        'pulse-neon': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
        'glow': {
          'from': { boxShadow: '0 0 10px #00ffff, 0 0 20px #00ffff' },
          'to': { boxShadow: '0 0 20px #00ffff, 0 0 30px #00ffff, 0 0 40px #00ffff' },
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'hero': 'linear-gradient(135deg, #0a0a1a 0%, #1a0a2e 50%, #0a1a2e 100%)',
      },
    },
  },
  plugins: [],
}
