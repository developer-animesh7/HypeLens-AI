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
# Copy the example environment file
cp .env.local.example .env.local

# Edit .env.local and configure your variables
# Required:
NEXT_PUBLIC_API_URL=http://localhost:5000

# Optional (with defaults):
# NEXT_PUBLIC_APP_NAME=HypeLens AI
# NEXT_PUBLIC_APP_VERSION=1.0.0
# NEXT_PUBLIC_ENABLE_ANALYTICS=false
# NEXT_PUBLIC_MAX_IMAGE_SIZE=10485760
# NEXT_PUBLIC_DEFAULT_SEARCH_LIMIT=20
```

**Environment Variables:**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | ✅ Yes | `http://localhost:5000` | Backend API base URL |
| `NEXT_PUBLIC_APP_NAME` | ❌ No | `HypeLens AI` | Application name for branding |
| `NEXT_PUBLIC_APP_VERSION` | ❌ No | `1.0.0` | Application version |
| `NEXT_PUBLIC_ENABLE_ANALYTICS` | ❌ No | `false` | Enable analytics tracking |
| `NEXT_PUBLIC_MAX_IMAGE_SIZE` | ❌ No | `10485760` | Max image upload size (bytes) |
| `NEXT_PUBLIC_DEFAULT_SEARCH_LIMIT` | ❌ No | `20` | Default search results limit |

3. **Verify backend is running**:
```bash
# The FastAPI backend must be running on port 5000
curl http://localhost:5000/health

# If backend is not running, start it first:
cd ../
python run_project.py
```

4. Run development server:
```bash
npm run dev
```

5. Open http://localhost:3000

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

**IMPORTANT**: The FastAPI backend server must be running on the configured API URL (default: `http://localhost:5000`) before starting the frontend.

The frontend connects to the Python backend API:

### Endpoints Used
- `POST /api/semantic-search` - AI-powered semantic text search
- `POST /api/visual/search_by_image` - Visual search by image upload
- `GET /api/products/:id` - Get product details
- `GET /api/trending` - Get trending products
- `GET /api/categories` - Get product categories

### API Configuration
Located in `src/lib/api.ts`:
- Base URL from environment variables (`NEXT_PUBLIC_API_URL`)
- Request/response interceptors with logging
- Comprehensive error handling (400, 401, 403, 404, 429, 500, 503)
- CSRF token support (prepared for future use)
- 15-second timeout configuration
- Development mode debugging

### Health Check
```bash
# Verify backend is accessible
curl http://localhost:5000/health

# Expected response: {"status": "healthy"}
```

## 🔧 Environment Variables

The application uses environment variables for configuration. All variables are validated at build time to catch configuration errors early.

### Required Variables

#### `NEXT_PUBLIC_API_URL`
- **Type**: String (URL)
- **Required**: Yes
- **Default**: `http://localhost:5000`
- **Description**: Backend API base URL. Must be a valid HTTP/HTTPS URL.
- **Examples**:
  - Development: `http://localhost:5000`
  - Staging: `https://staging-api.yourdomain.com`
  - Production: `https://api.yourdomain.com`

### Optional Variables

#### `NEXT_PUBLIC_APP_NAME`
- **Type**: String
- **Required**: No
- **Default**: `HypeLens AI`
- **Description**: Application name displayed in UI and page titles

#### `NEXT_PUBLIC_APP_VERSION`
- **Type**: String
- **Required**: No
- **Default**: `1.0.0`
- **Description**: Application version displayed in footer

#### `NEXT_PUBLIC_ENABLE_ANALYTICS`
- **Type**: String (`"true"` or `"false"`)
- **Required**: No
- **Default**: `false`
- **Description**: Enable/disable analytics tracking

#### `NEXT_PUBLIC_MAX_IMAGE_SIZE`
- **Type**: String (number as string)
- **Required**: No
- **Default**: `10485760` (10 MB)
- **Description**: Maximum image upload size in bytes
- **Examples**:
  - 5 MB: `5242880`
  - 10 MB: `10485760`
  - 20 MB: `20971520`

