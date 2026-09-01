# Jefferson Web

Next.js frontend for Jefferson, deployed at [jefferson-one.vercel.app](https://jefferson-one.vercel.app).

## Stack

- **Next.js 15** (App Router) + **React 19** + **TypeScript**
- **Tailwind CSS 4** + Radix UI primitives + lucide-react icons
- Deployed on **Vercel**

## Routes

| Route | What it is |
|-------|-----------|
| `/` | Landing page |
| `/about` | About the project |
| `/demo` | Video walkthrough player (`public/videos/demo.mp4`) |

## Develop

```bash
npm install
npm run dev   # http://localhost:3000
```

The simulation engine, CLI, and API this frontend talks to live in [`/backend`](../backend). The explainer videos in [`/media`](../media) are rendered with Remotion; see [`/media/remotion`](../media/remotion) to re-render them.
