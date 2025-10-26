# Project Documentation

## Overview

This project is a **dynamic, client‑side web application** that provides a rich user interface for managing a list of items (e.g., tasks, notes, or products).  It supports creating, editing, deleting, filtering, drag‑and‑drop reordering, and theme switching (light/dark).  All functionality runs in the browser – there is no server‑side component other than a simple static file server.

## Features

- **Add items** – input new entries via a form.
- **Edit items** – inline editing with instant preview.
- **Delete items** – remove entries with a single click.
- **Filter items** – search or filter by status/categories.
- **Drag‑and‑drop** – reorder items using the native HTML5 Drag‑and‑Drop API.
- **Theme switching** – toggle between light and dark themes; preference is persisted in `localStorage`.
- **Responsive UI** – works on desktop and mobile browsers.
- **Pure JavaScript** – no external frameworks; only vanilla JS, HTML5, and CSS3.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Markup | HTML5 |
| Styling | CSS3 (Flexbox/Grid, CSS Variables for theming) |
| Logic | Vanilla JavaScript (ES6 modules) |
| Build/Serve | Any static file server (e.g., `http-server`, `live-server`, Python's `http.server`) |
| Version Control | Git |

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your‑username/your‑repo.git
   cd your‑repo
   ```

2. **Install a static file server** (optional, you can use any server you prefer). Example with `npm`:
   ```bash
   npm install -g http-server   # or live-server, serve, etc.
   ```

3. **Serve `index.html`**
   ```bash
   # Using http-server (default port 8080)
   http-server .
   # Or with Python 3
   python -m http.server 8000
   ```
   Open your browser and navigate to `http://localhost:8080` (or the port you chose).

## Usage

### Adding an Item
```html
<form id="addForm">
  <input type="text" id="newItem" placeholder="Enter item" required />
  <button type="submit">Add</button>
</form>
```
The JavaScript module `src/add.js` listens for the form submit, creates a new DOM element, and appends it to the list.

### Editing an Item
```html
<li class="item" draggable="true">
  <span class="text">Sample Item</span>
  <button class="edit">✎</button>
</li>
```
Click the **edit** button – the script replaces the `<span>` with an `<input>` pre‑filled with the current text. Press **Enter** or click **Save** to commit changes.

### Deleting an Item
```html
<button class="delete">✖</button>
```
The delete button removes the parent `<li>` from the DOM and updates `localStorage`.

### Filtering Items
```html
<input type="text" id="filter" placeholder="Search..." />
```
The filter input triggers a `keyup` event; the script hides items that do not contain the entered substring.

### Drag‑and‑Drop Reordering
Each list item has `draggable="true"`. The drag‑and‑drop module handles `dragstart`, `dragover`, and `drop` events, swapping the positions of the involved `<li>` elements and persisting the new order.

### Theme Switching
```html
<button id="themeToggle">Toggle Theme</button>
```
The theme script toggles a `data-theme="dark"` attribute on `<html>` and stores the preference in `localStorage`. CSS variables define the colour palette for light and dark modes.

## Development

### File Structure
```
project-root/
│
├─ index.html            # Entry point – loads CSS & JS modules
├─ style.css             # Global styles + CSS variables for themes
├─ script.js             # Main entry script that imports modules
├─ src/                  # JavaScript modules (ES6)
│   ├─ add.js
│   ├─ edit.js
│   ├─ delete.js
│   ├─ filter.js
│   ├─ dnd.js            # drag‑and‑drop logic
│   └─ theme.js
└─ README.md             # ← you are reading it!
```

### Code Organization
- **`index.html`** – minimal markup; only includes `<link>` for CSS and a `<script type="module" src="script.js"></script>`.
- **`style.css`** – defines layout, component styling, and two theme palettes using CSS custom properties (`--bg-color`, `--text-color`, …).
- **`script.js`** – imports all feature modules and initializes them in a predictable order.
- **`src/*.js`** – each file encapsulates a single responsibility (single‑responsibility principle). They expose an `init()` function that is called from `script.js`.

### Example: Linking CSS & JS in `index.html`
```html
<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Dynamic List App</title>
  <!-- Global stylesheet -->
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <!-- UI markup goes here -->
  <script type="module" src="script.js"></script>
</body>
</html>
```
The `type="module"` attribute enables ES6 module imports inside `script.js`.

## Contribution Guidelines

1. **Fork the repository** and clone your fork.
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** – keep the code style consistent (use 2‑space indentation, semicolons optional, descriptive variable names).
4. **Run the app locally** to verify that nothing is broken.
5. **Write/Update documentation** if you add new features.
6. **Commit** with a clear message:
   ```bash
   git commit -m "feat: add drag‑and‑drop reordering"
   ```
7. **Push** and open a Pull Request against the `main` branch.
8. **Review** – ensure the PR passes any CI checks (if configured) and that the README reflects the new functionality.

### Coding Standards
- Use **ES6+** syntax (let/const, arrow functions, template literals).
- Keep each module focused on a single feature.
- Prefer **named exports** for testability.
- Write **inline comments** for non‑obvious logic.
- Ensure the UI remains accessible (ARIA attributes where appropriate).

---

*Happy coding! 🎉*