#### `NEXT_PUBLIC_DEFAULT_SEARCH_LIMIT`
- **Type**: String (number as string)
- **Required**: No
- **Default**: `20`
- **Description**: Default number of search results per page

### Setup Instructions

1. **Copy the example file**:
   ```bash
   cp .env.local.example .env.local
   ```

2. **Edit `.env.local`** with your values:
   ```bash
   NEXT_PUBLIC_API_URL=http://localhost:5000
   # Add other optional variables as needed
   ```

3. **Validation**: Environment variables are automatically validated when you run `npm run dev` or `npm run build`. Missing required variables will display helpful error messages.

### Security Notes

- ⚠️ **Never commit `.env.local`** to version control (it's in `.gitignore`)
- ✅ **Do commit `.env.local.example`** as a template for other developers
- 🔒 Only use `NEXT_PUBLIC_` prefix for non-sensitive configuration
- 🔑 Variables with `NEXT_PUBLIC_` prefix are exposed to the browser
- 🔄 Rotate credentials regularly and update `.env.local` accordingly
- 📝 Use different values for development, staging, and production

### Troubleshooting

**Problem**: `Missing required environment variable: NEXT_PUBLIC_API_URL`

**Solution**: 
1. Ensure `.env.local` exists in the `frontend-nextjs/` directory
2. Verify `NEXT_PUBLIC_API_URL` is set in `.env.local`
3. Restart the development server after changing environment variables

**Problem**: `Invalid NEXT_PUBLIC_API_URL format`

**Solution**:
- URL must include protocol: `http://` or `https://`
- ❌ Invalid: `localhost:5000`, `/api`
- ✅ Valid: `http://localhost:5000`, `https://api.yourdomain.com`

**Problem**: Backend connection errors (CORS, network errors)

**Solution**:
1. Verify backend is running: `curl http://localhost:5000/health`
2. Check backend CORS configuration allows `http://localhost:3000`
3. Ensure `NEXT_PUBLIC_API_URL` matches the backend server address
4. Check firewall/network settings if using custom ports

## 🔒 Security

The application implements comprehensive security measures to protect against common web vulnerabilities.

### Security Headers

Security headers are automatically configured in `next.config.ts` and applied to all routes:

- **Content Security Policy (CSP)**: Restricts resource loading to prevent Cross-Site Scripting (XSS) attacks. Controls which scripts, styles, images, and connections are allowed.
- **X-Frame-Options**: Set to `DENY` to prevent clickjacking attacks by blocking iframe embedding of the application.
- **X-Content-Type-Options**: Set to `nosniff` to prevent MIME-type sniffing attacks, forcing browsers to respect the declared Content-Type.
- **Referrer-Policy**: Set to `strict-origin-when-cross-origin` to control referrer information leakage—sends full URL for same-origin requests, only origin for cross-origin HTTPS requests.
- **Permissions-Policy**: Restricts access to browser features (camera, microphone, geolocation, payment APIs, etc.) following the principle of least privilege.
- **X-DNS-Prefetch-Control**: Enabled to allow DNS prefetching for external domains, improving performance for product images from e-commerce sites.
- **Strict-Transport-Security (HSTS)**: Forces HTTPS connections in production with a max-age of 1 year, applying to all subdomains. Automatically enabled only in production builds (not in development since localhost uses HTTP).

### CORS Configuration

**IMPORTANT**: CORS (Cross-Origin Resource Sharing) is handled by the backend FastAPI server in `app.py` (lines 154-160). CORS is a backend security mechanism and should **NOT** be configured in the frontend.

The backend is configured to accept requests from:
- `http://localhost:3000` (Next.js development server)
- `http://127.0.0.1:3000` (alternative localhost address)

**If you encounter CORS errors:**

1. Verify the backend is running on port 5000:
   ```bash
   curl http://localhost:5000/health
   ```

2. Check that `NEXT_PUBLIC_API_URL` in `.env.local` matches the backend's allowed origins

3. Ensure the backend's CORS middleware in `app.py` includes your frontend URL

4. Restart both frontend and backend servers after configuration changes

**Do NOT attempt to configure CORS headers in the frontend** - this is architecturally incorrect and will not solve CORS issues.

### Testing Security Headers

To verify security headers are properly applied:

```bash
# Start the development server
npm run dev

# In another terminal, check response headers
curl -I http://localhost:3000
```

You should see headers like `X-Frame-Options`, `Content-Security-Policy`, `X-Content-Type-Options`, etc. in the response.

**Example output:**
```
HTTP/1.1 200 OK
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; ...
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
...
```

### Production Considerations

**Automatic Production Enhancements:**
- HSTS header is automatically enabled only in production builds
- CSP includes `upgrade-insecure-requests` directive in production to automatically upgrade HTTP requests to HTTPS

**Configuration for Production:**
- Set `NEXT_PUBLIC_PRODUCTION_DOMAIN` in `.env.local` to your production API URL for proper CSP configuration
- Review and tighten CSP directives based on your specific security requirements
- Consider using CSP nonces for inline scripts in production for enhanced security (requires code changes)
- Monitor CSP violation reports to identify and fix security issues

**Security Best Practices:**
- Always use HTTPS in production environments
- Regularly update dependencies to patch security vulnerabilities
- Review security headers periodically and adjust as needed
- Enable security scanning tools in your CI/CD pipeline
- Follow the principle of least privilege for all configurations

### CSP Violations and Debugging

If you encounter Content Security Policy violations in the browser console:

1. **Open browser DevTools**:
   - Press `F12` or right-click → Inspect
   - Go to the Console tab

2. **Look for CSP errors**:
   ```
   Refused to load the script 'https://example.com/script.js' because it violates
   the following Content Security Policy directive: "script-src 'self'"
   ```

3. **Common CSP issues and solutions**:

   **Problem**: External scripts are blocked
   - **Solution**: Add the domain to the appropriate CSP directive in `next.config.ts`
   - Example: For Google Analytics, add `https://www.googletagmanager.com` to `script-src`

   **Problem**: Inline styles are blocked in production
   - **Solution**: CSP already includes `'unsafe-inline'` for styles (required for Tailwind CSS)
   - If still blocked, verify the CSP directive hasn't been modified

   **Problem**: Images from e-commerce sites don't load
   - **Solution**: CSP already allows `https: http:` for images
   - Check browser console for specific errors

   **Problem**: API calls to backend are blocked
   - **Solution**: Verify `connect-src` includes your backend URL
   - Development: `http://localhost:5000` and `http://127.0.0.1:5000` are already included
   - Production: Add your production API domain

4. **Adjust CSP directives** in `next.config.ts` if needed:
   - Locate the `headers()` function
   - Modify the `cspDirectives` array
   - Add specific domains instead of using wildcards for better security

**Development vs Production CSP:**
- **Development**: Includes `'unsafe-eval'` for Next.js hot module replacement and React DevTools
- **Production**: Remove `'unsafe-eval'` and tighten directives for maximum security (requires testing)

### Security Resources

- [OWASP Secure Headers Project](https://owasp.org/www-project-secure-headers/)
- [MDN Content Security Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [Next.js Security Headers Documentation](https://nextjs.org/docs/advanced-features/security-headers)

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

## 🎨 Customization

### Theme Colors
Edit `tailwind.config.ts`:
```typescript
colors: {
  primary: { /* your colors */ },
  // ...
}
```

### Environment Configuration
Edit `.env.local` (see **Environment Variables** section for all options):
```bash
NEXT_PUBLIC_API_URL=http://localhost:5000
NEXT_PUBLIC_APP_NAME=Your App Name
NEXT_PUBLIC_APP_VERSION=2.0.0
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
