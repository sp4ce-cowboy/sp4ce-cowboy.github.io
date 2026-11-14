# rubesh.dev

Source of [rubesh.dev](https://rubesh.dev): one static page, plain HTML and CSS, served by GitHub Pages.

`index.html` is built by `build.py` from the [GitHub profile README](https://github.com/sp4ce-cowboy/sp4ce-cowboy):
the bio (its whoami block), the tech stack (`.github/techstack.txt`) and the projects (`.github/projects.txt`,
newest first). After changing any of those, run `python3 build.py`, check `index.html`, then commit and push.
Design changes go in the page template inside `build.py`, so a rebuild keeps them.
