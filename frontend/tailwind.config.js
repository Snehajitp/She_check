export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        rose:    { 50:'#fff1f2', 100:'#ffe4e6', 400:'#fb7185', 500:'#f43f5e', 600:'#e11d48', 700:'#be123c' },
        mauve:   { 50:'#fdf4ff', 100:'#fae8ff', 400:'#c084fc', 500:'#a855f7', 600:'#9333ea' },
        sage:    { 50:'#f0fdf4', 100:'#dcfce7', 400:'#4ade80', 500:'#22c55e', 600:'#16a34a' },
        blush:   { DEFAULT: '#f9e4e8', dark: '#f2c4ce' },
        plum:    { DEFAULT: '#4a1942', light: '#7b2d6e' },
      },
      fontFamily: {
        display: ['"DM Serif Display"', 'Georgia', 'serif'],
        body:    ['"Inter"', 'system-ui', 'sans-serif'],
      },
      borderRadius: { '2xl':'1rem', '3xl':'1.5rem' },
      boxShadow: {
        soft: '0 2px 20px 0 rgba(74,25,66,0.08)',
        card: '0 4px 32px 0 rgba(74,25,66,0.10)',
      }
    }
  },
  plugins: []
}
