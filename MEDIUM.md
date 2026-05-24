# Publishing the README as a Medium article

A short checklist so the published version reads as polished as the
README does on GitHub.

## 1. Import, don't paste

Use Medium's URL import: open `medium.com/p/import` and paste

```
https://github.com/Prajwalabraham/make-any-coding-assistant-self-learning/blob/main/README.md
```

Medium fetches the rendered version. Pasting raw markdown works too
but you'll lose more formatting.

## 2. Fix the four things Medium mangles

After import, eyeball these:

1. **The TL;DR blockquote at the top contains a code block.** Medium
   renders blockquotes and code blocks separately and the nesting
   confuses it. Either lift the code block out of the blockquote, or
   convert the whole TL;DR into a single styled paragraph.
2. **The per-agent wiring table.** Medium renders tables but they look
   cramped on mobile. Acceptable workaround: take a screenshot of the
   table as rendered on GitHub and paste it as an image.
3. **Heading levels.** Medium honors H1/H2/H3 only. The `####` Pitfalls
   sub-sub-headings inside skill descriptions will become bold-only.
   Usually fine, but check that hierarchy still reads cleanly.
4. **Relative image paths.** `assets/cover.svg` won't resolve. Upload
   `assets/cover.png` as the cover image directly in Medium's UI.

## 3. Attach the repo

Medium has a native GitHub embed. Drop a blank line, paste the URL,
press Enter:

```
https://github.com/Prajwalabraham/make-any-coding-assistant-self-learning
```

It auto-renders a card with the repo name, description, and star
count. Three good spots:

- Right after the TL;DR (skimmers grab it in five seconds)
- Inside the **Install** section, just below the curl one-liner
- As a final CTA at the bottom, above the "want to contribute" line

## 4. Cover image

`assets/cover.png` is 1500×750, Medium's preferred aspect ratio. Upload
it as the cover in the story settings panel. The SVG source is in
`assets/cover.svg` if you want to tweak (open in any editor or import
to Figma).

## 5. Tags

Suggested Medium tags (you can pick five):

- AI
- Coding
- Developer Tools
- Claude
- Productivity

## 6. Subtitle

Medium shows a subtitle under the title. Suggested:

> Take the architecture of Hermes and OpenClaw and port it into Claude
> Code, Cursor, Codex, or Aider — without leaving the agent you
> already use.

## 7. Read time and word count

The article is about 7 minutes (Medium will calculate this
automatically). If you want to trim, the easiest cut is the per-agent
table in the three-layer section; the article still reads cleanly
without it.
