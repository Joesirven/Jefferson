# Jefferson explainer videos (Remotion)

The videos in [`../videos`](../videos) are rendered programmatically with [Remotion](https://remotion.dev) - React components instead of a timeline editor. Edit the components, re-render, commit.

## Compositions

| ID | Output | What it shows |
|----|--------|---------------|
| `Architecture` | `../videos/architecture.mp4` | System architecture: data sources -> persona generation -> Supabase -> simulation engine -> aggregation -> CLI / API / web |
| `Simulation` | `../videos/simulation.mp4` | How one poll runs: question -> persona prompts -> batched LLM calls -> aggregation -> Supabase |

Both are 1280x720, 30fps, 15 seconds.

## Re-render

```bash
npm install
npx remotion browser ensure   # one-time: downloads headless Chrome
npx remotion render src/index.ts Architecture ../videos/architecture.mp4
npx remotion render src/index.ts Simulation ../videos/simulation.mp4
```

Preview while editing:

```bash
npx remotion studio src/index.ts
```

## Editing notes

- `src/theme.tsx` holds the shared palette, fonts, and primitives (`NodeBox`, `Arrow`, `Title`). Match the GitHub-dark look when adding scenes.
- Keep videos short and text large; they render inline in the READMEs.
- No external assets: everything is divs + SVG, so renders are deterministic and fast.
