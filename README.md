# UV Magazine Full-Stack Website

A full-stack English website for a literary and multimedia magazine. It covers the functional requirements from the provided PDF:

- Home page with About / Gallery / Submit navigation
- Featured Issues section
- Footer social links
- About page
- Gallery page with LOOK / READ / LISTEN / WATCH category entry cards
- LOOK page for artwork and photography in a grid
- READ page for short stories and poems as cards, plus detail pages
- LISTEN page with audio players
- WATCH page with video embeds
- Logo/home navigation and submit CTA
- Submission form backed by MongoDB
- Admin area for managing content, issues, about text, links, and submissions

The original PDF specifies these core functions and page groupings. fileciteturn3file0 fileciteturn3file1turn3file2

## Stack

- Node.js
- Express
- EJS
- MongoDB + Mongoose
- express-session
- Basic CSS and vanilla JavaScript

## Quick start

1. Copy `.env.example` to `.env`
2. Set `MONGODB_URI`, `SESSION_SECRET`, `ADMIN_EMAIL`, and `ADMIN_PASSWORD`
3. Install dependencies
   ```bash
   npm install
   ```
4. Seed the database
   ```bash
   npm run seed
   ```
5. Start the server
   ```bash
   npm run dev
   ```
6. Open `http://localhost:3000`

## Admin login

Go to `/admin/login`

The first run creates an admin user using:

- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`

## Content model summary

- `ContentItem`
  - categories: `look`, `read`, `listen`, `watch`
  - subtypes for finer classification such as artwork, photography, poem, short-story, music, spoken-word, short-film, video
- `Issue`
- `SocialLink`
- `Submission`
- `PageSetting`
- `User`

## Submission behavior

The PDF references a submit button that can jump to a Google Form. This implementation supports both:

- internal site submission page at `/submit`
- optional external submission URL in admin settings

If `submissionMode` is set to `external`, the submit button redirects to the external form URL.

## Media notes

To keep the app stable and simple:

- images are stored as URLs
- audio is stored as hosted file URLs
- video is stored as embed URLs (YouTube/Vimeo) or direct video URLs

## Suggested production hardening

Before production, add:

- CSRF protection
- rate limiting
- stricter content sanitization
- secure cookies and HTTPS
- file upload service if needed
- richer admin roles if a team will manage the site


## Official URLs configured in this build

- Submit (Google Form): https://docs.google.com/forms/d/e/1FAIpQLSfY1mKenxXltfFdG36W9Bb_Y3LJz9I9j_zj71UfWm_z2YLKTQ/viewform
- Featured issues archive: https://issuu.com/ultravioletmagazine
- Legacy Wix admin sign-in: https://users.wix.com/signin?originUrl=https%3A%2F%2Fmanage.wix.com%2Fmy-account%2Fsites&postLogin=https%3A%2F%2Fmanage.wix.com%2Fmy-account%2Fsites&overrideLocale=zh&forceRender=true
- Legacy public site: https://uvmagqueens.wixsite.com/uvmagazine

Public submit buttons now open the Google Form. The internal test submission form remains available at `/submit/local` for admin workflow testing.
