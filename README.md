# HypeLens AI - Modern Frontend

A futuristic, modern shopping assistant frontend built with Next.js 14, featuring AI-powered search and stunning UI/UX inspired by Airbnb Design and Obys Agency.

## ✨ Features

### 🎨 Design
- **Dark/Light Mode**: Seamless theme switching with system preference detection
- **Glass Morphism**: Beautiful transparent UI elements with backdrop blur
- **Smooth Animations**: Powered by Framer Motion for cinematic transitions
- **Responsive Design**: Mobile-first approach, works on all devices
- **Modern Typography**: Custom font stack with Inter and Outfit

### 🔍 Search Capabilities
- **Text Search**: AI-powered product search with autocomplete
- **Visual Search**: Upload images to find similar products
- **Smart Suggestions**: Quick access to popular categories
- **Real-time Results**: Get search results in under 1 second

### 🚀 Performance
- **Server-Side Rendering**: Fast initial page loads with Next.js 14
- **Optimized Images**: Automatic image optimization
- **Code Splitting**: Lazy loading for better performance
- **API Caching**: Smart caching with React Query

## 📁 Project Structure

```
frontend-nextjs/
├── src/
│   ├── app/                      # Next.js 14 App Router
│   │   ├── layout.tsx           # Root layout with theme provider
│   │   ├── page.tsx             # Home page
│   │   └── globals.css          # Global styles
│   │
│   ├── components/              # React components
│   │   ├── layout/              # Layout components
│   │   │   └── Header.tsx       # Main navigation header
│   │   ├── home/                # Home page components
│   │   │   ├── HeroSection.tsx  # Hero with animated elements
│   │   │   ├── SearchSection.tsx # Search interface
│   │   │   └── FeaturesSection.tsx # Features grid
│   │   └── providers/           # Context providers
│   │       └── ThemeProvider.tsx # Theme management
│   │
│   ├── lib/                     # Utility libraries
│   │   ├── api.ts              # Axios instance & interceptors
│   │   └── utils.ts            # Helper functions
│   │
│   ├── services/                # API services
│   │   └── productService.ts   # Product API calls
│   │
│   └── store/                   # State management
│       └── useStore.ts         # Zustand stores
│
├── public/                      # Static assets
├── .env.local                   # Environment variables
├── next.config.js              # Next.js configuration
├── tailwind.config.ts          # Tailwind CSS config
├── tsconfig.json               # TypeScript config
└── package.json                # Dependencies
```

## 🛠️ Tech Stack

### Core
- **Next.js 14**: React framework with App Router
- **React 18**: UI library
- **TypeScript**: Type-safe development

### Styling
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Animation library
- **next-themes**: Theme management

### State & Data
- **Zustand**: Lightweight state management
- **Axios**: HTTP client
- **React Icons**: Icon library

### Features
- **react-dropzone**: File upload with drag & drop

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
cd frontend-nextjs
npm install
```

2. Set up environment variables:
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Run development server:
```bash
npm run dev
```

4. Open http://localhost:3000

### Build for Production

```bash
npm run build
npm start
```

## 🎨 Design System

### Colors
- **Primary**: Blue gradient (500-600)
- **Accent**: Purple & Pink gradients
- **Dark Mode**: Sophisticated dark palette
- **Transparency**: Glass morphism effects

### Typography
- **Headings**: Outfit (bold, modern)
- **Body**: Inter (clean, readable)

### Animations
- **Float**: Gentle floating elements
- **Glow**: Pulsing glow effects
- **Slide**: Smooth entrance animations
- **Scale**: Interactive hover states

## 🔌 Backend Integration

The frontend connects to the Python backend API:

### Endpoints Used
- `POST /api/search` - Text search
- `POST /api/visual-search` - Image search
- `GET /api/products/:id` - Get product details
- `GET /api/trending` - Trending products
- `GET /api/categories` - Product categories

### API Configuration
Located in `src/lib/api.ts`:
- Base URL from environment variables
- Request/response interceptors
- Error handling
- Timeout configuration

## 📱 Responsive Breakpoints

- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

## 🎯 Key Components

### Header
- Animated on scroll
- Theme toggle
- Mobile menu
- Glass morphism effect

### Hero Section
- Gradient animations
- Floating cards
- Stats display
- CTA buttons

### Search Section
- Mode toggle (text/image)
- Image upload with preview
- Quick suggestions
- Smooth transitions

### Features Section
- Grid layout
- Icon animations
- Hover effects
- Gradient accents

## 🔧 Customization

### Theme Colors
Edit `tailwind.config.ts`:
```typescript
colors: {
  primary: { /* your colors */ },
  // ...
}
```

### API URL
Edit `.env.local`:
```
NEXT_PUBLIC_API_URL=your_api_url
```

### Fonts
Edit `src/app/layout.tsx`:
```typescript
const customFont = CustomFont({ /* config */ })
```

## 📄 License

MIT License - Feel free to use for your projects!

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Built with ❤️ using Next.js 14 & Tailwind CSS**
