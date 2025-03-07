# google-advocacy-demo

This repo houses reusable Vue.js components and styles for the Google Advocacy demos

## Project Setup

Make sure you have NVM or a compatible version of Node.js installed.

```sh
nvm use
```

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```

## App Routes
  - `http://localhost:3000/!#/`: Big Tv 65"
  - `http://localhost:3000/!#/tv`: Tv 55"
  - `http://localhost:3000/!#/chromebook`: Chromebook
  - `http://localhost:3000/!#/phone`: Phone

## queryParams
  - `?manual` to control of the navigation by clicking to go next
  - `?view` to start from a specific route
  - `?rank` to simulate the celebratory moment on tv screen